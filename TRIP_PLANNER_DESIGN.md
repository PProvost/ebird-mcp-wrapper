# Birding Trip Planner — Design Spec

## What We're Building

A mobile-friendly app that takes your current location and personal life list, then plans 2–3 ready-to-go birding outings ranked by time commitment. Each outing identifies which new species you're likely to find, where to go, in what order, and roughly how long it'll take.

---

## Core Challenges & How to Solve Them

### 1. Life List Access

**Problem:** The eBird API has no endpoint for personal user data — life lists are locked behind a login.

**Solution:** Direct the user to eBird's download page (`ebird.org/MyEBird`) to export their life list CSV. The app imports it once and stores it locally in the browser (localStorage/IndexedDB). The user only needs to re-import when they've added new species.

**UX approach:**
- On first launch, show a "Set up your life list" step with a deep link directly to the eBird download page
- After import, show a count ("You've seen 312 species") and a "Re-import" button
- Store per-device — cross-device sync is a potential v2 enhancement

The eBird life list CSV includes common name, scientific name, location, date, etc. — everything we need.

---

### 2. Location → eBird Region Code

**Good news:** Most eBird geo endpoints (nearby observations, nearby hotspots) accept raw `lat`/`lng` directly — no region code needed for the core features.

**Region code is needed for:** Seasonal frequency data (bar charts), which tells us what's *likely* this time of year vs. just what's been seen recently.

**Solution:** Reverse geocode lat/lng → county name → map to eBird region code format.
- Use **Nominatim** (OpenStreetMap, free, no API key) for reverse geocoding
- eBird US county codes follow the pattern `US-{STATE}-{3-digit FIPS}`, which is derivable from the geocoding result
- Fall back to state-level (`US-CO`) if county lookup fails

---

### 3. "Likely to See" — Identifying Target Species

This is the core intelligence of the app. Two data sources combined:

**A. Recent local observations** (what's actually there now)
- Pull recent observations within 25km using the eBird geo endpoint
- Look back 14 days
- Filter out species already on the life list
- This tells you what's been *reported* recently

**B. Seasonal frequency** (what's expected this time of year)
- Use eBird's bar chart data for the local region
- This adjusts for the fact that a species might not have been reported lately but is common this month
- Candidates should score high on *either* recent sightings *or* high seasonal frequency (or both)

**Scoring formula (conceptual):**
```
score = (recency_weight × days_since_last_sighting⁻¹)
      + (frequency_weight × seasonal_frequency)
      + (rarity_bonus if notable)
```

Top-scoring candidates become the "target species list" for trip planning.

---

### 4. Outing Planning — The Hard Part

**Inputs per outing:**
- Target species list
- Nearby hotspots (from eBird)
- Which species have been seen at which hotspot recently
- Driving time from current location
- Estimated time at hotspot

**Hotspot scoring:**
For each nearby hotspot, calculate:
- Number of target species seen there recently
- Driving time from user's location
- Estimated visit duration

**Estimating visit duration at a hotspot (the tricky bit):**
eBird has no trail length data. But the checklist endpoint returns checklists with duration in minutes — averaging recent checklist durations at a hotspot gives a solid proxy for typical visit time. e.g., if 50 recent checklists at a hotspot average 45 minutes, plan for ~45 minutes there.

**Outing tiers:**

| Tier | Drive budget | Visit budget | Hotspots | Character |
|---|---|---|---|---|
| Quick (1 hr) | ≤15 min | ~30–45 min | 1 | Highest-yield nearby spot; top 5 targets |
| Half-day (3–4 hrs) | ≤30 min | ~2–3 hrs total | 2–3 | Route-optimized; mix of habitats |
| Full day (6–8 hrs) | ≤90 min | ~5–6 hrs total | 4–6 | Includes notable/rare species; longer drives worthwhile |

**Route optimization:** With ≤6 stops, brute-force ordering is fine (visiting in order of fewest new species → most, or by proximity). For half-day and full-day, compute a simple nearest-neighbor route.

---

### 5. Driving Time / Routing

| Option | Cost | Accuracy |
|---|---|---|
| Google Maps Directions API | $5/1000 requests | Best |
| OpenRouteService | Free, open source | Very good |
| Straight-line × speed factor | Free | Rough but workable |

**Decided: OpenRouteService** — free, generous limits, good accuracy, easy to swap to Google Maps later.

**Maps display:** Leaflet.js with OpenStreetMap tiles (free, no API key).

---

### 6. Platform: Progressive Web App (PWA)

**Why PWA over native mobile?**
- Works on any phone browser — Android and iPhone
- Can be "installed" to the home screen (feels native)
- Uses the browser's Geolocation API (same GPS accuracy as native)
- One codebase, deployable in hours
- No app store gatekeeping or approval process

---

## Tech Stack

**Backend (Python — familiar territory):**
- FastAPI — same language/patterns as the MCP server
- Proxies eBird API calls (keeps the API key server-side)
- Handles routing requests via OpenRouteService
- Handles Nominatim reverse geocoding
- No database needed for v1 (stateless — life list lives in the browser)

**Frontend:**
- React (component-based, good for the card/step UI this needs)
- Leaflet.js for the map
- PWA manifest + service worker for installability

**Hosting (cheap/free to start):**
- Backend: Render or Railway (free tier handles light traffic)
- Frontend: Netlify or Vercel (free)
- Alternative: FastAPI serves the static React build from a single container

**Life list:** Stored in browser IndexedDB — simple, private, zero infra cost. Cross-device sync is a v2 consideration.

---

## Decisions

| Decision | Choice |
|---|---|
| Platform | PWA |
| Routing API | OpenRouteService (free) |
| Life list storage | Per-device (browser IndexedDB) |
| MVP scope | Full 3-tier outing planner |

## Remaining Open Question

**Map vs. list UI:** Should the primary output be a visual map showing the hotspot route, a card/list view ("Go here, then here, expect to see these birds"), or both?

Likely answer: both — a map for spatial orientation + cards with species details. The map doesn't need to be elaborate (just pins and a route line).

---

## What This Does NOT Need (v1)

- User accounts / login
- Real-time notifications ("rare bird alert!")
- Social features
- eBird checklist submission
- A database

All of these are natural v2 additions if the core proves useful.
