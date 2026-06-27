# AI Feedback Discovery Workflow Steps

This document outlines the detailed step-by-step processing workflow of the Spotify growth feedback discovery engine.

---

### Step 1: Collect Feedback Data
*   **Purpose:** Automatically retrieve raw, unfiltered feedback from external public sources (App Store, Play Store, Reddit, Spotify forums, social posts).
*   **Input:** API credentials/endpoints, scraping configurations, RSS feed urls, and polling cron triggers.
*   **Output:** List of raw JSON feedback objects containing raw review text, ratings, source tags, timestamps, and author usernames.
*   **Failure Cases:** API rate limits (HTTP 429), target website layout updates breaking scrapers, network timeouts, expired credentials.

---

### Step 2: Clean the Text
*   **Purpose:** Prepare text for analysis by removing markup, duplicate submissions, and formatting artifacts.
*   **Input:** List of raw JSON feedback objects.
*   **Output:** Normalized feedback objects containing plain text strings with standardized whitespaces and stripped HTML/Markdown tags.
*   **Failure Cases:** Encoding/decoding errors (e.g., emoji corruptions), over-aggressive cleaning stripping useful indicators (like exclamation marks or capitalization), text truncation.

---

### Step 3: Detect Language and Remove Noise
*   **Purpose:** Filter out non-English content (or prepare it for translation) and discard low-value noise (e.g., single-word posts like "nice", "ok", or gibberish).
*   **Input:** Cleaned, plain-text feedback objects.
*   **Output:** Enriched feedback objects tagged with a language code, excluding entries identified as spam or noise.
*   **Failure Cases:** Misclassifying specialized terms/slang as foreign languages, filtering out valid short-form bug reviews (e.g., "crashing on startup"), translation API failures.

---

### Step 4: Classify into Themes
*   **Purpose:** Assign reviews to specific product feature categories (e.g., UI/UX, Audio Quality, Offline Mode, Premium Subscriptions, Podcasts) for targeted routing.
*   **Input:** Noise-filtered text records.
*   **Output:** Structured feedback objects with associated theme tags and classifier confidence scores.
*   **Failure Cases:** Misclassification due to ambiguous phrasing, missing secondary categories for multi-topic reviews, LLM classifier timeouts or cost overruns.

---

### Step 5: Detect User Segment
*   **Purpose:** Identify the user segment (e.g., Free vs. Premium tier, iOS vs. Android, long-term user vs. new installer) to prioritize high-value user feedback.
*   **Input:** Feedback text content, source metadata (device info, App Store vs Play Store), and review rating.
*   **Output:** Feedback objects tagged with inferred or explicit user segment attributes.
*   **Failure Cases:** Incomplete metadata resulting in "Unknown" user tags, incorrect inference of premium status from non-contextual text.

---

### Step 6: Summarize Insights
*   **Purpose:** Condense individual complex feedback items into rapid-read bullet points and compile batches of feedback into overall system trend summaries.
*   **Input:** Classified and segmented feedback records.
*   **Output:** Extracted bullet points of key requests, bugs, and feature ideas.
*   **Failure Cases:** LLM model hallucinations, summaries that are too vague to be actionable (e.g., "Fix the app"), exceeding LLM context window limits during batch summaries.

---

### Step 7: Store Results
*   **Purpose:** Save all processed data points, classifications, and summaries into persistent storage for historical analytics and queries.
*   **Input:** Fully analyzed, enriched, and structured feedback records.
*   **Output:** Successful database save transaction confirmation.
*   **Failure Cases:** Database connection pool exhaustion, schema validation mismatch constraints, storage capacity limits.

---

### Step 8: Send Results to Frontend
*   **Purpose:** Serve aggregated feedback charts, sentiment patterns, and classified reviews to the Spotify PM interface.
*   **Input:** HTTP client requests specifying query terms, filters, pagination, or persistent socket subscriptions.
*   **Output:** Serialized JSON payload containing processed statistics, sentiment ratios, and paginated lists of matching reviews.
*   **Failure Cases:** API endpoint crashes under load, slow response times due to lack of index optimization, CORS origin block errors.
