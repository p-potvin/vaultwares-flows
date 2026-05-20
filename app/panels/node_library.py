"""Node library panel — searchable, categorised, drag-to-canvas sidebar."""

from __future__ import annotations

from PySide6.QtCore import QMimeData, QPoint, Qt
from PySide6.QtGui import QColor, QDrag, QFont, QPalette
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.nodes.registry import NodeDef, definitions_by_category
from app.theme.palette import (
    HEADER_COLORS,
    PANEL_BG,
    PANEL_BORDER,
    PORT_TYPE_COLORS,
    SIDEBAR_CATEGORY_BG,
    SIDEBAR_ITEM_HOVER,
    SIDEBAR_ITEM_SELECTED,
    TEXT_MUTED,
    TEXT_SECONDARY,
)


class NodeLibraryPanel(QWidget):
    """Left sidebar listing all available node types, with search and drag support."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(220)
        self.setMaximumWidth(300)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._build_ui()
        self._populate()

    # ── UI construction ────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QLabel("  Node Library")
        header.setFixedHeight(42)
        header.setStyleSheet(
            "QLabel { background:#0D0F18; color:#E2E8F0; font-size:13px;"
            "font-weight:600; border-bottom:1px solid #1A1D2E; padding-left:8px; }"
        )
        layout.addWidget(header)

        # Search
        self._search = QLineEdit()
        self._search.setPlaceholderText("  🔍  Search nodes…")
        self._search.setFixedHeight(36)
        self._search.setStyleSheet(
            "QLineEdit { background:#0B0D14; border:none; border-bottom:1px solid #1A1D2E;"
            "color:#E2E8F0; padding:0 12px; font-size:12px; }"
            "QLineEdit:focus { border-bottom:1px solid #7C3AED; }"
        )
        self._search.textChanged.connect(self._filter)
        layout.addWidget(self._search)

        # Tree
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(12)
        self._tree.setStyleSheet(
            "QTreeWidget { background:#0F1117; border:none; }"
            "QTreeWidget::item { padding:4px 6px; border-radius:4px; }"
            "QTreeWidget::item:hover { background:#1E2035; }"
            "QTreeWidget::item:selected { background:#2D1B69; color:#E2E8F0; }"
            "QTreeWidget::branch:has-children:!has-siblings:closed,"
            "QTreeWidget::branch:closed:has-children:has-siblings {"
            "  border-image:none; image:none; }"
        )
        self._tree.setDragEnabled(True)
        self._tree.setDragDropMode(QTreeWidget.DragDropMode.DragOnly)
        self._tree.startDrag = self._start_drag  # type: ignore[assignment]
        layout.addWidget(self._tree)

        # Footer hint
        hint = QLabel("  Drag nodes onto the canvas")
        hint.setFixedHeight(28)
        hint.setStyleSheet(
            "QLabel { background:#0D0F18; color:#2D3260; font-size:10px;"
            "border-top:1px solid #1A1D2E; padding-left:8px; }"
        )
        layout.addWidget(hint)

    # ── populate ───────────────────────────────────────────────────────────
    def _populate(self, filter_text: str = "") -> None:
        self._tree.clear()
        ft = filter_text.lower()

        cat_font = QFont("Inter", 10)
        cat_font.setWeight(QFont.Weight.Bold)
        node_font = QFont("Inter", 11)

        for category, defs in definitions_by_category().items():
            matches = [
                d for d in defs
                if ft in d.title.lower() or ft in d.description.lower()
            ] if ft else defs

            if not matches:
                continue

            # Category row
            cat_item = QTreeWidgetItem([f"  {category.upper()}"])
            cat_item.setFont(0, cat_font)
            cat_item.setForeground(0, QColor(TEXT_MUTED))
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            cat_item.setBackground(0, QColor(SIDEBAR_CATEGORY_BG))
            self._tree.addTopLevelItem(cat_item)

            for defn in matches:
                category_color, _ = HEADER_COLORS.get(defn.header_category, ("#4B5563", "#374151"))
                node_item = QTreeWidgetItem([f"  {defn.icon}  {defn.title}"])
                node_item.setFont(0, node_font)
                node_item.setForeground(0, QColor("#C4CBE0"))
                node_item.setToolTip(0, defn.description)
                node_item.setData(0, Qt.ItemDataRole.UserRole, defn.type_id)
                cat_item.addChild(node_item)

            cat_item.setExpanded(True)

    def _filter(self, text: str) -> None:
        self._populate(text)

    # ── drag ───────────────────────────────────────────────────────────────
    def _start_drag(self, actions) -> None:
        item = self._tree.currentItem()
        if item is None:
            return
        type_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not type_id:
            return

        mime = QMimeData()
        mime.setText(type_id)

        drag = QDrag(self._tree)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.CopyAction)
