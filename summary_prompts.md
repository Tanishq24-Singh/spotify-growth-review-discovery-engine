# AI Prompt Design: Summary Insights Generator

This document details the system prompt, user prompt template, output format specification, and output example for generating weekly/monthly product summaries from classified review data.

---

## 1. System Prompt

```text
You are a Principal Product Manager and Analytics Director at Spotify. 
Your task is to analyze a batch of classified user reviews and generate a comprehensive, structured product summary that surfaces key discovery insights and growth recommendations.

Your summary must accurately answer these 6 core business questions based on the review data provided:
1. Why do users struggle to discover new music?
2. What are the most common discovery-related user frustrations?
3. What specific listening behaviors or goals are users trying to achieve?
4. Why do users feel trapped replaying the same music (repetitive loops)?
5. Which user segments (e.g., Premium, Free, iOS, Android, power users) are most affected by discovery friction?
6. What unmet needs and missing features keep appearing?

### Hard Rules:
1. Base all observations strictly on the provided dataset. Do not make up user reviews or introduce features/problems not present in the input logs.
2. Return a valid JSON object ONLY. Do not output codeblocks, markdown commentary, or introductory conversational filler.
3. Keep product recommendations highly actionable and product-focused (e.g., UI tweaks, algorithm updates, control preferences).
```

---

## 2. User Prompt Template

```text
Analyze the following batch of classified Spotify reviews from {{START_DATE}} to {{END_DATE}}.

[BATCH METADATA]
Total Records Ingested: {{TOTAL_COUNT}}
Active Channels: {{CHANNELS}}
Primary Theme Distribution:
{{THEME_DISTRIBUTION_JSON}}

[CLASSIFIED RECORDS SAMPLE]
{{CLASSIFIED_RECORDS_JSON}}

Analyze the data and output the structured JSON summary meeting the format guidelines.

JSON Output:
```

---

## 3. Output Format

The output must be a single, valid JSON block matching this exact schema:

```json
{
  "period": "YYYY-MM-DD to YYYY-MM-DD",
  "total_records_analyzed": 0,
  "executive_summary": "A high-level paragraph summarizing the core feedback theme of this period.",
  "discovery_barriers": {
    "barriers": ["List of main reasons users struggle to discover new music"],
    "common_frustrations": ["List of common complaints about UI or features"]
  },
  "intended_behaviors": {
    "goals": ["List of listening behaviors/flows users are actively trying to achieve"]
  },
  "repetitive_listening_triggers": {
    "drivers": ["Analysis of why users are stuck replaying the same music/filter bubbles"]
  },
  "affected_segments": [
    {
      "segment": "Segment name (e.g. Premium/iOS)",
      "impact_description": "Detailed description of how this group is affected."
    }
  ],
  "unmet_needs": [
    {
      "need": "Feature description",
      "frequency": "High/Medium/Low",
      "user_quote": "A representative evidence quote from the review list"
    }
  ],
  "recommended_actions": [
    {
      "area": "Product area (e.g., Algorithm, Home UI, Settings)",
      "action": "Description of the recommended feature or fix",
      "priority": "High/Medium/Low"
    }
  ]
}
```

---

## 4. Example Output

```json
{
  "period": "2026-06-18 to 2026-06-25",
  "total_records_analyzed": 1420,
  "executive_summary": "This week's reviews are heavily dominated by frustration regarding Smart Shuffle loops and podcast clutter on the Home feed. Users express a strong desire to explore new music but feel trapped in repetitive listening patterns due to algorithm exploitation.",
  "discovery_barriers": {
    "barriers": [
      "Algorithmic recommendations prioritizing previously played tracks",
      "Cluttered interfaces pushing non-music content, blocking paths to new releases"
    ],
    "common_frustrations": [
      "Smart Shuffle playing the same 5-10 songs on rotation",
      "Autoplay shifting to completely mismatched genres"
    ]
  },
  "intended_behaviors": {
    "goals": [
      "Transitioning dynamically from a known playlist into similar but novel genres",
      "Exploring niche local music and independent artists"
    ]
  },
  "repetitive_listening_triggers": {
    "drivers": [
      "Smart shuffle algorithms over-indexing on historical heavy rotation tracks",
      "Autoplay repeating the same track cache instead of fetching live recommendation nodes"
    ]
  },
  "affected_segments": [
    {
      "segment": "Premium/iOS and Android Mobile Users",
      "impact_description": "Power users with custom playlists are most vocal about algorithm repetition. They rely heavily on Smart Shuffle to dynamically update their listening experience but find it counterproductive."
    }
  ],
  "unmet_needs": [
    {
      "need": "Explicit artist block setting",
      "frequency": "High",
      "user_quote": "Please let me block specific artists from appearing in my recommendations."
    },
    {
      "need": "Exclude playlist from algorithm profile",
      "frequency": "Medium",
      "user_quote": "My kids listen to nursery rhymes and now my recommendations are ruined."
    }
  ],
  "recommended_actions": [
    {
      "area": "Smart Shuffle Algorithm",
      "action": "Inject a novelty-bias coefficient into the recommendation builder to enforce a minimum of 40% unplayed tracks in shuffle sequences.",
      "priority": "High"
    },
    {
      "area": "Settings / Control Options",
      "action": "Introduce a simple toggle to allow users to exclude specific playlists from affecting their personalized taste profile.",
      "priority": "High"
    },
    {
      "area": "Home Feed UI",
      "action": "Implement a music-only filter toggle on the Home screen dashboard to remove podcasts and audiobooks for listeners seeking pure music discovery.",
      "priority": "Medium"
    }
  ]
}
```
