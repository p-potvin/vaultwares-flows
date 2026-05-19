"""Minimap — small overview overlay positioned in the bottom-right corner."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QPointF, QRectF, QTimer, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsView, QWidget

from app.theme.palette import ACCENT_PRIMARY, NODE_BORDER_SELECTED, PANEL_BG


class Minimap(QWidget):
    """Renders a bird's-eye thumbnail of the scene and lets the user click to navigate."""

    _WIDTH = 210
    _HEIGHT = 140
    _MARGIN = 10
    _PADDING = 6

    def __init__(self, view: QGraphicsView, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._view = view
        self.setFixedSize(self._WIDTH, self._HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self._dragging = False

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.update)
        self._refresh_timer.start(80)  # ~12 fps — lightweight

    # ── painting ───────────────────────────────────────────────────────────
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self._WIDTH, self._HEIGHT
        p = self._PADDING

        # Background panel
        bg = QColor(12, 14, 22, 210)
        painter.setBrush(QBrush(bg))
        painter.setPen(QPen(QColor("#1E2035"), 1))
        painter.drawRoundedRect(0, 0, w, h, 8, 8)

        scene = self._view.scene()
        if scene is None:
            return

        items_rect = scene.itemsBoundingRect()
        if items_rect.isEmpty():
            # Draw "empty" hint
            painter.setPen(QColor("#2D3260"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Empty canvas")
            return

        items_rect = items_rect.adjusted(-80, -80, 80, 80)

        # Scale to fit inside the minimap with padding
        avail_w = w - p * 2
        avail_h = h - p * 2
        sx = avail_w / items_rect.width()
        sy = avail_h / items_rect.height()
        scale = min(sx, sy)

        # Offset to center content
        rendered_w = items_rect.width() * scale
        rendered_h = items_rect.height() * scale
        ox = p + (avail_w - rendered_w) / 2
        oy = p + (avail_h - rendered_h) / 2

        target = QRectF(ox, oy, rendered_w, rendered_h)

        # Clip to inner area
        painter.setClipRect(QRectF(p, p, avail_w, avail_h))

        # Render scene (nodes appear as colored rectangles)
        scene.render(painter, target, items_rect)

        painter.setClipping(False)

        # Viewport rectangle
        vp_poly = self._view.mapToScene(self._view.viewport().rect())
        vp_rect = vp_poly.boundingRect()

        def to_mm(sr: QRectF) -> QRectF:
            """Convert scene rect → minimap pixel rect."""
            rx = (sr.x() - items_rect.x()) * scale + ox
            ry = (sr.y() - items_rect.y()) * scale + oy
            rw = sr.width() * scale
            rh = sr.height() * scale
            return QRectF(rx, ry, rw, rh)

        vp_mm = to_mm(vp_rect)
        painter.setBrush(QBrush(QColor(124, 58, 237, 35)))
        painter.setPen(QPen(ACCENT_PRIMARY, 1.5))
        painter.drawRect(vp_mm)

    # ── interaction — click/drag to navigate ───────────────────────────────
    def _scene_pos_from_mouse(self, local: QPoint) -> QPointF | None:
        scene = self._view.scene()
        if scene is None:
            return None
        items_rect = scene.itemsBoundingRect()
        if items_rect.isEmpty():
            return None
        items_rect = items_rect.adjusted(-80, -80, 80, 80)
        p = self._PADDING
        avail_w = self._WIDTH - p * 2
        avail_h = self._HEIGHT - p * 2
        sx = avail_w / items_rect.width()
        sy = avail_h / items_rect.height()
        scale = min(sx, sy)
        rendered_w = items_rect.width() * scale
        rendered_h = items_rect.height() * scale
        ox = p + (avail_w - rendered_w) / 2
        oy = p + (avail_h - rendered_h) / 2
        sc_x = (local.x() - ox) / scale + items_rect.x()
        sc_y = (local.y() - oy) / scale + items_rect.y()
        return QPointF(sc_x, sc_y)

    def _navigate_to(self, local: QPoint) -> None:
        sc = self._scene_pos_from_mouse(local)
        if sc:
            self._view.centerOn(sc)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._navigate_to(event.position().toPoint())

    def mouseMoveEvent(self, event) -> None:
        if self._dragging:
            self._navigate_to(event.position().toPoint())

    def mouseReleaseEvent(self, event) -> None:
        self._dragging = False
