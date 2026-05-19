"""Node type definitions and registry for Vaultwares Flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PortDef:
    """Defines a single input or output port on a node."""

    name: str
    port_type: str = "any"
    required: bool = True
    default: Any = None
    description: str = ""


@dataclass
class NodeDef:
    """Full definition of a node type."""

    type_id: str
    title: str
    category: str
    description: str = ""
    inputs: list[PortDef] = field(default_factory=list)
    outputs: list[PortDef] = field(default_factory=list)
    # icon is a unicode emoji or short label shown in the header
    icon: str = "◈"

    @property
    def header_category(self) -> str:
        """Return the category key used for header gradient lookup."""
        return self.category.lower().replace(" ", "_")


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
_REGISTRY: dict[str, NodeDef] = {}


def register(node_def: NodeDef) -> NodeDef:
    _REGISTRY[node_def.type_id] = node_def
    return node_def


def get_node_definition(type_id: str) -> NodeDef | None:
    return _REGISTRY.get(type_id)


def all_definitions() -> list[NodeDef]:
    return list(_REGISTRY.values())


def definitions_by_category() -> dict[str, list[NodeDef]]:
    result: dict[str, list[NodeDef]] = {}
    for d in _REGISTRY.values():
        result.setdefault(d.category, []).append(d)
    return dict(sorted(result.items()))


# ===========================================================================
# ── Input nodes ──
# ===========================================================================
register(NodeDef(
    type_id="input.text",
    title="Text Input",
    category="Input",
    description="Free-form text entry",
    icon="T",
    inputs=[],
    outputs=[PortDef("text", "string")],
))

register(NodeDef(
    type_id="input.number",
    title="Number",
    category="Input",
    description="Numeric constant (float)",
    icon="#",
    inputs=[],
    outputs=[PortDef("value", "float")],
))

register(NodeDef(
    type_id="input.integer",
    title="Integer",
    category="Input",
    description="Integer constant",
    icon="#",
    inputs=[],
    outputs=[PortDef("value", "int")],
))

register(NodeDef(
    type_id="input.bool",
    title="Boolean",
    category="Input",
    description="True / False toggle",
    icon="⊤",
    inputs=[],
    outputs=[PortDef("value", "bool")],
))

register(NodeDef(
    type_id="input.image_file",
    title="Load Image",
    category="Input",
    description="Load an image from disk",
    icon="🖼",
    inputs=[],
    outputs=[PortDef("image", "image"), PortDef("mask", "mask")],
))

register(NodeDef(
    type_id="input.audio_file",
    title="Load Audio",
    category="Input",
    description="Load an audio file from disk",
    icon="🎵",
    inputs=[],
    outputs=[PortDef("audio", "audio")],
))

register(NodeDef(
    type_id="input.video_file",
    title="Load Video",
    category="Input",
    description="Load a video file from disk",
    icon="🎬",
    inputs=[],
    outputs=[PortDef("video", "video"), PortDef("frame_count", "int"),
             PortDef("fps", "float")],
))

register(NodeDef(
    type_id="input.webcam",
    title="Webcam",
    category="Input",
    description="Capture from webcam",
    icon="📷",
    inputs=[PortDef("device_id", "int", required=False, default=0)],
    outputs=[PortDef("image", "image")],
))

# ===========================================================================
# ── AI / Models ──
# ===========================================================================
register(NodeDef(
    type_id="ai.load_checkpoint",
    title="Load Checkpoint",
    category="AI",
    description="Load a Stable Diffusion checkpoint from disk",
    icon="🧠",
    inputs=[PortDef("model_path", "string")],
    outputs=[PortDef("model", "model"), PortDef("clip", "model"),
             PortDef("vae", "model")],
))

register(NodeDef(
    type_id="ai.load_lora",
    title="Load LoRA",
    category="AI",
    description="Load a LoRA adapter and merge into model",
    icon="⚙",
    inputs=[PortDef("model", "model"), PortDef("clip", "model"),
            PortDef("lora_path", "string"),
            PortDef("strength_model", "float", default=1.0),
            PortDef("strength_clip", "float", default=1.0)],
    outputs=[PortDef("model", "model"), PortDef("clip", "model")],
))

register(NodeDef(
    type_id="ai.load_controlnet",
    title="Load ControlNet",
    category="AI",
    description="Load a ControlNet model",
    icon="🕸",
    inputs=[PortDef("controlnet_path", "string")],
    outputs=[PortDef("controlnet", "model")],
))

register(NodeDef(
    type_id="ai.clip_encode",
    title="CLIP Text Encode",
    category="AI",
    description="Encode a text prompt with CLIP",
    icon="✍",
    inputs=[PortDef("clip", "model"), PortDef("text", "string")],
    outputs=[PortDef("conditioning", "conditioning")],
))

register(NodeDef(
    type_id="ai.clip_vision",
    title="CLIP Vision Encode",
    category="AI",
    description="Encode an image with CLIP Vision",
    icon="👁",
    inputs=[PortDef("clip_vision", "model"), PortDef("image", "image")],
    outputs=[PortDef("embedding", "conditioning")],
))

# ===========================================================================
# ── Diffusion ──
# ===========================================================================
register(NodeDef(
    type_id="diffusion.ksampler",
    title="KSampler",
    category="Diffusion",
    description="Core latent diffusion sampler",
    icon="〜",
    inputs=[
        PortDef("model", "model"),
        PortDef("positive", "conditioning"),
        PortDef("negative", "conditioning"),
        PortDef("latent_image", "latent"),
        PortDef("seed", "int", default=42),
        PortDef("steps", "int", default=20),
        PortDef("cfg", "float", default=7.0),
        PortDef("sampler_name", "string", default="euler"),
        PortDef("scheduler", "string", default="karras"),
        PortDef("denoise", "float", default=1.0),
    ],
    outputs=[PortDef("latent", "latent")],
))

register(NodeDef(
    type_id="diffusion.vae_encode",
    title="VAE Encode",
    category="Diffusion",
    description="Encode image to latent space",
    icon="→",
    inputs=[PortDef("vae", "model"), PortDef("image", "image")],
    outputs=[PortDef("latent", "latent")],
))

register(NodeDef(
    type_id="diffusion.vae_decode",
    title="VAE Decode",
    category="Diffusion",
    description="Decode latent back to image",
    icon="←",
    inputs=[PortDef("vae", "model"), PortDef("latent", "latent")],
    outputs=[PortDef("image", "image")],
))

register(NodeDef(
    type_id="diffusion.empty_latent",
    title="Empty Latent Image",
    category="Diffusion",
    description="Create a blank latent tensor",
    icon="□",
    inputs=[PortDef("width", "int", default=512),
            PortDef("height", "int", default=512),
            PortDef("batch_size", "int", default=1)],
    outputs=[PortDef("latent", "latent")],
))

register(NodeDef(
    type_id="diffusion.controlnet_apply",
    title="Apply ControlNet",
    category="Diffusion",
    description="Apply ControlNet conditioning to a prompt",
    icon="🕸",
    inputs=[PortDef("conditioning", "conditioning"), PortDef("controlnet", "model"),
            PortDef("image", "image"), PortDef("strength", "float", default=1.0)],
    outputs=[PortDef("conditioning", "conditioning")],
))

register(NodeDef(
    type_id="diffusion.upscale_latent",
    title="Upscale Latent",
    category="Diffusion",
    description="Upscale a latent image by a scale factor",
    icon="⤢",
    inputs=[PortDef("latent", "latent"), PortDef("scale_by", "float", default=2.0),
            PortDef("method", "string", default="nearest-exact")],
    outputs=[PortDef("latent", "latent")],
))

# ===========================================================================
# ── Image Processing ──
# ===========================================================================
register(NodeDef(
    type_id="image.resize",
    title="Resize Image",
    category="Image",
    description="Resize an image to target dimensions",
    icon="⤡",
    inputs=[PortDef("image", "image"), PortDef("width", "int", default=512),
            PortDef("height", "int", default=512),
            PortDef("method", "string", default="lanczos")],
    outputs=[PortDef("image", "image")],
))

register(NodeDef(
    type_id="image.crop",
    title="Crop Image",
    category="Image",
    description="Crop image to a rectangular region",
    icon="⊠",
    inputs=[PortDef("image", "image"),
            PortDef("x", "int", default=0), PortDef("y", "int", default=0),
            PortDef("width", "int", default=256), PortDef("height", "int", default=256)],
    outputs=[PortDef("image", "image")],
))

register(NodeDef(
    type_id="image.flip",
    title="Flip Image",
    category="Image",
    description="Flip image horizontally or vertically",
    icon="↔",
    inputs=[PortDef("image", "image"),
            PortDef("flip_horizontal", "bool", default=True),
            PortDef("flip_vertical", "bool", default=False)],
    outputs=[PortDef("image", "image")],
))

register(NodeDef(
    type_id="image.rotate",
    title="Rotate Image",
    category="Image",
    description="Rotate image by degrees",
    icon="↻",
    inputs=[PortDef("image", "image"), PortDef("degrees", "float", default=90.0)],
    outputs=[PortDef("image", "image")],
))

register(NodeDef(
    type_id="image.blur",
    title="Gaussian Blur",
    category="Image",
    description="Apply Gaussian blur to an image",
    icon="≈",
    inputs=[PortDef("image", "image"), PortDef("radius", "float", default=3.0)],
    outputs=[PortDef("image", "image")],
))

register(NodeDef(
    type_id="image.color_adjust",
    title="Color Adjust",
    category="Image",
    description="Adjust brightness, contrast, saturation, hue",
    icon="◑",
    inputs=[PortDef("image", "image"),
            PortDef("brightness", "float", default=1.0),
            PortDef("contrast", "float", default=1.0),
            PortDef("saturation", "float", default=1.0),
            PortDef("hue", "float", default=0.0)],
    outputs=[PortDef("image", "image")],
))

register(NodeDef(
    type_id="image.mask_from_image",
    title="Image to Mask",
    category="Image",
    description="Extract a mask from an image channel",
    icon="◻",
    inputs=[PortDef("image", "image"),
            PortDef("channel", "string", default="red")],
    outputs=[PortDef("mask", "mask")],
))

register(NodeDef(
    type_id="image.blend",
    title="Blend Images",
    category="Image",
    description="Blend two images together",
    icon="⊕",
    inputs=[PortDef("image_a", "image"), PortDef("image_b", "image"),
            PortDef("blend_mode", "string", default="normal"),
            PortDef("opacity", "float", default=0.5)],
    outputs=[PortDef("image", "image")],
))

register(NodeDef(
    type_id="image.preview",
    title="Preview",
    category="Image",
    description="Display an image in the node",
    icon="👁",
    inputs=[PortDef("image", "image")],
    outputs=[],
))

# ===========================================================================
# ── Text ──
# ===========================================================================
register(NodeDef(
    type_id="text.format",
    title="Format Text",
    category="Text",
    description="Format text using Python f-string style template",
    icon="⌘",
    inputs=[PortDef("template", "string"),
            PortDef("value_1", "any", required=False),
            PortDef("value_2", "any", required=False)],
    outputs=[PortDef("text", "string")],
))

register(NodeDef(
    type_id="text.concatenate",
    title="Concatenate",
    category="Text",
    description="Join two strings",
    icon="+",
    inputs=[PortDef("text_a", "string"), PortDef("text_b", "string"),
            PortDef("separator", "string", default=" ")],
    outputs=[PortDef("text", "string")],
))

register(NodeDef(
    type_id="text.split",
    title="Split Text",
    category="Text",
    description="Split a string on a delimiter",
    icon="÷",
    inputs=[PortDef("text", "string"),
            PortDef("delimiter", "string", default=",")],
    outputs=[PortDef("part_1", "string"), PortDef("part_2", "string")],
))

register(NodeDef(
    type_id="text.prompt_builder",
    title="Prompt Builder",
    category="Text",
    description="Assemble a rich diffusion prompt from components",
    icon="✍",
    inputs=[PortDef("subject", "string", required=False),
            PortDef("style", "string", required=False),
            PortDef("quality_tags", "string", required=False),
            PortDef("negative_tags", "string", required=False)],
    outputs=[PortDef("positive_prompt", "string"),
             PortDef("negative_prompt", "string")],
))

# ===========================================================================
# ── Data / Logic ──
# ===========================================================================
register(NodeDef(
    type_id="data.math",
    title="Math",
    category="Data",
    description="Simple arithmetic operation",
    icon="∑",
    inputs=[PortDef("a", "float"), PortDef("b", "float"),
            PortDef("operation", "string", default="add")],
    outputs=[PortDef("result", "float")],
))

register(NodeDef(
    type_id="data.clamp",
    title="Clamp",
    category="Data",
    description="Clamp a value between min and max",
    icon="[ ]",
    inputs=[PortDef("value", "float"),
            PortDef("min", "float", default=0.0),
            PortDef("max", "float", default=1.0)],
    outputs=[PortDef("value", "float")],
))

register(NodeDef(
    type_id="data.compare",
    title="Compare",
    category="Data",
    description="Compare two values, output bool",
    icon="≶",
    inputs=[PortDef("a", "any"), PortDef("b", "any"),
            PortDef("operation", "string", default="==")],
    outputs=[PortDef("result", "bool")],
))

# ===========================================================================
# ── Control Flow ──
# ===========================================================================
register(NodeDef(
    type_id="control.if_else",
    title="If / Else",
    category="Control",
    description="Route data based on a boolean condition",
    icon="?",
    inputs=[PortDef("condition", "bool"),
            PortDef("if_true", "any"), PortDef("if_false", "any")],
    outputs=[PortDef("result", "any")],
))

register(NodeDef(
    type_id="control.for_loop",
    title="For Loop",
    category="Control",
    description="Iterate n times and collect outputs",
    icon="↺",
    inputs=[PortDef("count", "int", default=5), PortDef("input", "any")],
    outputs=[PortDef("item", "any"), PortDef("index", "int")],
))

register(NodeDef(
    type_id="control.batch_split",
    title="Batch Split",
    category="Control",
    description="Split a batch tensor into individual items",
    icon="⊢",
    inputs=[PortDef("input", "any"), PortDef("batch_size", "int", default=4)],
    outputs=[PortDef("output_1", "any"), PortDef("output_2", "any"),
             PortDef("output_3", "any"), PortDef("output_4", "any")],
))

# ===========================================================================
# ── Output ──
# ===========================================================================
register(NodeDef(
    type_id="output.save_image",
    title="Save Image",
    category="Output",
    description="Save an image to disk",
    icon="💾",
    inputs=[PortDef("image", "image"),
            PortDef("filename_prefix", "string", default="output"),
            PortDef("format", "string", default="png")],
    outputs=[PortDef("path", "string")],
))

register(NodeDef(
    type_id="output.preview_image",
    title="Preview Image",
    category="Output",
    description="Display image in output panel",
    icon="🖥",
    inputs=[PortDef("image", "image")],
    outputs=[],
))

register(NodeDef(
    type_id="output.api_send",
    title="Send to API",
    category="Output",
    description="Send payload to Vaultwares Pipelines cloud API",
    icon="☁",
    inputs=[PortDef("payload", "any"),
            PortDef("endpoint", "string", default="/api/v1/run"),
            PortDef("api_key", "string", required=False)],
    outputs=[PortDef("response", "any"), PortDef("status_code", "int")],
))

register(NodeDef(
    type_id="output.print",
    title="Print / Log",
    category="Output",
    description="Print a value to the console log",
    icon="»",
    inputs=[PortDef("value", "any"),
            PortDef("label", "string", required=False, default="")],
    outputs=[],
))

# ===========================================================================
# ── Utility ──
# ===========================================================================
register(NodeDef(
    type_id="utility.note",
    title="Note",
    category="Utility",
    description="Sticky note / comment on canvas",
    icon="📝",
    inputs=[],
    outputs=[],
))

register(NodeDef(
    type_id="utility.reroute",
    title="Reroute",
    category="Utility",
    description="Clean up wires with a pass-through junction",
    icon="•",
    inputs=[PortDef("input", "any")],
    outputs=[PortDef("output", "any")],
))

register(NodeDef(
    type_id="utility.seed",
    title="Seed Generator",
    category="Utility",
    description="Generate a random or fixed seed",
    icon="🎲",
    inputs=[PortDef("fixed", "bool", default=False)],
    outputs=[PortDef("seed", "int")],
))
