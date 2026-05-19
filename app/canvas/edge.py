"""FlowEdge (permanent bezier connection) and DraftEdge (in-progress wire)."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import (
    QBrush,
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QStyleOptionGraphicsItem

from app.theme.palette import EDGE_COLOR, EDGE_DRAFT, EDGE_GLOW, EDGE_SELECTED, PORT_TYPE_COLORS

if TYPE_CHECKING:
    from app.canvas.node import FlowPort

# Shared animation phase counter updated by FlowScene
_ANIM_PHASE: float = 0.0


def set_anim_phase(phase: float) -> None:
    global _ANIM_PHASE
    _ANIM_PHASE = phase


def _bezier_control_points(
    src: QPointF, dst: QPointF
) -> tuple[QPointF, QPointF]:
    dx = abs(dst.x() - src.x())
    dx = max(dx * 0.55, 60.0)
    return QPointF(src.x() + dx, src.y()), QPointF(dst.x() - dx, dst.y())


def _make_path(src: QPointF, dst: QPointF) -> QPainterPath:
    path = QPainterPath()
    path.moveTo(src)
    cp1, cp2 = _bezier_control_points(src, dst)
    path.cubicTo(cp1, cp2, dst)
    return path


# ---------------------------------------------------------------------------
# FlowEdge
# ---------------------------------------------------------------------------
class FlowEdge(QGraphicsPathItem):
    """A permanent animated bezier wire between two ports."""

    def __init__(
        self,
        source: FlowPort,
        target: FlowPort,
        parent: QGraphicsItem | None = None,
    ) -> None:
        super().__init__(parent)
        self.source_port = source
        self.target_port = target

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(0)

        # Derive color from source port type
        color_hex = PORT_TYPE_COLORS.get(source.port_def.port_type, "#7C3AED")
        self._color = QColor(color_hex)
        self._glow = QColor(self._color.red(), self._color.green(),
                            self._color.blue(), 55)

        self.update_path()

    # ── geometry ───────────────────────────────────────────────────────
    def update_path(self) -> None:
        src = self.source_port.scene_center()
        tgt = self.target_port.scene_center()
        self.setPath(_make_path(src, tgt))

    def boundingRect(self) -> QRectF:
        return self.path().boundingRect().adjusted(-20, -20, 20, 20)

    # ── paint ──────────────────────────────────────────────────────────
    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget=None,
    ) -> None:
        path = self.path()
        selected = self.isSelected()

        # outer glow
        glow_pen = QPen(self._glow, 10.0)
        glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(glow_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # main wire
        wire_color = EDGE_SELECTED if selected else self._color
        wire_width = 3.0 if selected else 2.0
        pen = QPen(wire_color, wire_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)

        # animated flow particles
        length = path.length()
        if length < 1:
            return
        num_dots = max(2, int(length / 70))
        phase = _ANIM_PHASE

        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(num_dots):
            t = ((i / num_dots) + phase) % 1.0
            pt = path.pointAtPercent(t)
            # fade in/out near ends
            fade = math.sin(t * math.pi)
            alpha = int(220 * fade)
            dot_color = QColor(
                self._color.red(), self._color.green(),
                self._color.blue(), alpha
            )
            painter.setBrush(QBrush(dot_color))
            r = 2.8 * fade + 1.0
            painter.drawEllipse(pt, r, r)


# ---------------------------------------------------------------------------
# DraftEdge
# ---------------------------------------------------------------------------
class DraftEdge(QGraphicsItem):
    """Temporary dashed wire shown while the user is dragging a connection."""

    def __init__(self, start: QPointF, parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent)
        self._start = start
        self._end = start
        self.setZValue(100)

    def set_end(self, pos: QPointF) -> None:
        self._end = pos
        # Force a repaint of the whole scene region covering this item
        scene = self.scene()
        if scene:
            scene.invalidate(self.sceneBoundingRect())

    def boundingRect(self) -> QRectF:
        xs = min(self._start.x(), self._end.x())
        ys = min(self._start.y(), self._end.y())
        w = abs(self._end.x() - self._start.x())
        h = abs(self._end.y() - self._start.y())
        return QRectF(xs - 30, ys - 30, w + 60, h + 60)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget=None,
    ) -> None:
        path = _make_path(self._start, self._end)

        pen = QPen(EDGE_DRAFT, 2.0, Qt.PenStyle.DashLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setDashPattern([5.0, 4.0])
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # endpoint dot
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(EDGE_DRAFT))
        painter.drawEllipse(self._end, 4.5, 4.5)
