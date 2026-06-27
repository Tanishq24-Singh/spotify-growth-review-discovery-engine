# Spotify Discovery Feedback: Review Label System

This document defines the categorization taxonomy for classifying Spotify user feedback related to music and content discovery.

---

### 1. discovery frustration
*   **Meaning:** The user experiences annoyance, complexity, cognitive overload, or general friction when trying to find new music, podcasts, or content.
*   **Sublabels:** `ui-clutter`, `search-friction`, `bad-filter-options`, `cluttered-homepage`
*   **Examples:** 
    *   *"The home screen is so crowded with podcasts I don't care about, I can't find new music releases."*
    *   *"It takes too many clicks to find the new releases page. The search tab is messy."*
*   **What it tells the business:** UI layout complexity or search pathways are blocking discovery. The design team should simplify navigation, improve filters, and reduce cognitive load on feed screens to increase discovery clicks.

---

### 2. repetitive listening
*   **Meaning:** The user feels trapped in a recommendation loop or "filter bubble" where Spotify continuously feeds them songs, artists, or genres they already know well, rather than fresh content.
*   **Sublabels:** `looping-recommendations`, `stale-daily-mixes`, `same-genre-bias`, `artist-overexposure`
*   **Examples:**
    *   *"My Discover Weekly has been playing the same songs I listened to last month."*
    *   *"Smart Shuffle just cycles through the same 10 songs over and over."*
*   **What it tells the business:** The recommendation algorithm is over-indexing on exploitation (familiarity) rather than exploration (novelty). Engineers need to tune the discovery algorithms for higher novelty factors or introduce a "refresh taste profile" button.

---

### 3. recommendation mismatch
*   **Meaning:** Spotify’s automated recommendations (Autoplay, Radio, Smart Shuffle, etc.) are completely irrelevant, jarring, or mismatch the user's current mood, genre preference, or context.
*   **Sublabels:** `wrong-genre-autoplay`, `mood-disconnect`, `incongruent-shuffle`, `foreign-language-intrusion`
*   **Examples:**
    *   *"I was listening to a relaxing acoustic playlist and Autoplay played a loud heavy metal song next."*
    *   *"Spotify keeps showing me French pop songs just because I listened to one French track."*
*   **What it tells the business:** Transition algorithms or taste-mapping models are failing to capture context. Autoplay and Shuffle rules need stricter guardrails (e.g., matching BPM, mood tags, or language) to prevent user jarring.

---

### 4. playlist dependence
*   **Meaning:** The user relies exclusively on static or manually curated playlists because they do not trust or enjoy algorithmic feeds.
*   **Sublabels:** `manual-curation-heavy`, `mistrust-of-algorithms`, `static-library-reliance`
*   **Examples:**
    *   *"I only listen to my own custom playlists. The algorithmic stations are useless."*
    *   *"I never use the Home feeds anymore; I just go straight to my Library."*
*   **What it tells the business:** Low trust in Spotify's automated features. The platform should focus on "assisted curation" features (e.g., inline suggestions inside user playlists) to gently build trust and transition static listeners into dynamic discovery formats.

---

### 5. intent to explore
*   **Meaning:** The user explicitly expresses a desire to branch out, learn about new genres, find obscure/indie artists, or discover global music, but feels the system isn't helper.
*   **Sublabels:** `niche-genres`, `underground-artists`, `global-music-exploration`, `starter-packs-request`
*   **Examples:**
    *   *"I want to get into 80s synthwave but I don't know where to start."*
    *   *"Show me local, independent artists in my city rather than the global top 50."*
*   **What it tells the business:** High-value, engaged user segment with unmet curiosity. Spotify can build guided discovery features, "genre deep-dives", or community-led curator recommendations to satisfy this explorer cohort.

---

### 6. missing control
*   **Meaning:** The user wants explicit control to tune, adjust, or block recommendations (e.g., downvoting, banning artists/genres) but cannot find these settings or they do not exist.
*   **Sublabels:** `no-block-artist`, `cannot-exclude-genre`, `no-downvote-button`, `taste-profile-exclusion`
*   **Examples:**
    *   *"I hate this singer but Spotify keeps putting them in my mixes and there's no way to block them."*
    *   *"I want to listen to white noise for sleep without it ruining my recommendation algorithm."*
*   **What it tells the business:** High churn indicator. Users feel trapped and powerless. Product teams must introduce simple feedback loops like "Don't recommend this artist again" or "Exclude this playlist from my taste profile" (e.g., for sleep/kids music).

---

### 7. unmet need
*   **Meaning:** The user identifies missing discovery-related features, integrations, or capabilities that are currently absent from Spotify.
*   **Sublabels:** `social-discovery-missing`, `cross-platform-import`, `local-gig-integration`, `lyrics-search-discovery`
*   **Examples:**
    *   *"I wish I could easily discover music through my friends' live listening on mobile."*
    *   *"I want Spotify to recommend music based on the local concerts happening this weekend."*
*   **What it tells the business:** Whitespace opportunities. These insights point to potential new features, updates, or integrations (e.g., ticketing partnerships, richer social feeds) that can serve as major growth drivers.
