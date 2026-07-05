# Spotify Growth: AI Review Discovery Engine

An AI-powered review discovery engine and dashboard for product managers to query reviews, analyze user friction, and review weekly AI recommendations.

## Features
- **Dynamic API Settings Drawer**: Easily switch between a local backend (`http://localhost:8080/api/v1`) and a deployed production backend (e.g. on Render) directly from the UI.
- **Connection Diagnostics**: Built-in "Test Connection" tool to ping and verify backend API availability in real time.
- **User Reviews Audit Grid**: Search, filter by labels (e.g., discovery frustration, repetitive listening), and filter by user segments.
- **AI Summary & Interventions**: Displays executive summaries, average sentiment scores, friction percentages, and recommended product interventions.
- **Automatic Fallback Database**: Server automatically initializes schemas and falls back to a local SQLite database (`spotify_feedback.db`) if no PostgreSQL `DATABASE_URL` is set.

---

## 1. Local Development Setup

### Prerequisites
- Python 3.8+ installed on your machine.

### Installation
1. Clone this repository to your local machine.
2. Open your terminal in the repository root directory.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App
1. Start the Flask server:
   ```bash
   python server.py
   ```
2. Open your web browser and navigate to:
   **[http://localhost:8080/](http://localhost:8080/)**
3. The dashboard will automatically serve the UI and load review summaries from your local SQLite database.

---

## 2. Deployment Instructions

### Frontend (Vercel)
The frontend is a static single-page application (`index.html`).
1. Push this repository to GitHub.
2. Go to [Vercel](https://vercel.com) and click **Add New > Project**.
3. Import this GitHub repository.
4. Leave all settings at default and click **Deploy**.
5. Once deployed, open your live Vercel website URL.
6. Click the **Gear Icon (Settings)** next to "Spotify Growth" in the sidebar to configure your production backend API URL (e.g. your Render endpoint).

### Backend API (Render)
1. Go to [Render](https://render.com) and create a new **Web Service**.
2. Connect this GitHub repository.
3. Configure the service:
   - **Runtime**: `Python 3`
   - **Start Command**: `python server.py`
4. In the **Environment Variables** settings, configure:
   - `PORT`: `8080` (or leave default)
   - `DATABASE_URL`: PostgreSQL connection string (e.g. Neon or Supabase)
   - `OPENAI_API_KEY`: Your OpenAI API Key for running prompt chains
5. Use your Render web service URL (e.g. `https://your-service.onrender.com/api/v1`) as the Backend API URL in your Vercel settings!
