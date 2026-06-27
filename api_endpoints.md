# Backend API Specifications: Spotify Growth Discovery Engine

This document defines the REST API endpoints, request/response payload specifications, and route details.

---

### 1. Upload or Start Ingestion Workflow
*   **Method:** `POST`
*   **Route:** `/api/v1/workflows/trigger`
*   **Purpose:** Start a data extraction job from APIs or accept a custom review CSV/JSON upload, and kick off the AI classification pipeline.
*   **Request Body:** (JSON or Multipart Form-Data if file uploaded)
    ```json
    {
      "sources": ["reddit", "app_store", "play_store"],
      "start_date": "2026-06-18T00:00:00Z",
      "end_date": "2026-06-25T23:59:59Z"
    }
    ```
*   **Response Body (Success 202 Accepted):**
    ```json
    {
      "workflow_run_id": "bb22cc44-dd66-44ee-99aa-887766554433",
      "status": "running",
      "started_at": "2026-06-25T23:54:05.000Z",
      "message": "AI analysis pipeline scheduled successfully."
    }
    ```

---

### 2. Fetch Workflow Run Status
*   **Method:** `GET`
*   **Route:** `/api/v1/workflows/status/:id`
*   **Purpose:** Query the processing progress, item throughput, and failure status of an active pipeline job.
*   **Request Body:** None (Requires workflow ID in URL path).
*   **Response Body (Success 200 OK):**
    ```json
    {
      "workflow_run_id": "bb22cc44-dd66-44ee-99aa-887766554433",
      "status": "completed",
      "progress": {
        "total_records": 150,
        "processed_records": 150,
        "percentage": 100.0
      },
      "started_at": "2026-06-25T23:54:05.000Z",
      "completed_at": "2026-06-25T23:54:20.000Z",
      "errors": null
    }
    ```

---

### 3. Fetch Classified Reviews
*   **Method:** `GET`
*   **Route:** `/api/v1/reviews`
*   **Purpose:** Supply paginated, filterable, and searchable classified reviews for the frontend audit tables.
*   **Request Body:** None (Filtered via Query Parameters: `search`, `theme`, `subtheme`, `sentiment_min`, `sentiment_max`, `segment`, `page`, `limit`).
*   **Response Body (Success 200 OK):**
    ```json
    {
      "total_records": 128,
      "page": 1,
      "limit": 10,
      "data": [
        {
          "id": "ff88aa22-bb11-44ee-aa22-001122334455",
          "raw_text": "I hate Spotify's search page. It's so cluttered with podcasts!",
          "cleaned_text": "I hate Spotify's search page. It's so cluttered with podcasts!",
          "detected_language": "en",
          "primary_label": "discovery frustration",
          "sublabels": ["ui-clutter", "search-friction"],
          "sentiment_score": -0.75,
          "inferred_segment": "Premium/iOS",
          "confidence": 0.94,
          "classified_at": "2026-06-25T23:54:15.980Z"
        }
      ]
    }
    ```

---

### 4. Fetch Summary Insights
*   **Method:** `GET`
*   **Route:** `/api/v1/insights/summary`
*   **Purpose:** Fetch the compiled narrative aggregates and action items for display in the main PM dashboard metrics.
*   **Request Body:** None (Filtered via Query Parameters: `start_date`, `end_date`, `source_channel`).
*   **Response Body (Success 200 OK):**
    ```json
    {
      "id": "dd55ee11-22aa-33bb-44cc-55ddeeff0011",
      "time_period_start": "2026-06-18T00:00:00.000Z",
      "time_period_end": "2026-06-25T23:59:59.999Z",
      "avg_sentiment": -0.15,
      "top_themes": [
        {"theme": "discovery frustration", "count": 248},
        {"theme": "missing control", "count": 120}
      ],
      "summary_text": "Users are reporting a high volume of frustration with the Home tab podcast recommendation clutter...",
      "action_items": [
        "Inject a novelty-bias coefficient into the recommendation builder to enforce a minimum of 40% unplayed tracks in shuffle sequences.",
        "Introduce a simple toggle to allow users to exclude specific playlists from affecting their personalized taste profile."
      ],
      "created_at": "2026-06-25T23:55:00.000Z"
    }
    ```

---

### 5. Download Reports
*   **Method:** `GET`
*   **Route:** `/api/v1/insights/export`
*   **Purpose:** Generate and download a physical summary document file (PDF, Markdown, or JSON dump).
*   **Request Body:** None (Filtered via Query Parameters: `start_date`, `end_date`, `format` (e.g., `'pdf'`, `'markdown'`, `'json'`).
*   **Response Body (Success 200 OK):**
    *   *If format = 'json':* Returns the raw insight JSON block.
    *   *If format = 'pdf' or 'markdown':* Returns the compiled document file stream (content-type: `application/pdf` or `text/markdown`).

---

### 6. Save User Interview Notes
*   **Method:** `POST`
*   **Route:** `/api/v1/interviews`
*   **Purpose:** Save qualitative transcripts and insights from user interviews and link them to quantitative review records.
*   **Request Body (JSON):**
    ```json
    {
      "user_id": "spotify_user_9214",
      "interview_date": "2026-06-25T14:00:00.000Z",
      "transcript": "Q: Why did you rate search screen 2 stars? A: Too much junk on the home screen...",
      "summary_notes": "- User feels overwhelmed by podcast recommendations.\n- Expresses need to block artists.",
      "linked_reviews": ["8f2a1b9e-4c7b-402a-9e12-3f8b654012ab"]
    }
    ```
*   **Response Body (Success 201 Created):**
    ```json
    {
      "interview_id": "aa99ee11-22ff-33bb-44dd-55ccaa668899",
      "status": "success",
      "message": "User research interview saved and linked successfully."
    }
    ```
