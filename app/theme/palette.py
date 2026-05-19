"""Vaultwares Flows – colour palette and QSS stylesheet."""

from __future__ import annotations

from PySide6.QtGui import QColor

# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------
CANVAS_BG = QColor("#0B0D14")
CANVAS_GRID_DOT = QColor("#1C1F31")

# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------
NODE_BG = QColor("#141520")
NODE_BG_HOVER = QColor("#191C2A")
NODE_BORDER = QColor("#252845")
NODE_BORDER_SELECTED = QColor("#7C3AED")
NODE_TITLE = QColor("#E2E8F0")
NODE_LABEL = QColor("#8B95B0")

# Header gradients per category  (start, stop)
HEADER_COLORS: dict[str, tuple[str, str]] = {
    "ai":          ("#3D1A78", "#1A3A6B"),
    "diffusion":   ("#4A1275", "#1E1A6B"),
    "image":       ("#1A4731", "#163A6B"),
    "text":        ("#163A6B", "#1E40AF"),
    "data":        ("#4A2800", "#78350F"),
    "output":      ("#4A1010", "#7F1D1D"),
    "control":     ("#1F2937", "#374151"),
    "input":       ("#1A3A4A", "#1A4A6B"),
    "model":       ("#2D1B5E", "#1A3360"),
    "mask":        ("#2D1B5E", "#1A3A6B"),
    "utility":     ("#1A2535", "#243040"),
}

# ---------------------------------------------------------------------------
# Ports
# ---------------------------------------------------------------------------
PORT_TYPE_COLORS: dict[str, str] = {
    "float":        "#A78BFA",
    "int":          "#60A5FA",
    "string":       "#34D399",
    "bool":         "#F87171",
    "image":        "#F472B6",
    "model":        "#818CF8",
    "latent":       "#FB923C",
    "mask":         "#C084FC",
    "conditioning": "#FBBF24",
    "audio":        "#38BDF8",
    "video":        "#E879F9",
    "any":          "#94A3B8",
}

# ---------------------------------------------------------------------------
# Edges
# ---------------------------------------------------------------------------
EDGE_COLOR = QColor("#7C3AED")
EDGE_GLOW = QColor(124, 58, 237, 60)
EDGE_SELECTED = QColor("#A855F7")
EDGE_DRAFT = QColor("#64748B")

# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------
SELECTION_FILL = QColor(124, 58, 237, 35)
SELECTION_BORDER = QColor("#7C3AED")

# ---------------------------------------------------------------------------
# Panels / chrome
# ---------------------------------------------------------------------------
PANEL_BG = QColor("#0F1117")
PANEL_BORDER = QColor("#1E2035")
TOOLBAR_BG = QColor("#0D0F18")
TOOLBAR_BORDER = QColor("#1A1D2E")
SIDEBAR_ITEM_HOVER = QColor("#1E2035")
SIDEBAR_ITEM_SELECTED = QColor("#2D1B69")
SIDEBAR_CATEGORY_BG = QColor("#11131E")

# ---------------------------------------------------------------------------
# Text / status
# ---------------------------------------------------------------------------
TEXT_PRIMARY = QColor("#E2E8F0")
TEXT_SECONDARY = QColor("#94A3B8")
TEXT_MUTED = QColor("#475569")
ACCENT_SUCCESS = QColor("#10B981")
ACCENT_WARNING = QColor("#F59E0B")
ACCENT_ERROR = QColor("#EF4444")
ACCENT_INFO = QColor("#3B82F6")
ACCENT_PRIMARY = QColor("#7C3AED")

# ---------------------------------------------------------------------------
# Global QSS
# ---------------------------------------------------------------------------
APP_STYLESHEET = """
/* ── Global ── */
QWidget {
    background-color: #0F1117;
    color: #E2E8F0;
    font-family: "Inter", "Segoe UI", "SF Pro Display", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0B0D14;
}

/* ── Scrollbars ── */
QScrollBar:vertical, QScrollBar:horizontal {
    background: #0F1117;
    width: 6px;
    height: 6px;
    margin: 0;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #2D3260;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background: #7C3AED;
}
QScrollBar::add-line, QScrollBar::sub-line { background: none; border: none; }
QScrollBar::add-page, QScrollBar::sub-page { background: none; }

/* ── Toolbar ── */
QToolBar {
    background-color: #0D0F18;
    border-bottom: 1px solid #1A1D2E;
    spacing: 4px;
    padding: 4px 8px;
}
QToolBar::separator {
    background: #1A1D2E;
    width: 1px;
    margin: 4px 4px;
}
QToolButton {
    background: transparent;
    border: none;
    color: #94A3B8;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 12px;
}
QToolButton:hover  { background: #1E2035; color: #E2E8F0; }
QToolButton:pressed { background: #2D1B69; color: #E2E8F0; }
QToolButton:checked { background: #2D1B69; color: #A78BFA; }

/* ── MenuBar ── */
QMenuBar {
    background-color: #0D0F18;
    color: #94A3B8;
    border-bottom: 1px solid #1A1D2E;
    padding: 2px;
}
QMenuBar::item { padding: 4px 10px; border-radius: 4px; }
QMenuBar::item:selected { background: #1E2035; color: #E2E8F0; }
QMenu {
    background-color: #141520;
    border: 1px solid #252845;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item { padding: 6px 24px; border-radius: 4px; }
QMenu::item:selected { background: #2D1B69; color: #E2E8F0; }
QMenu::separator { background: #252845; height: 1px; margin: 4px 8px; }

/* ── LineEdit ── */
QLineEdit {
    background: #0B0D14;
    border: 1px solid #252845;
    border-radius: 6px;
    color: #E2E8F0;
    padding: 5px 10px;
    selection-background-color: #7C3AED;
}
QLineEdit:focus { border-color: #7C3AED; }
QLineEdit::placeholder { color: #475569; }

/* ── TreeWidget / ListWidget ── */
QTreeWidget, QListWidget {
    background: transparent;
    border: none;
    outline: none;
}
QTreeWidget::item, QListWidget::item {
    padding: 5px 8px;
    border-radius: 5px;
}
QTreeWidget::item:hover, QListWidget::item:hover { background: #1E2035; }
QTreeWidget::item:selected, QListWidget::item:selected {
    background: #2D1B69;
    color: #E2E8F0;
}
QTreeWidget::branch { background: transparent; }
QHeaderView::section {
    background: #0F1117;
    border: none;
    color: #475569;
    padding: 4px 8px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Splitter ── */
QSplitter::handle { background: #1A1D2E; }
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical   { height: 1px; }

/* ── Spin / Combo ── */
QDoubleSpinBox, QSpinBox, QComboBox {
    background: #0B0D14;
    border: 1px solid #252845;
    border-radius: 6px;
    color: #E2E8F0;
    padding: 4px 8px;
    min-height: 26px;
}
QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus { border-color: #7C3AED; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background: #141520;
    border: 1px solid #252845;
    selection-background-color: #2D1B69;
    border-radius: 6px;
}

/* ── PushButton ── */
QPushButton {
    background: #1E2035;
    border: 1px solid #252845;
    border-radius: 6px;
    color: #E2E8F0;
    padding: 5px 14px;
}
QPushButton:hover  { background: #2D3260; border-color: #7C3AED; }
QPushButton:pressed { background: #2D1B69; }
QPushButton[primary="true"] {
    background: #7C3AED;
    border-color: #7C3AED;
    color: #fff;
    font-weight: 600;
}
QPushButton[primary="true"]:hover { background: #6D28D9; }

/* ── StatusBar ── */
QStatusBar {
    background: #0D0F18;
    border-top: 1px solid #1A1D2E;
    color: #475569;
    font-size: 11px;
    padding: 2px 8px;
}
QStatusBar::item { border: none; }

/* ── Label ── */
QLabel { background: transparent; }

/* ── GroupBox ── */
QGroupBox {
    border: 1px solid #252845;
    border-radius: 6px;
    margin-top: 16px;
    padding-top: 8px;
    color: #475569;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 8px;
}
"""
