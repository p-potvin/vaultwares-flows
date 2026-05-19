"""Properties panel — shows and edits input values of the selected node."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.canvas.node import FlowNode
from app.nodes.registry import PortDef
from app.theme.palette import HEADER_COLORS, NODE_BG, PANEL_BG, TEXT_PRIMARY, TEXT_SECONDARY


class PropertiesPanel(QWidget):
    """Right sidebar that displays and edits properties of the selected node."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(240)
        self.setMaximumWidth(340)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._current_node: FlowNode | None = None
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        self._header = QLabel("  Properties")
        self._header.setFixedHeight(42)
        self._header.setStyleSheet(
            "QLabel { background:#0D0F18; color:#E2E8F0; font-size:13px;"
            "font-weight:600; border-bottom:1px solid #1A1D2E; padding-left:8px; }"
        )
        layout.addWidget(self._header)

        # Scroll area for form fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background:#0F1117; border:none; }")
        layout.addWidget(scroll)

        self._content = QWidget()
        self._content.setStyleSheet("background:#0F1117;")
        scroll.setWidget(self._content)

        self._form_layout = QVBoxLayout(self._content)
        self._form_layout.setContentsMargins(12, 12, 12, 12)
        self._form_layout.setSpacing(6)
        self._form_layout.addStretch()

        self._show_empty()

    # ── public API ─────────────────────────────────────────────────────────
    def set_node(self, node: FlowNode | None) -> None:
        self._current_node = node
        self._rebuild()

    # ── internal ───────────────────────────────────────────────────────────
    def _clear_form(self) -> None:
        while self._form_layout.count():
            item = self._form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_empty(self) -> None:
        self._clear_form()
        hint = QLabel("Select a node to\ninspect its properties")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet(
            "QLabel { color:#2D3260; font-size:12px; padding:40px 20px; }"
        )
        self._form_layout.addWidget(hint)
        self._form_layout.addStretch()

    def _rebuild(self) -> None:
        self._clear_form()
        node = self._current_node
        if node is None:
            self._show_empty()
            return

        defn = node.definition
        cat = defn.header_category
        gradient_start, gradient_end = HEADER_COLORS.get(cat, ("#1F2937", "#374151"))

        # Node identity card
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {gradient_start}, stop:1 {gradient_end});"
            f"border-radius:8px; border:1px solid #252845; }}"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(2)

        icon_title = QLabel(f"{defn.icon}  {defn.title}")
        icon_title.setStyleSheet("color:#E2E8F0; font-size:14px; font-weight:600; background:transparent;")
        card_layout.addWidget(icon_title)

        category_lbl = QLabel(defn.category)
        category_lbl.setStyleSheet("color:rgba(255,255,255,0.55); font-size:10px; background:transparent;")
        card_layout.addWidget(category_lbl)

        if defn.description:
            desc_lbl = QLabel(defn.description)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("color:rgba(255,255,255,0.45); font-size:10px; background:transparent; margin-top:4px;")
            card_layout.addWidget(desc_lbl)

        self._form_layout.addWidget(card)

        # Inputs section
        if defn.inputs:
            sep = self._make_section_label("INPUTS")
            self._form_layout.addWidget(sep)
            form = QFormLayout()
            form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            form.setHorizontalSpacing(10)
            form.setVerticalSpacing(8)
            for pd in defn.inputs:
                label = QLabel(pd.name)
                label.setStyleSheet("color:#8B95B0; font-size:11px;")
                widget = self._make_field(pd)
                form.addRow(label, widget)
            self._form_layout.addLayout(form)

        # Outputs section (read-only labels)
        if defn.outputs:
            sep = self._make_section_label("OUTPUTS")
            self._form_layout.addWidget(sep)
            for pd in defn.outputs:
                row = QLabel(f"  → {pd.name}  ({pd.port_type})")
                row.setStyleSheet("color:#475569; font-size:11px; padding:2px 0;")
                self._form_layout.addWidget(row)

        self._form_layout.addStretch()

    def _make_section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "QLabel { color:#2D3260; font-size:10px; font-weight:700;"
            "letter-spacing:0.08em; padding:8px 0 2px 0; }"
        )
        return lbl

    def _make_field(self, pd: PortDef) -> QWidget:
        t = pd.port_type
        default = pd.default

        if t == "bool":
            w = QCheckBox()
            w.setChecked(bool(default))
            return w

        if t == "int":
            w = QSpinBox()
            w.setRange(-999_999, 999_999)
            w.setValue(int(default) if default is not None else 0)
            return w

        if t == "float":
            w = QDoubleSpinBox()
            w.setRange(-999_999.0, 999_999.0)
            w.setDecimals(3)
            w.setSingleStep(0.01)
            w.setValue(float(default) if default is not None else 0.0)
            return w

        if t == "string":
            val = str(default) if default is not None else ""
            if "\n" in val or len(val) > 60:
                w = QTextEdit()
                w.setPlainText(val)
                w.setFixedHeight(72)
                return w
            w = QLineEdit()
            w.setText(val)
            return w

        # fallback
        w = QLineEdit()
        w.setText(str(default) if default is not None else "")
        w.setStyleSheet("color:#8B95B0; font-style:italic;")
        return w
