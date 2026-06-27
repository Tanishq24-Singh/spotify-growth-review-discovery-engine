import urllib.request
import json
import datetime
import re
import sys

# Set User-Agent headers to prevent blocks
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

COUNTRIES = ['us', 'gb', 'ca', 'au']
APP_ID = "324684580"  # Spotify iOS App ID

# Discovery keywords for filtering
DISCOVERY_KEYWORDS = [
    "discovery", "recommend", "recommendation", "shuffle", "autoplay", "algorithm",
    "loop", "mix", "daily mix", "discover weekly", "smart shuffle", "playlist",
    "artist", "find music", "genre", "search", "cluttered", "clutter", "crap",
    "podcast", "play list", "variety", "repetition", "repetitive", "stale"
]

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def clean_text(text):
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove markdown links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Normalize whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_app_store_date(date_str):
    # E.g. "2026-06-25T20:00:00-07:00"
    try:
        # Strip timezone offset for simplicity
        clean = date_str.split('+')[0].split('-')
        # Reconstruct if it has negative timezone
        if len(clean) > 3:
            clean = clean[:3]
        clean_str = '-'.join(clean)
        if 'T' in clean_str:
            dt_part = clean_str.split('T')[0]
            tm_part = clean_str.split('T')[1]
            # Strip seconds/millis if needed
            tm_part = tm_part.split(':')[0] + ':' + tm_part.split(':')[1]
            clean_str = f"{dt_part}T{tm_part}"
            return datetime.datetime.strptime(clean_str, "%Y-%m-%dT%H:%M")
    except Exception:
        pass
    return datetime.datetime.utcnow()

def classify_comment(text):
    text_lower = text.lower()
    theme = None
    subtheme = []
    sentiment = 0.0
    user_segment = None
    insight = ""
    confidence = 0.90
    
    # 1. Repetitive listening
    if any(k in text_lower for k in ["smart shuffle", "loop", "repetition", "repetitive", "stale", "same song", "same track"]):
        theme = "repetitive listening"
        subtheme = ["looping-recommendations"]
        sentiment = -0.5 if "hate" in text_lower or "annoying" in text_lower or "terrible" in text_lower else -0.3
        user_segment = "Mobile User"
        insight = "User is experiencing high repetition and loops when playing playlists or using smart shuffle."
    # 2. Recommendation mismatch
    elif any(k in text_lower for k in ["autoplay", "mismatch", "genre", "weird recommend", "wrong song"]):
        theme = "recommendation mismatch"
        subtheme = ["wrong-genre-autoplay"]
        sentiment = -0.4
        user_segment = "Mobile User"
        insight = "Autoplay or algorithmic recommendations are mismatching the user's current mood or genre preference."
    # 3. Discovery frustration
    elif any(k in text_lower for k in ["search", "cluttered", "clutter", "confusing", "podcast", "home screen"]):
        theme = "discovery frustration"
        subtheme = ["ui-clutter"]
        sentiment = -0.5
        user_segment = "Mobile User"
        insight = "User finds the user interface (search, home screen) too cluttered, especially with podcasts, hindering music discovery."
    # 4. Intent to explore
    elif any(k in text_lower for k in ["explore", "discover weekly", "new music", "find new", "underground", "niche"]):
        theme = "intent to explore"
        subtheme = ["niche-genres"]
        sentiment = 0.2 if "love" in text_lower or "good" in text_lower else -0.1
        user_segment = "Explorer Cohort"
        insight = "User expresses an active desire to find new releases or explore niche/underground genres."
    # 5. Missing control
    elif any(k in text_lower for k in ["block", "exclude", "ban", "dislike", "hide"]):
        theme = "missing control"
        subtheme = ["no-block-artist"]
        sentiment = -0.4
        user_segment = "Mobile User"
        insight = "User wants explicit control to block specific artists or exclude certain styles from recommendation algorithms."
    # 6. Playlist dependence
    elif any(k in text_lower for k in ["my playlist", "custom playlist", "my library"]):
        theme = "playlist dependence"
        subtheme = ["manual-curation-heavy"]
        sentiment = 0.0
        user_segment = "Static Listener"
        insight = "User relies heavily on custom curated playlists rather than trusting algorithmic channels."
    else:
        theme = "unmet need"
        subtheme = ["social-discovery-missing"]
        sentiment = -0.1
        user_segment = "Mobile User"
        insight = "User mentions a gap or missing discovery feature in the application."
        
    return theme, subtheme, sentiment, user_segment, insight, confidence

def is_valid_discovery_comment(text):
    text_lower = text.lower()
    
    # Exclude short meaningless comments
    if len(text.split()) < 4:
        return False
        
    # Exclude obvious spam or ads
    if any(k in text_lower for k in ["promo", "crypto", "free money", "earn cash", "join now", "invest", "subscribe to my"]):
        return False
        
    # Must contain at least one discovery-related keyword
    return any(k in text_lower for k in DISCOVERY_KEYWORDS)

def collect_app_store_reviews():
    collected = []
    print("Collecting App Store reviews...")
    for country in COUNTRIES:
        # Fetch page 1, 2, and 3 of reviews
        for page in range(1, 4):
            url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={APP_ID}/sortby=mostrecent/json"
            data = fetch_json(url)
            if not data or 'feed' not in data or 'entry' not in data['feed']:
                continue
                
            entries = data['feed']['entry']
            # If there's only 1 entry, it might be a dict, convert to list
            if isinstance(entries, dict):
                entries = [entries]
                
            for entry in entries:
                # Skip the first entry if it's the app info
                if 'im:name' in entry:
                    continue
                    
                try:
                    review_id = entry.get('id', {}).get('label')
                    author = entry.get('author', {}).get('name', {}).get('label')
                    rating = int(entry.get('im:rating', {}).get('label', 0))
                    title = entry.get('title', {}).get('label', '')
                    content = entry.get('content', {}).get('label', '')
                    date_str = entry.get('updated', {}).get('label', '')
                    
                    full_text = f"{title}. {content}" if title else content
                    dt = parse_app_store_date(date_str)
                    
                    # Store raw
                    collected.append({
                        "id": review_id,
                        "source": "app_store",
                        "platform": "iOS",
                        "country": country.upper(),
                        "date": dt,
                        "author": author,
                        "rating": rating,
                        "raw_text": full_text
                    })
                except Exception as ex:
                    print(f"Error parsing App Store review: {ex}", file=sys.stderr)
                    
    print(f"Collected {len(collected)} raw App Store reviews.")
    return collected

def collect_reddit_reviews():
    collected = []
    print("Collecting Reddit discussions...")
    # Search r/spotify for posts matching discovery terms
    queries = [
        "recommendations", "shuffle", "algorithm", "stale", "autoplay"
    ]
    for q in queries:
        url = f"https://www.reddit.com/r/spotify/search.json?q={q}&restrict_sr=on&sort=new&limit=50"
        data = fetch_json(url)
        if not data or 'data' not in data or 'children' not in data['data']:
            continue
            
        posts = data['data']['children']
        for post in posts:
            post_data = post.get('data', {})
            if not post_data:
                continue
                
            try:
                post_id = post_data.get('id')
                author = post_data.get('author')
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                created_utc = post_data.get('created_utc')
                
                full_text = f"{title}. {selftext}" if selftext else title
                dt = datetime.datetime.utcfromtimestamp(created_utc)
                
                # Check for duplicates by ID
                if any(x['id'] == post_id for x in collected):
                    continue
                    
                collected.append({
                    "id": post_id,
                    "source": "reddit",
                    "platform": "Web/Mobile",
                    "country": None,
                    "date": dt,
                    "author": author,
                    "rating": None,
                    "raw_text": full_text
                })
            except Exception as ex:
                print(f"Error parsing Reddit post: {ex}", file=sys.stderr)
                
    print(f"Collected {len(collected)} raw Reddit posts.")
    return collected

def main():
    # 1. Collect
    raw_app_store = collect_app_store_reviews()
    raw_reddit = collect_reddit_reviews()
    
    total_raw_collected = len(raw_app_store) + len(raw_reddit)
    print(f"Total raw records collected: {total_raw_collected}")
    
    # 2. Filter & Process
    all_raw = raw_app_store + raw_reddit
    
    valid_records = []
    source_counts = {"app_store": 0, "reddit": 0}
    theme_counts = {}
    
    # Sort by date descending
    all_raw.sort(key=lambda x: x['date'], reverse=True)
    
    # Date filter start
    start_filter_date = datetime.datetime(2019, 1, 1)
    
    seen_texts = set()
    
    for item in all_raw:
        # Date Filter
        if item['date'] < start_filter_date:
            continue
            
        raw_text = item['raw_text']
        cleaned = clean_text(raw_text)
        
        # Deduplicate identical cleaned texts
        if cleaned.lower() in seen_texts:
            continue
        seen_texts.add(cleaned.lower())
        
        # Filter rules
        if not is_valid_discovery_comment(cleaned):
            continue
            
        # Classify
        theme, subtheme, sentiment, user_segment, insight, confidence = classify_comment(cleaned)
        
        # Track statistics
        source_counts[item['source']] = source_counts.get(item['source'], 0) + 1
        if theme:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
            
        valid_records.append({
            "source": item['source'],
            "platform": item['platform'],
            "country": item['country'],
            "date": item['date'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            "original_text": raw_text,
            "cleaned_text": cleaned,
            "theme": theme,
            "subtheme": subtheme,
            "sentiment": sentiment,
            "user_segment": user_segment,
            "insight": insight,
            "confidence_score": confidence
        })
        
    print(f"Total valid records after filtering: {len(valid_records)}")
    
    # 3. Print Output
    output_data = {
        "summary": {
            "total_raw_collected": total_raw_collected,
            "total_valid_records": len(valid_records),
            "date_range": {
                "start": "2019-01-01T00:00:00Z",
                "end": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            },
            "source_wise_counts": source_counts,
            "top_themes": sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        },
        "records": valid_records
    }
    
    with open("real_spotify_feedback.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print("SUCCESS: real_spotify_feedback.json written.")

if __name__ == "__main__":
    main()
