"""FlowScene — QGraphicsScene that owns nodes, edges, and the dot-grid background."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QTransform
from PySide6.QtWidgets import QGraphicsScene

from app.canvas import edge as edge_module
from app.canvas.edge import DraftEdge, FlowEdge
from app.canvas.node import FlowNode, FlowPort, PortSide
from app.nodes.registry import NodeDef, get_node_definition
from app.theme.palette import CANVAS_BG, CANVAS_GRID_DOT, SELECTION_BORDER, SELECTION_FILL


class FlowScene(QGraphicsScene):
    """Main scene for the flow canvas."""

    node_selected = Signal(object)       # emits FlowNode or None
    connection_made = Signal(object, object)  # (source_port, target_port)

    # ── scene rectangle: very large but finite ─────────────────────────────
    SCENE_SIZE = 40_000

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        half = self.SCENE_SIZE / 2
        self.setSceneRect(-half, -half, self.SCENE_SIZE, self.SCENE_SIZE)
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)

        self._edges: list[FlowEdge] = []
        self._connecting_port: FlowPort | None = None
        self._draft_edge: DraftEdge | None = None

        # animation timer — drives all edge particle animations
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._tick_animation)
        self._anim_phase = 0.0
        self._anim_timer.start(30)  # ~33 fps

        self.selectionChanged.connect(self._on_selection_changed)

    # ── animation ──────────────────────────────────────────────────────────
    def _tick_animation(self) -> None:
        self._anim_phase = (self._anim_phase + 0.018) % 1.0
        edge_module.set_anim_phase(self._anim_phase)
        for e in self._edges:
            e.update()

    # ── background ─────────────────────────────────────────────────────────
    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        painter.fillRect(rect, CANVAS_BG)

        scale = painter.worldTransform().m11()
        if scale < 0.25:
            return  # skip grid when too zoomed out

        grid = 24.0
        dot_r = max(0.8, 1.1 / scale)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(CANVAS_GRID_DOT)

        x0 = math.floor(rect.left() / grid) * grid
        y0 = math.floor(rect.top() / grid) * grid
        x1 = rect.right() + grid
        y1 = rect.bottom() + grid

        # major grid lines every 5 cells — slightly brighter dot
        major_color = QColor(40, 45, 70)
        minor_color = CANVAS_GRID_DOT

        x = x0
        while x <= x1:
            y = y0
            while y <= y1:
                is_major = (round(x / grid) % 5 == 0) and (round(y / grid) % 5 == 0)
                painter.setBrush(major_color if is_major else minor_color)
                r = (dot_r * 1.6) if is_major else dot_r
                painter.drawEllipse(QPointF(x, y), r, r)
                y += grid
            x += grid

    # ── node creation ──────────────────────────────────────────────────────
    def create_node(self, type_id: str, pos: QPointF) -> FlowNode | None:
        defn = get_node_definition(type_id)
        if defn is None:
            return None
        node = FlowNode(defn)
        node.setPos(pos - QPointF(114, 20))  # centre on drop point
        self.addItem(node)
        return node

    def add_node_def(self, defn: NodeDef, pos: QPointF) -> FlowNode:
        node = FlowNode(defn)
        node.setPos(pos - QPointF(114, 20))
        self.addItem(node)
        return node

    def remove_node(self, node: FlowNode) -> None:
        # remove all connected edges first
        for port in node.all_ports:
            for edge in list(port.edges):
                self._remove_edge(edge)
        self.removeItem(node)

    # ── connection handling ────────────────────────────────────────────────
    def begin_connection(self, port: FlowPort) -> None:
        self._cancel_connection()
        self._connecting_port = port
        start = port.scene_center()
        self._draft_edge = DraftEdge(start)
        self.addItem(self._draft_edge)

    def _finish_connection(self, target: FlowPort) -> None:
        src = self._connecting_port
        if src is None:
            return
        if src.can_connect_to(target):
            # Determine which is output
            if src.side == PortSide.OUTPUT:
                out_port, in_port = src, target
            else:
                out_port, in_port = target, src

            # Remove existing connection on in_port (single input rule)
            for existing in list(in_port.edges):
                self._remove_edge(existing)

            edge = FlowEdge(out_port, in_port)
            self.addItem(edge)
            self._edges.append(edge)
            out_port.add_edge(edge)
            in_port.add_edge(edge)
            self.connection_made.emit(out_port, in_port)
        self._cancel_connection()

    def _cancel_connection(self) -> None:
        if self._draft_edge is not None:
            self.removeItem(self._draft_edge)
            self._draft_edge = None
        self._connecting_port = None

    def _remove_edge(self, edge: FlowEdge) -> None:
        edge.source_port.remove_edge(edge)
        edge.target_port.remove_edge(edge)
        if edge in self._edges:
            self._edges.remove(edge)
        self.removeItem(edge)

    # ── Qt event overrides ─────────────────────────────────────────────────
    def mouseMoveEvent(self, event) -> None:
        if self._connecting_port is not None and self._draft_edge is not None:
            self._draft_edge.set_end(event.scenePos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._connecting_port is not None:
            # Check whether we released on a port
            item = self.itemAt(event.scenePos(), QTransform())
            if isinstance(item, FlowPort) and item is not self._connecting_port:
                self._finish_connection(item)
            else:
                self._cancel_connection()
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            for item in list(self.selectedItems()):
                if isinstance(item, FlowNode):
                    self.remove_node(item)
                elif isinstance(item, FlowEdge):
                    self._remove_edge(item)
            event.accept()
            return
        if key == Qt.Key.Key_Escape:
            self._cancel_connection()
            event.accept()
            return
        super().keyPressEvent(event)

    # ── selection ──────────────────────────────────────────────────────────
    def _on_selection_changed(self) -> None:
        selected_nodes = [i for i in self.selectedItems() if isinstance(i, FlowNode)]
        self.node_selected.emit(selected_nodes[0] if selected_nodes else None)
