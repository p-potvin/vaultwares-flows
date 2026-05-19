"""FlowPort and FlowNode — the visual building blocks of the canvas."""

from __future__ import annotations

import math
from enum import Enum
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QGraphicsItem, QGraphicsObject, QStyleOptionGraphicsItem

from app.nodes.registry import NodeDef, PortDef
from app.theme.palette import (
    HEADER_COLORS,
    NODE_BG,
    NODE_BORDER,
    NODE_BORDER_SELECTED,
    NODE_LABEL,
    NODE_TITLE,
    PORT_TYPE_COLORS,
)

if TYPE_CHECKING:
    from app.canvas.edge import FlowEdge


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PORT_RADIUS = 6.0
_TITLE_FONT = QFont("Inter", 11)
_TITLE_FONT.setWeight(QFont.Weight.Medium)
_LABEL_FONT = QFont("Inter", 9)
_NODE_RADIUS = 10.0
_HEADER_HEIGHT = 42.0
_PORT_ROW_HEIGHT = 26.0
_PORT_BODY_PAD = 10.0
_NODE_WIDTH = 228.0
_SHADOW_OFFSET = 5.0
_SHADOW_BLUR = 18.0


class PortSide(Enum):
    INPUT = "input"
    OUTPUT = "output"


# ---------------------------------------------------------------------------
# FlowPort
# ---------------------------------------------------------------------------
class FlowPort(QGraphicsItem):
    """A circular connector on the edge of a node."""

    def __init__(self, port_def: PortDef, side: PortSide, parent: "FlowNode") -> None:
        super().__init__(parent)
        self.port_def = port_def
        self.side = side
        self._edges: list[FlowEdge] = []
        self._hovered = False

        self.setAcceptHoverEvents(True)
        self.setZValue(3)

        color_hex = PORT_TYPE_COLORS.get(port_def.port_type, "#94A3B8")
        self._color = QColor(color_hex)

    # ── edge management ────────────────────────────────────────────────
    @property
    def edges(self) -> list[FlowEdge]:
        return self._edges

    def add_edge(self, edge: FlowEdge) -> None:
        if edge not in self._edges:
            self._edges.append(edge)
        self.update()

    def remove_edge(self, edge: FlowEdge) -> None:
        if edge in self._edges:
            self._edges.remove(edge)
        self.update()

    def is_connected(self) -> bool:
        return bool(self._edges)

    # ── geometry ───────────────────────────────────────────────────────
    def scene_center(self) -> QPointF:
        return self.mapToScene(QPointF(0.0, 0.0))

    def can_connect_to(self, other: "FlowPort") -> bool:
        if self.side == other.side:
            return False
        if self.parentItem() is other.parentItem():
            return False
        t1, t2 = self.port_def.port_type, other.port_def.port_type
        if t1 == "any" or t2 == "any":
            return True
        return t1 == t2

    # ── Qt overrides ───────────────────────────────────────────────────
    def boundingRect(self) -> QRectF:
        r = PORT_RADIUS + 6
        return QRectF(-r, -r, r * 2, r * 2)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget=None,
    ) -> None:
        c = self._color
        connected = bool(self._edges)

        if self._hovered:
            # outer glow ring
            glow = QRadialGradient(0.0, 0.0, PORT_RADIUS * 2.8)
            glow.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), 90))
            glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(QRectF(-PORT_RADIUS * 2.8, -PORT_RADIUS * 2.8,
                                       PORT_RADIUS * 5.6, PORT_RADIUS * 5.6))

        # port circle
        painter.setPen(QPen(c, 2.0))
        if connected or self._hovered:
            painter.setBrush(QBrush(c))
        else:
            painter.setBrush(QBrush(NODE_BG))
        painter.drawEllipse(QRectF(-PORT_RADIUS, -PORT_RADIUS,
                                   PORT_RADIUS * 2, PORT_RADIUS * 2))

    def hoverEnterEvent(self, event) -> None:
        self._hovered = True
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.update()

    def hoverLeaveEvent(self, event) -> None:
        self._hovered = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            scene = self.scene()
            if scene is not None:
                scene.begin_connection(self)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        # Let the scene handle finalisation via its own mouseReleaseEvent
        event.accept()


# ---------------------------------------------------------------------------
# FlowNode
# ---------------------------------------------------------------------------
class FlowNode(QGraphicsObject):
    """A single node on the flow canvas."""

    def __init__(self, definition: NodeDef, parent=None) -> None:
        super().__init__(parent)
        self._def = definition
        self._ports_in: list[FlowPort] = []
        self._ports_out: list[FlowPort] = []
        self._collapsed = False

        self._setup_flags()
        self._calc_size()
        self._build_ports()

    # ── setup ──────────────────────────────────────────────────────────
    def _setup_flags(self) -> None:
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.setZValue(1)

    def _calc_size(self) -> None:
        n_ports = max(len(self._def.inputs), len(self._def.outputs), 1)
        body_h = n_ports * _PORT_ROW_HEIGHT + _PORT_BODY_PAD * 2
        self._width = _NODE_WIDTH
        self._height = _HEADER_HEIGHT + body_h

    def _build_ports(self) -> None:
        y_start = _HEADER_HEIGHT + _PORT_BODY_PAD + _PORT_ROW_HEIGHT / 2

        for i, pd in enumerate(self._def.inputs):
            p = FlowPort(pd, PortSide.INPUT, self)
            p.setPos(0.0, y_start + i * _PORT_ROW_HEIGHT)
            self._ports_in.append(p)

        for i, pd in enumerate(self._def.outputs):
            p = FlowPort(pd, PortSide.OUTPUT, self)
            p.setPos(self._width, y_start + i * _PORT_ROW_HEIGHT)
            self._ports_out.append(p)

    # ── public API ─────────────────────────────────────────────────────
    @property
    def definition(self) -> NodeDef:
        return self._def

    @property
    def all_ports(self) -> list[FlowPort]:
        return self._ports_in + self._ports_out

    # ── geometry ───────────────────────────────────────────────────────
    def boundingRect(self) -> QRectF:
        extra = PORT_RADIUS + 2
        return QRectF(-extra, -_SHADOW_OFFSET,
                      self._width + extra * 2,
                      self._height + _SHADOW_OFFSET + 4)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self._width, self._height),
                            _NODE_RADIUS, _NODE_RADIUS)
        return path

    # ── paint ──────────────────────────────────────────────────────────
    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget=None,
    ) -> None:
        rect = QRectF(0.0, 0.0, self._width, self._height)
        selected = self.isSelected()

        # ── drop shadow ────────────────────────────────────────────────
        shadow_rect = rect.translated(0, _SHADOW_OFFSET)
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(4):
            alpha = int(55 - i * 12)
            expand = i * 2.5
            painter.setBrush(QColor(0, 0, 0, alpha))
            painter.drawRoundedRect(
                shadow_rect.adjusted(-expand, -expand, expand, expand),
                _NODE_RADIUS + expand * 0.3, _NODE_RADIUS + expand * 0.3,
            )

        # ── selection glow ─────────────────────────────────────────────
        if selected:
            for i in range(4):
                alpha = int(80 - i * 18)
                expand = i * 3.0
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(124, 58, 237, alpha))
                painter.drawRoundedRect(
                    rect.adjusted(-expand, -expand, expand, expand),
                    _NODE_RADIUS + expand * 0.3, _NODE_RADIUS + expand * 0.3,
                )

        # ── body ───────────────────────────────────────────────────────
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(NODE_BG))
        painter.drawRoundedRect(rect, _NODE_RADIUS, _NODE_RADIUS)

        # ── header gradient ────────────────────────────────────────────
        cat = self._def.header_category
        gradient_start, gradient_end = HEADER_COLORS.get(cat, ("#1F2937", "#374151"))
        grad = QLinearGradient(0.0, 0.0, self._width, 0.0)
        grad.setColorAt(0.0, QColor(gradient_start))
        grad.setColorAt(1.0, QColor(gradient_end))

        header_rect = QRectF(0.0, 0.0, self._width, _HEADER_HEIGHT)
        clip = QPainterPath()
        clip.addRoundedRect(rect, _NODE_RADIUS, _NODE_RADIUS)
        painter.setClipPath(clip)
        painter.setBrush(QBrush(grad))
        painter.drawRect(header_rect)
        painter.setClipping(False)

        # thin divider below header
        painter.setPen(QPen(QColor(255, 255, 255, 12), 1.0))
        painter.drawLine(
            QPointF(0.0, _HEADER_HEIGHT),
            QPointF(self._width, _HEADER_HEIGHT),
        )

        # ── border ─────────────────────────────────────────────────────
        border_color = NODE_BORDER_SELECTED if selected else NODE_BORDER
        border_width = 2.0 if selected else 1.0
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(border_color, border_width))
        painter.drawRoundedRect(rect, _NODE_RADIUS, _NODE_RADIUS)

        # ── icon + title ───────────────────────────────────────────────
        painter.setPen(QPen(NODE_TITLE))
        painter.setFont(_TITLE_FONT)
        title_rect = QRectF(14.0, 0.0, self._width - 28.0, _HEADER_HEIGHT)
        icon_and_title = f"{self._def.icon}  {self._def.title}"
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         icon_and_title)

        # ── port labels ────────────────────────────────────────────────
        painter.setFont(_LABEL_FONT)
        y_start = _HEADER_HEIGHT + _PORT_BODY_PAD + _PORT_ROW_HEIGHT / 2

        for i, pd in enumerate(self._def.inputs):
            cy = y_start + i * _PORT_ROW_HEIGHT
            label_rect = QRectF(14.0, cy - _PORT_ROW_HEIGHT / 2,
                                self._width / 2 - 20, _PORT_ROW_HEIGHT)
            port_color = PORT_TYPE_COLORS.get(pd.port_type, "#94A3B8")
            painter.setPen(QPen(QColor(port_color).lighter(130)))
            painter.drawText(label_rect,
                             Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                             pd.name)

        for i, pd in enumerate(self._def.outputs):
            cy = y_start + i * _PORT_ROW_HEIGHT
            label_rect = QRectF(self._width / 2 + 6.0, cy - _PORT_ROW_HEIGHT / 2,
                                self._width / 2 - 20, _PORT_ROW_HEIGHT)
            port_color = PORT_TYPE_COLORS.get(pd.port_type, "#94A3B8")
            painter.setPen(QPen(QColor(port_color).lighter(130)))
            painter.drawText(label_rect,
                             Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                             pd.name)

    # ── item change ────────────────────────────────────────────────────
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for port in self.all_ports:
                for edge in port.edges:
                    edge.update_path()
        return super().itemChange(change, value)

    # ── context menu ───────────────────────────────────────────────────
    def contextMenuEvent(self, event) -> None:
        from PySide6.QtWidgets import QMenu
        menu = QMenu()
        menu.setStyleSheet(
            "QMenu { background:#141520; border:1px solid #252845; border-radius:8px; padding:4px; }"
            "QMenu::item { padding:6px 24px; border-radius:4px; color:#E2E8F0; }"
            "QMenu::item:selected { background:#2D1B69; }"
        )
        dup_action = menu.addAction("⧉  Duplicate")
        del_action = menu.addAction("✕  Delete")
        menu.addSeparator()
        menu.addAction(f"📋  {self._def.title}")

        chosen = menu.exec(event.screenPos())
        if chosen == del_action:
            scene = self.scene()
            if scene:
                scene.remove_node(self)
        elif chosen == dup_action:
            scene = self.scene()
            if scene:
                new_node = FlowNode(self._def)
                new_node.setPos(self.pos() + QPointF(30, 30))
                scene.addItem(new_node)
