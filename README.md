# VECTOR PRO — Advanced Object Tracking

Real-time multi-object tracking built for MacBook + iPhone, ready for drone programming.

## What's in here

```
index.html                  ← The entire app, single file
.github/workflows/deploy.yml ← Auto-deploy to GitHub Pages on push
bridge/drone_bridge.py       ← WebSocket → MAVLink relay for real drones
README.md                   ← This file
```

## Quick start (MacBook)

```bash
# Option 1: Python server (simplest)
cd vector-pro
python3 -m http.server 8080
# Open http://localhost:8080

# Option 2: Deploy to GitHub Pages (see below)
```

## iPhone

1. Deploy to GitHub Pages (see below)
2. Open the https:// URL in Safari
3. Tap **Share → Add to Home Screen** for fullscreen camera + rear cam

## GitHub Pages Deploy (built-in)

The app has a GitHub deploy panel in the side panel. Fill in:
- **GitHub Username**
- **Repo name** (e.g. `vector-pro`)
- **Classic token** — Settings → Developer settings → Personal access tokens → Tokens (classic)
  - Scopes: **repo** + **workflow** (must be classic token, NOT fine-grained)

Tap **Init Repo** → app pushes itself to GitHub, enables Pages.
URL: `https://your-username.github.io/vector-pro/`

## Detector stack (auto-selects best available)

1. **YOLOv8n** via ONNX Runtime Web / WebGL (~6.7MB, quantized int8) — fastest, most accurate
2. **MediaPipe EfficientDet-Lite0** GPU — solid fallback
3. **TFJS COCO-SSD** — works everywhere

## Analytics (cvzone-style)

| Feature | How to use |
|---------|-----------|
| Speed (km/h) | Shown on every label automatically |
| Counting lines | Click **╱ LINE** → click 2 points on video |
| Alert zones | Click **▭ ZONE** → drag rectangle on video |
| Heatmap | Toggle **Heatmap** button or press **H** |
| Re-ID | Objects keep their ID after leaving frame; lock survives the gap |

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `L` | Auto-lock best object |
| `U` | Unlock |
| `Space` | Pause/resume |
| `H` | Toggle heatmap |
| `T` | Toggle trails |
| `S` | Toggle speed labels |

## Drone bridge

```bash
pip install websockets pymavlink
python3 bridge/drone_bridge.py
# Real FC:
python3 bridge/drone_bridge.py --mavlink /dev/ttyUSB0
# ArduPilot SITL:
python3 bridge/drone_bridge.py --mavlink udp:127.0.0.1:14550
```

Connect the app to `ws://localhost:8765`. Bridge emits MAVLink body-frame velocity commands from the locked target's position error + range.

## GitHub token note

Must be a **classic** token (not fine-grained PAT). Fine-grained tokens cannot modify `.github/workflows/` — a known GitHub API limitation.
