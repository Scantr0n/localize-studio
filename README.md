# Localize Studio

A local tool that turns the manual Şengün-video workflow (transcribe →
translate → styled captions → burned-in video) into a repeatable app.
Runs entirely on your Mac — no hosting, no accounts, just for you.

## Running it

Two dev servers, already registered in the workspace's `.claude/launch.json`:

- **Backend**: `localize-studio-backend` — FastAPI on port 8010
- **Frontend**: `localize-studio` — Vite/React on port 5174

Start both (via the `run` skill, or manually):

```bash
# backend
cd backend && .venv/bin/python -m uvicorn main:app --port 8010

# frontend
cd frontend && npm run dev
```

Then open http://localhost:5174.

## One-time setup for translation

AI translation calls the Anthropic API. Copy `backend/.env.example` to
`backend/.env` and add your own key:

```
ANTHROPIC_API_KEY=your_key_here
```

Without it, everything else works (upload, crop-detect, transcribe, manual
transcript editing, styling, rendering) — you'll just need to type
translations in by hand instead of getting AI suggestions.

## What it does

1. **Upload** a client's video.
2. **Prepare** — auto-detects and crops black bars/letterboxing.
3. **Transcript** — Whisper transcribes it, but always review and fix lines
   before continuing. Whisper is genuinely unreliable on multi-language or
   code-switched audio (confirmed hands-on with the Şengün clip) — this step
   is not optional polish.
4. **Translate** — AI-suggested translation into a target language, editable
   before you use it.
5. **Style & Render** — pick a caption style, build one or more tracks (e.g.
   a native-language version + a translated version), click on the preview
   frame to place the tag anchor if the style needs one, and render.
   Four styles are live: `head_tag` (the one that actually shipped to
   Şengün's Weibo — big color-cycling caption + a small name/greeting tag
   near the speaker's head), `bubbly`, `bounce_rotate`, and `comic_pop` (the
   three you called out as liked from the earlier style rounds, ported over
   2026-07-21).

## What's NOT here yet (on purpose — see the build plan)

- A few styles from the `influencer-china` rounds aren't ported over yet
  (glitch_pop was explicitly disliked, so skipped; a couple others were never
  revisited after `head_tag` became the focus). Adding one is a single new
  file in `backend/captions/styles/` following the existing pattern.
- Code-switched audio (multiple languages in one clip) isn't auto-detected
  per-segment — you'll transcribe in one dominant language and manually
  split/relabel segments that need it, the way the Şengün clip was corrected
  by hand.
- No job history/browsing UI — each job lives at its own URL
  (`/jobs/{id}/...`), you'll want to bookmark or note the URL for an
  in-progress client video.
- One anchor point per render (not one per tag moment).

See `/Users/jackscanlon/.claude/plans/vivid-chasing-toucan.md` for the full
design plan and reasoning.
