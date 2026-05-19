# vaultwares-flows

> Native App version of **Vault Flows** — Create any pipeline you can imagine using anything, anywhere, any way.

## Overview

**Vaultwares Flows** is a node-based visual workflow builder built with PySide6/Qt. It features an infinite canvas where you can drag, drop, and wire nodes together to create powerful AI/diffusion pipelines — locally or via the Vaultwares Pipelines cloud API.

Inspired by Figma Weave's canvas and the ComfyUI node system.

---

## Features

| Feature | Description |
|---|---|
| 🎨 **Vaultwares Branding** | Dark UI with purple accent palette |
| 🧩 **Node-Based Canvas** | Infinite QGraphicsScene with dot-grid background |
| ↔ **Pan / Zoom** | Middle-mouse or Space+drag to pan; scroll to zoom |
| 🔗 **Animated Connections** | Type-coloured bezier wires with flowing particles |
| 📦 **40+ Built-in Nodes** | AI, Diffusion, Image, Text, Data, Control, Output |
| 🗺️ **Minimap** | Click-to-navigate mini overview (bottom-right) |
| 📋 **Node Library** | Searchable, categorised sidebar with drag-to-canvas |
| ⚙️ **Properties Panel** | Dynamic form editor for selected node inputs |
| ☁️ **Cloud Ready** | Connect to Vaultwares Pipelines API |
| 🔥 **AI / Diffusion Ready** | Optional PyTorch, xformers, Diffusers support |

---

## Quick Start

```bash
# 1. Install core dependency
pip install PySide6

# 2. Run the app
python main.py
```

### Optional AI/Diffusion stack

```bash
pip install -r requirements-ai.txt
```

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `Space` + drag | Pan canvas |
| Scroll wheel | Zoom in/out |
| `F` | Fit all nodes in view |
| `0` | Reset zoom to 100% |
| `+` / `-` | Zoom in / out |
| `Del` / `Backspace` | Delete selected |
| `Escape` | Cancel connection |
| `V` | Select tool |
| `H` | Pan tool |

---

## Node Categories

- **Input** — Text, Number, Image, Audio, Video, Webcam
- **AI** — Load Checkpoint, LoRA, ControlNet, CLIP Encode
- **Diffusion** — KSampler, VAE Encode/Decode, Empty Latent, ControlNet Apply
- **Image** — Resize, Crop, Flip, Rotate, Blur, Color Adjust, Blend
- **Text** — Format, Concatenate, Split, Prompt Builder
- **Data** — Math, Clamp, Compare
- **Control** — If/Else, For Loop, Batch Split
- **Output** — Save Image, Preview, API Send, Print/Log
- **Utility** — Note, Reroute, Seed Generator

---

## Project Structure

```
vaultwares-flows/
├── main.py                    # Entry point
├── requirements.txt           # Core deps (PySide6)
├── requirements-ai.txt        # Optional AI/diffusion stack
├── pyproject.toml
└── app/
    ├── theme/
    │   └── palette.py         # Dark colour palette + QSS
    ├── canvas/
    │   ├── scene.py           # FlowScene (QGraphicsScene)
    │   ├── view.py            # FlowView (pan/zoom/drag-drop)
    │   ├── node.py            # FlowNode + FlowPort
    │   ├── edge.py            # FlowEdge + DraftEdge
    │   └── minimap.py         # Minimap overlay
    ├── nodes/
    │   └── registry.py        # All 40+ node type definitions
    ├── panels/
    │   ├── node_library.py    # Left sidebar
    │   └── properties.py      # Right properties panel
    └── main_window.py         # FlowWindow (QMainWindow)
```
