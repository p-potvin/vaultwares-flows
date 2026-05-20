"""FlowWindow — the main application window for Vaultwares Flows."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QKeySequence, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app.canvas.minimap import Minimap
from app.canvas.node import FlowNode
from app.canvas.scene import FlowScene
from app.canvas.view import FlowView
from app.nodes.registry import definitions_by_category
from app.panels.node_library import NodeLibraryPanel
from app.panels.properties import PropertiesPanel
from app.theme.palette import ACCENT_PRIMARY, PANEL_BG, TEXT_MUTED, TEXT_SECONDARY


# ---------------------------------------------------------------------------
# Utility: icon-free toolbar button text
# ---------------------------------------------------------------------------
_TB_STYLE = (
    "QToolButton { background:transparent; border:none; color:#94A3B8;"
    "padding:5px 12px; border-radius:6px; font-size:12px; }"
    "QToolButton:hover { background:#1E2035; color:#E2E8F0; }"
    "QToolButton:pressed { background:#2D1B69; color:#E2E8F0; }"
    "QToolButton:checked { background:#2D1B69; color:#A78BFA; }"
)


class FlowWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Vaultwares Flows")
        self.setMinimumSize(1100, 700)
        self.resize(1440, 900)

        self._scene = FlowScene(self)
        self._view = FlowView(self._scene, self)

        self._lib_panel = NodeLibraryPanel(self)
        self._props_panel = PropertiesPanel(self)

        self._build_menu()
        self._build_toolbar()
        self._build_central()
        self._build_status_bar()
        self._connect_signals()
        self._add_welcome_nodes()

    # ── menu ───────────────────────────────────────────────────────────────
    def _build_menu(self) -> None:
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("File")
        file_menu.addAction("New Workflow", self._new_workflow, QKeySequence.StandardKey.New)
        file_menu.addAction("Open…", lambda: None, QKeySequence.StandardKey.Open)
        file_menu.addAction("Save", lambda: None, QKeySequence.StandardKey.Save)
        file_menu.addAction("Save As…", lambda: None, QKeySequence("Ctrl+Shift+S"))
        file_menu.addSeparator()
        file_menu.addAction("Export…", lambda: None)
        file_menu.addSeparator()
        file_menu.addAction("Quit", self.close, QKeySequence.StandardKey.Quit)

        # Edit
        edit_menu = mb.addMenu("Edit")
        edit_menu.addAction("Undo", lambda: None, QKeySequence.StandardKey.Undo)
        edit_menu.addAction("Redo", lambda: None, QKeySequence.StandardKey.Redo)
        edit_menu.addSeparator()
        edit_menu.addAction("Select All", self._select_all, QKeySequence.StandardKey.SelectAll)
        edit_menu.addAction("Delete Selected", self._delete_selected, Qt.Key.Key_Delete)

        # View
        view_menu = mb.addMenu("View")
        view_menu.addAction("Zoom In", self._view.zoom_in, QKeySequence.StandardKey.ZoomIn)
        view_menu.addAction("Zoom Out", self._view.zoom_out, QKeySequence.StandardKey.ZoomOut)
        view_menu.addAction("Reset Zoom", self._view.reset_zoom, QKeySequence("Ctrl+0"))
        view_menu.addAction("Fit All", self._view.fit_all, Qt.Key.Key_F)

        # Help
        help_menu = mb.addMenu("Help")
        help_menu.addAction("Documentation", lambda: None)
        help_menu.addAction("About Vaultwares Flows", self._show_about)

    # ── toolbar ────────────────────────────────────────────────────────────
    def _build_toolbar(self) -> None:
        tb = QToolBar("Main Toolbar", self)
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        tb.setStyleSheet(
            "QToolBar { background:#0D0F18; border-bottom:1px solid #1A1D2E; spacing:2px; padding:4px 6px; }"
        )
        self.addToolBar(tb)

        # ── Logo wordmark ──────────────────────────────────────────────
        logo = QLabel("  <b><span style='color:#7C3AED'>vault</span>"
                       "<span style='color:#E2E8F0'>wares</span> "
                       "<span style='color:#94A3B8'>flows</span></b>  ")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet("QLabel { font-size:15px; letter-spacing:-0.02em; }")
        tb.addWidget(logo)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("QFrame { color:#1E2035; margin:6px 4px; }")
        tb.addWidget(sep)

        # ── Tool buttons ───────────────────────────────────────────────
        self._act_select = QAction("✦  Select", self)
        self._act_select.setCheckable(True)
        self._act_select.setChecked(True)
        self._act_select.setStatusTip("Select tool (V)")
        self._act_select.setShortcut("V")
        tb.addAction(self._act_select)

        self._act_pan = QAction("✥  Pan", self)
        self._act_pan.setCheckable(True)
        self._act_pan.setStatusTip("Pan tool (H)")
        self._act_pan.setShortcut("H")
        tb.addAction(self._act_pan)

        tb.addSeparator()

        act_fit = QAction("⊡  Fit All", self)
        act_fit.setStatusTip("Fit all nodes in view (F)")
        act_fit.triggered.connect(self._view.fit_all)
        tb.addAction(act_fit)

        act_zoom_in = QAction("+  Zoom In", self)
        act_zoom_in.triggered.connect(self._view.zoom_in)
        tb.addAction(act_zoom_in)

        act_zoom_out = QAction("−  Zoom Out", self)
        act_zoom_out.triggered.connect(self._view.zoom_out)
        tb.addAction(act_zoom_out)

        tb.addSeparator()

        # ── Spacer ─────────────────────────────────────────────────────
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        # ── Cloud / Run buttons ────────────────────────────────────────
        act_run = QAction("▶  Run Workflow", self)
        act_run.setStatusTip("Execute the current workflow")
        act_run.triggered.connect(self._run_workflow)
        tb.addAction(act_run)

        act_cloud = QAction("☁  Connect to Cloud", self)
        act_cloud.setStatusTip("Connect to Vaultwares Pipelines API")
        tb.addAction(act_cloud)

        tb.addSeparator()

        act_settings = QAction("⚙  Settings", self)
        tb.addAction(act_settings)

        # Apply styles to each action's button
        for action in tb.actions():
            widget = tb.widgetForAction(action)
            if widget:
                widget.setStyleSheet(_TB_STYLE)

    # ── central layout ─────────────────────────────────────────────────────
    def _build_central(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background:#1A1D2E; }")

        splitter.addWidget(self._lib_panel)

        # Canvas container (view + floating minimap)
        canvas_container = QWidget()
        canvas_container.setStyleSheet("background:#0B0D14;")
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)
        canvas_layout.addWidget(self._view)

        splitter.addWidget(canvas_container)
        splitter.addWidget(self._props_panel)

        splitter.setSizes([240, 960, 260])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

        self.setCentralWidget(splitter)

        # Minimap — overlay on the view, bottom-right
        self._minimap = Minimap(self._view, self._view)
        self._view.resizeEvent = self._on_view_resize  # type: ignore[assignment]
        self._position_minimap()

    def _position_minimap(self) -> None:
        vw = self._view.width()
        vh = self._view.height()
        mw = self._minimap.width()
        mh = self._minimap.height()
        margin = 12
        self._minimap.move(vw - mw - margin, vh - mh - margin)

    def _on_view_resize(self, event) -> None:
        FlowView.resizeEvent(self._view, event)
        self._position_minimap()

    # ── status bar ─────────────────────────────────────────────────────────
    def _build_status_bar(self) -> None:
        sb = QStatusBar(self)
        sb.setStyleSheet(
            "QStatusBar { background:#0D0F18; border-top:1px solid #1A1D2E;"
            "color:#2D3260; font-size:11px; }"
        )
        self.setStatusBar(sb)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setStyleSheet("color:#2D3260; padding:0 8px;")
        sb.addPermanentWidget(self._zoom_label)

        self._node_count_label = QLabel("0 nodes")
        self._node_count_label.setStyleSheet("color:#2D3260; padding:0 8px;")
        sb.addPermanentWidget(self._node_count_label)

        sb.showMessage("Ready  ·  Hold Space to pan  ·  Scroll to zoom  ·  F to fit")

    # ── signals ────────────────────────────────────────────────────────────
    def _connect_signals(self) -> None:
        self._view.zoom_changed.connect(self._on_zoom_changed)
        self._scene.node_selected.connect(self._on_node_selected)
        self._scene.changed.connect(self._on_scene_changed)

    # ── slots ──────────────────────────────────────────────────────────────
    def _on_zoom_changed(self, zoom: float) -> None:
        self._zoom_label.setText(f"{zoom * 100:.0f}%")

    def _on_node_selected(self, node: FlowNode | None) -> None:
        self._props_panel.set_node(node)

    def _on_scene_changed(self, _regions=None) -> None:
        nodes = [i for i in self._scene.items() if isinstance(i, FlowNode)]
        self._node_count_label.setText(f"{len(nodes)} node{'s' if len(nodes) != 1 else ''}")

    # ── actions ────────────────────────────────────────────────────────────
    def _new_workflow(self) -> None:
        for item in list(self._scene.items()):
            self._scene.removeItem(item)
        self._scene._edges.clear()  # noqa: SLF001

    def _select_all(self) -> None:
        for item in self._scene.items():
            item.setSelected(True)

    def _delete_selected(self) -> None:
        from app.canvas.edge import FlowEdge as FE
        for item in list(self._scene.selectedItems()):
            if isinstance(item, FlowNode):
                self._scene.remove_node(item)
            elif isinstance(item, FE):
                self._scene._remove_edge(item)  # noqa: SLF001

    def _run_workflow(self) -> None:
        self.statusBar().showMessage("▶ Running workflow… (execution engine coming soon)", 4000)

    def _show_about(self) -> None:
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("About Vaultwares Flows")
        msg.setText(
            "<b>Vaultwares Flows v0.1.0</b><br><br>"
            "Visual node-based workflow builder with AI &amp; diffusion model support.<br><br>"
            "Built with PySide6 · Python 3.10+<br>"
            "<a href='https://github.com/p-potvin/vaultwares-flows' "
            "style='color:#7C3AED;'>github.com/p-potvin/vaultwares-flows</a>"
        )
        msg.setStyleSheet(
            "QMessageBox { background:#141520; } QLabel { color:#E2E8F0; font-size:13px; }"
            "QPushButton { background:#2D1B69; color:#E2E8F0; border:none; border-radius:6px;"
            "padding:6px 20px; } QPushButton:hover { background:#7C3AED; }"
        )
        msg.exec()

    # ── welcome graph ──────────────────────────────────────────────────────
    def _add_welcome_nodes(self) -> None:
        """Populate the canvas with an example Stable-Diffusion workflow."""
        from app.canvas.edge import FlowEdge
        from app.canvas.node import FlowNode
        from app.nodes.registry import get_node_definition

        def make(type_id: str, x: float, y: float) -> FlowNode | None:
            defn = get_node_definition(type_id)
            if defn is None:
                return None
            n = FlowNode(defn)
            n.setPos(QPointF(x, y))
            self._scene.addItem(n)
            return n

        def wire(src: FlowNode | None, out_i: int,
                 dst: FlowNode | None, in_i: int) -> None:
            if src is None or dst is None:
                return
            if out_i >= len(src._ports_out) or in_i >= len(dst._ports_in):  # noqa: SLF001
                return
            sp = src._ports_out[out_i]  # noqa: SLF001
            dp = dst._ports_in[in_i]    # noqa: SLF001
            edge = FlowEdge(sp, dp)
            self._scene.addItem(edge)
            self._scene._edges.append(edge)  # noqa: SLF001
            sp.add_edge(edge)
            dp.add_edge(edge)

        # ── nodes ──────────────────────────────────────────────────────
        n_ckpt        = make("ai.load_checkpoint",     -860, 100)
        n_pos_txt     = make("input.text",             -600,  60)
        n_neg_txt     = make("input.text",             -600, 220)
        n_empty_lat   = make("diffusion.empty_latent", -600, 380)
        n_clip_pos    = make("ai.clip_encode",         -340,  60)
        n_clip_neg    = make("ai.clip_encode",         -340, 220)
        n_ksampler    = make("diffusion.ksampler",      -60, 180)
        n_vae_decode  = make("diffusion.vae_decode",    320, 220)
        n_preview     = make("output.preview_image",    590, 220)

        # ── wires ──────────────────────────────────────────────────────
        # checkpoint → model inputs
        wire(n_ckpt, 0, n_ksampler, 0)    # model  → model
        wire(n_ckpt, 1, n_clip_pos, 0)    # clip   → clip  (positive encoder)
        wire(n_ckpt, 1, n_clip_neg, 0)    # clip   → clip  (negative encoder)
        wire(n_ckpt, 2, n_vae_decode, 0)  # vae    → vae

        # text prompts → CLIP encoders
        wire(n_pos_txt, 0, n_clip_pos, 1)  # text → text
        wire(n_neg_txt, 0, n_clip_neg, 1)  # text → text

        # CLIP → KSampler conditioning
        wire(n_clip_pos, 0, n_ksampler, 1)  # conditioning → positive
        wire(n_clip_neg, 0, n_ksampler, 2)  # conditioning → negative

        # empty latent → KSampler
        wire(n_empty_lat, 0, n_ksampler, 3)  # latent → latent_image

        # KSampler → VAE Decode → Preview
        wire(n_ksampler, 0, n_vae_decode, 1)  # latent → latent
        wire(n_vae_decode, 0, n_preview, 0)   # image  → image

        QTimer.singleShot(120, self._view.fit_all)
