import os
import json
import uuid
import threading
from datetime import datetime, timedelta
import sqlite3
from flask import Flask, request, jsonify, send_file
from io import BytesIO

# Import database helper and orchestrator from workflow pipeline
from workflow_pipeline import get_db_connection, execute_query, trigger_workflow_pipeline, init_db

# Initialize Flask App
app = Flask(__name__)

# Basic CORS configuration
try:
    from flask_cors import CORS
    CORS(app)
except ImportError:
    pass

# Helper to verify database features (like User Interviews table)
def init_server_db():
    """Ensures server-specific tables like user_interviews are initialized in the database."""
    conn = get_db_connection()
    is_sqlite = isinstance(conn, sqlite3.Connection)
    cursor = conn.cursor()
    
    if is_sqlite:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_interviews (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            interview_date TEXT NOT NULL,
            transcript TEXT NOT NULL,
            summary_notes TEXT,
            linked_reviews TEXT, -- JSON array string
            created_at TEXT NOT NULL
        )""")
    else:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_interviews (
            id UUID PRIMARY KEY,
            user_id VARCHAR(100) NOT NULL,
            interview_date TIMESTAMP NOT NULL,
            transcript TEXT NOT NULL,
            summary_notes TEXT,
            linked_reviews UUID[],
            created_at TIMESTAMP NOT NULL
        )""")
    
    conn.commit()
    conn.close()
    print("[Server DB] Server tables verified.")

# ==========================================
# Frontend Route
# ==========================================

@app.route("/")
def serve_frontend():
    """Serves the static index.html dashboard file."""
    return send_file("index.html")

# ==========================================
# API Endpoints
# ==========================================

@app.route("/api/v1/workflows/trigger", methods=["POST"])
def trigger_workflow():
    """
    POST /api/v1/workflows/trigger
    Trigger a background processing run, optionally accepting a JSON list of reviews to ingest.
    """
    data = request.get_json() or {}
    mock_reviews = data.get("reviews", None)
    sources = data.get("sources", None)
    
    # Generate run ID immediately
    run_id = str(uuid.uuid4())
    started_at = datetime.utcnow().isoformat()
    
    conn = get_db_connection()
    execute_query(conn, """
        INSERT INTO workflow_runs (id, started_at, status, processed_count)
        VALUES (%s, %s, %s, %s)
    """, (run_id, started_at, "running", 0))
    conn.commit()
    conn.close()
    
    # Run the ingestion + analysis workflow inside a background thread so the client returns instantly (202 Accepted)
    def bg_task(workflow_run_id, mock_data, source_list):
        from workflow_pipeline import run_cleaning_pipeline, run_classification_pipeline, run_summarization_pipeline, ingest_raw_reviews, collect_organic_reviews
        try:
            if mock_data:
                ingest_raw_reviews(mock_data)
            else:
                if not source_list:
                    source_list = ['app_store', 'reddit', 'social_media']
                real_reviews = collect_organic_reviews(source_list)
                ingest_raw_reviews(real_reviews)
                
            run_cleaning_pipeline()
            classified = run_classification_pipeline(workflow_run_id=workflow_run_id)
            
            # Commit success run
            completed_at = datetime.utcnow().isoformat()
            db_conn = get_db_connection()
            execute_query(db_conn, """
                UPDATE workflow_runs 
                SET completed_at = %s, status = %s, processed_count = %s
                WHERE id = %s
            """, (completed_at, "completed", classified, workflow_run_id))
            db_conn.commit()
            db_conn.close()
            
            # Compile 2019-Current Day summary report
            start_date = "2019-01-01T00:00:00Z"
            end_dt = datetime.utcnow()
            end_date = end_dt.strftime("%Y-%m-%dT23:59:59Z")
            run_summarization_pipeline(start_date, end_date)
            
        except Exception as e:
            completed_at = datetime.utcnow().isoformat()
            db_conn = get_db_connection()
            execute_query(db_conn, """
                UPDATE workflow_runs 
                SET completed_at = %s, status = %s, error_message = %s
                WHERE id = %s
            """, (completed_at, "failed", str(e), workflow_run_id))
            db_conn.commit()
            db_conn.close()
            
    thread = threading.Thread(target=bg_task, args=(run_id, mock_reviews, sources))
    thread.start()
    
    return jsonify({
        "workflow_run_id": run_id,
        "status": "running",
        "started_at": started_at,
        "message": "AI analysis pipeline scheduled successfully in background."
    }), 202


@app.route("/api/v1/workflows/status/<uuid_id>", methods=["GET"])
def get_workflow_status(uuid_id):
    """
    GET /api/v1/workflows/status/:id
    Query the status and progress counter of a specific run.
    """
    conn = get_db_connection()
    is_sqlite = isinstance(conn, sqlite3.Connection)
    
    cursor = execute_query(conn, """
        SELECT id, started_at, completed_at, status, processed_count, error_message 
        FROM workflow_runs WHERE id = %s
    """, (uuid_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Workflow run not found"}), 404
        
    res = dict(row) if is_sqlite else {
        "id": row[0],
        "started_at": row[1],
        "completed_at": row[2],
        "status": row[3],
        "processed_count": row[4],
        "error_message": row[5]
    }
    
    # Map progress
    progress_pct = 100 if res["status"] == "completed" else (0 if res["status"] == "failed" else 50)
    
    return jsonify({
        "workflow_run_id": res["id"],
        "status": res["status"],
        "progress": {
            "total_records": res["processed_count"],
            "processed_records": res["processed_count"],
            "percentage": progress_pct
        },
        "started_at": res["started_at"],
        "completed_at": res["completed_at"],
        "errors": res["error_message"]
    }), 200


@app.route("/api/v1/reviews", methods=["GET"])
def get_reviews():
    """
    GET /api/v1/reviews
    Fetch paginated list of classified reviews with filter overrides.
    """
    theme = request.args.get("theme")
    subtheme = request.args.get("subtheme")
    segment = request.args.get("segment")
    search = request.args.get("search")
    
    page = int(request.args.get("page", 1))
    limit_val = request.args.get("limit")
    if limit_val == "all":
        limit = None
        offset = 0
    else:
        try:
            limit = int(limit_val) if limit_val else 20
            offset = (page - 1) * limit
        except ValueError:
            limit = 20
            offset = (page - 1) * limit
            
    conn = get_db_connection()
    is_sqlite = isinstance(conn, sqlite3.Connection)
    
    # 1. Calculate database-wide stats for metadata
    cursor_collected = execute_query(conn, "SELECT count(*) FROM raw_reviews")
    total_collected = cursor_collected.fetchone()[0]
    
    cursor_sources = execute_query(conn, "SELECT source, count(*) FROM raw_reviews GROUP BY source")
    source_counts = {}
    for r in cursor_sources.fetchall():
        s_name = r[0] if not is_sqlite else r["source"]
        s_count = r[1] if not is_sqlite else list(r)[1]
        source_counts[s_name] = s_count
        
    cursor_dates = execute_query(conn, "SELECT MIN(retrieved_at), MAX(retrieved_at) FROM raw_reviews")
    dates_row = cursor_dates.fetchone()
    min_date = dates_row[0] if dates_row else None
    max_date = dates_row[1] if dates_row else None
    
    # Base query construction
    query_parts = [
        "SELECT c.id, r.raw_text, cl.cleaned_text, cl.detected_language, c.primary_label, c.sublabels, c.sentiment_score, c.inferred_segment, c.confidence, c.classified_at, r.source, r.retrieved_at",
        "FROM classified_reviews c",
        "JOIN cleaned_reviews cl ON c.cleaned_review_id = cl.id",
        "JOIN raw_reviews r ON cl.raw_review_id = r.id",
        "WHERE 1=1"
    ]
    params = []
    
    if theme:
        query_parts.append("AND c.primary_label = %s")
        params.append(theme)
    if segment:
        query_parts.append("AND c.inferred_segment = %s")
        params.append(segment)
    if search:
        query_parts.append("AND (cl.cleaned_text LIKE %s OR r.raw_text LIKE %s)")
        search_val = f"%{search}%"
        params.append(search_val)
        params.append(search_val)
        
    # Query total records matching
    count_query = "SELECT count(*) " + " ".join(query_parts[1:])
    cursor = execute_query(conn, count_query, tuple(params))
    total_records = cursor.fetchone()[0]
    
    # Sort and paginate
    if limit is not None:
        query_parts.append("ORDER BY c.classified_at DESC LIMIT %s OFFSET %s")
        params.extend([limit, offset])
    else:
        query_parts.append("ORDER BY c.classified_at DESC")
    
    full_query = "\n".join(query_parts)
    cursor = execute_query(conn, full_query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    
    insight_map = {
        "discovery frustration": "User finds the user interface (search, home screen) too cluttered, especially with podcasts, hindering music discovery.",
        "repetitive listening": "User is experiencing high repetition and loops when playing playlists or using smart shuffle.",
        "recommendation mismatch": "Autoplay or algorithmic recommendations are mismatching the user's current mood or genre preference.",
        "playlist dependence": "User relies heavily on custom curated playlists rather than trusting algorithmic channels.",
        "intent to explore": "User expresses active intent to explore new tracks, niche genres, or artists.",
        "missing control": "User wants more control, such as blocking artists or excluding genres from personalization.",
        "unmet need": "User mentions a gap or missing discovery feature in the application."
    }
    
    data_list = []
    for row in rows:
        if is_sqlite:
            # Parse json array string for sqlite
            subtheme_arr = []
            try:
                if row["sublabels"]:
                    subtheme_arr = json.loads(row["sublabels"])
            except:
                pass
                
            theme_val = row["primary_label"]
            sentiment_val = row["sentiment_score"]
            segment_val = row["inferred_segment"]
            confidence_val = row["confidence"]
            retrieved_at_val = row["retrieved_at"]
            classified_at_val = row["classified_at"]
            source_val = row["source"]
            raw_text_val = row["raw_text"]
            cleaned_text_val = row["cleaned_text"]
            
            insight_val = insight_map.get(theme_val, "User provided feedback regarding general application usage.")
            
            data_list.append({
                "id": row["id"],
                "raw_text": raw_text_val,
                "cleaned_text": cleaned_text_val,
                "detected_language": row["detected_language"],
                "primary_label": theme_val,
                "sublabels": subtheme_arr,
                "sentiment_score": sentiment_val,
                "inferred_segment": segment_val,
                "confidence": confidence_val,
                "classified_at": classified_at_val,
                "source": source_val,
                "retrieved_at": retrieved_at_val,
                
                # Requested output keys
                "platform": source_val,
                "date": retrieved_at_val or classified_at_val,
                "original_text": raw_text_val,
                "theme": theme_val,
                "subtheme": subtheme_arr,
                "sentiment": sentiment_val,
                "user_segment": segment_val,
                "insight": insight_val,
                "confidence_score": confidence_val
            })
        else:
            subtheme_arr = row[5]
            theme_val = row[4]
            sentiment_val = row[6]
            segment_val = row[7]
            confidence_val = row[8]
            classified_at_val = row[9]
            source_val = row[10]
            retrieved_at_val = row[11]
            raw_text_val = row[1]
            cleaned_text_val = row[2]
            
            insight_val = insight_map.get(theme_val, "User provided feedback regarding general application usage.")
            
            data_list.append({
                "id": row[0],
                "raw_text": raw_text_val,
                "cleaned_text": cleaned_text_val,
                "detected_language": row[3],
                "primary_label": theme_val,
                "sublabels": subtheme_arr,
                "sentiment_score": sentiment_val,
                "inferred_segment": segment_val,
                "confidence": confidence_val,
                "classified_at": classified_at_val,
                "source": source_val,
                "retrieved_at": retrieved_at_val,
                
                # Requested output keys
                "platform": source_val,
                "date": retrieved_at_val or classified_at_val,
                "original_text": raw_text_val,
                "theme": theme_val,
                "subtheme": subtheme_arr,
                "sentiment": sentiment_val,
                "user_segment": segment_val,
                "insight": insight_val,
                "confidence_score": confidence_val
            })
            
    has_more = False
    next_page_token = None
    if limit is not None:
        has_more = (page * limit) < total_records
        next_page_token = page + 1 if has_more else None
            
    return jsonify({
        "total_records": total_records,
        "total_collected": total_collected,
        "total_valid": total_records,
        "total_unique_comments": total_records,
        "source_counts": source_counts,
        "date_range": {
            "start": min_date,
            "end": max_date
        },
        "page": page,
        "limit": limit,
        "has_more": has_more,
        "next_page_token": next_page_token,
        "data": data_list
    }), 200


@app.route("/api/v1/insights/summary", methods=["GET"])
def get_insights_summary():
    """
    GET /api/v1/insights/summary
    Retrieve the most recent AI generated aggregated metrics and report summary.
    """
    conn = get_db_connection()
    is_sqlite = isinstance(conn, sqlite3.Connection)
    
    cursor = execute_query(conn, """
        SELECT id, time_period_start, time_period_end, avg_sentiment, top_themes, summary_text, action_items, created_at
        FROM summary_insights ORDER BY created_at DESC LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "No aggregated summaries generated yet."}), 404
        
    if is_sqlite:
        themes = []
        actions = []
        try:
            if row["top_themes"]:
                themes = json.loads(row["top_themes"])
            if row["action_items"]:
                actions = json.loads(row["action_items"])
        except:
            pass
            
        res = {
            "id": row["id"],
            "time_period_start": row["time_period_start"],
            "time_period_end": row["time_period_end"],
            "avg_sentiment": row["avg_sentiment"],
            "top_themes": themes,
            "summary_text": row["summary_text"],
            "action_items": actions,
            "created_at": row["created_at"]
        }
    else:
        res = {
            "id": row[0],
            "time_period_start": row[1],
            "time_period_end": row[2],
            "avg_sentiment": row[3],
            "top_themes": row[4],
            "summary_text": row[5],
            "action_items": row[6],
            "created_at": row[7]
        }
        
    return jsonify(res), 200


@app.route("/api/v1/insights/export", methods=["GET"])
def export_insights_report():
    """
    GET /api/v1/insights/export
    Downloads the latest summary insight report in Markdown or JSON format.
    """
    export_format = request.args.get("format", "markdown").lower()
    
    conn = get_db_connection()
    is_sqlite = isinstance(conn, sqlite3.Connection)
    
    cursor = execute_query(conn, """
        SELECT id, time_period_start, time_period_end, avg_sentiment, top_themes, summary_text, action_items
        FROM summary_insights ORDER BY created_at DESC LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "No report data to export"}), 404
        
    # Unpack SQLite columns
    if is_sqlite:
        themes = json.loads(row["top_themes"]) if row["top_themes"] else []
        actions = json.loads(row["action_items"]) if row["action_items"] else []
        period_start = row["time_period_start"]
        period_end = row["time_period_end"]
        avg_sentiment = row["avg_sentiment"]
        summary_text = row["summary_text"]
    else:
        themes = row[4]
        actions = row[5]
        period_start = row[1]
        period_end = row[2]
        avg_sentiment = row[3]
        summary_text = row[4]
        
    if export_format == "json":
        json_bytes = BytesIO(json.dumps({
            "period": f"{period_start} to {period_end}",
            "avg_sentiment": avg_sentiment,
            "themes": themes,
            "summary": summary_text,
            "actions": actions
        }, indent=2).encode())
        return send_file(json_bytes, mimetype="application/json", as_attachment=True, download_name="spotify_insights.json")
        
    # Default: Markdown
    md_content = f"""# Spotify Growth Insight Report
**Period:** {period_start} to {period_end}
**Average Sentiment Score:** {avg_sentiment:.2f}

## Executive Summary
{summary_text}

## Top Frustration Labels
"""
    for t in themes:
        md_content += f"- **{t.get('theme', 'unknown')}:** {t.get('count', 0)} comments\n"
        
    md_content += "\n## Action Items & Recommendations\n"
    for action in actions:
        if isinstance(action, dict):
            md_content += f"- **[{action.get('area', 'Product')}]** {action.get('action', '')} (Priority: {action.get('priority', 'Medium')})\n"
        else:
            md_content += f"- {action}\n"
            
    md_bytes = BytesIO(md_content.encode())
    return send_file(md_bytes, mimetype="text/markdown", as_attachment=True, download_name="spotify_insights_report.md")


@app.route("/api/v1/interviews", methods=["POST"])
def save_interview():
    """
    POST /api/v1/interviews
    Save qualitative customer research interviews linked to quantitative feedback reviews.
    """
    data = request.get_json() or {}
    
    user_id = data.get("user_id")
    interview_date = data.get("interview_date", datetime.utcnow().isoformat())
    transcript = data.get("transcript")
    summary_notes = data.get("summary_notes", "")
    linked_reviews = data.get("linked_reviews", [])
    
    if not user_id or not transcript:
        return jsonify({"error": "user_id and transcript are required fields."}), 400
        
    interview_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    conn = get_db_connection()
    is_sqlite = isinstance(conn, sqlite3.Connection)
    
    linked_payload = json.dumps(linked_reviews) if is_sqlite else linked_reviews
    
    execute_query(conn, """
        INSERT INTO user_interviews (id, user_id, interview_date, transcript, summary_notes, linked_reviews, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (interview_id, user_id, interview_date, transcript, summary_notes, linked_payload, created_at))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "interview_id": interview_id,
        "status": "success",
        "message": "User research interview details saved and linked successfully."
    }), 201


# ==========================================
# Server Init & Startup
# ==========================================

if __name__ == "__main__":
    # Ensure database schemas are fully loaded
    init_db()
    init_server_db()
    
    # Run the local Flask server on Port 8080
    port = int(os.getenv("PORT", 8080))
    print(f"[Server] Running listening API on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
