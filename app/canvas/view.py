"""FlowView — QGraphicsView with pan, zoom, drag-drop and keyboard shortcuts."""

from __future__ import annotations

from PySide6.QtCore import QMimeData, QPoint, QPointF, Qt, Signal
from PySide6.QtGui import (
    QDrag,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QWheelEvent,
)
from PySide6.QtWidgets import QGraphicsView

from app.canvas.scene import FlowScene


class FlowView(QGraphicsView):
    """Infinite canvas view: pan with middle-mouse / Space+drag, zoom with scroll."""

    zoom_changed = Signal(float)

    _ZOOM_MIN = 0.05
    _ZOOM_MAX = 5.0
    _ZOOM_STEP = 0.10

    def __init__(self, scene: FlowScene, parent=None) -> None:
        super().__init__(scene, parent)
        self._zoom_level: float = 1.0
        self._panning: bool = False
        self._pan_last: QPoint = QPoint()
        self._space_held: bool = False

        self._setup_view()

    # ── setup ──────────────────────────────────────────────────────────────
    def _setup_view(self) -> None:
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
            | QPainter.RenderHint.TextAntialiasing
        )
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorViewCenter
        )
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setRubberBandSelectionMode(Qt.ItemSelectionMode.IntersectsItemShape)
        self.setAcceptDrops(True)
        self.setBackgroundBrush(Qt.BrushStyle.NoBrush)
        self.setFrameShape(QGraphicsView.Shape.NoFrame)

        # Try OpenGL for smoother rendering (only when a real display is available)
        try:
            import os
            platform = os.environ.get("QT_QPA_PLATFORM", "")
            if platform not in ("offscreen", "minimal"):
                from PySide6.QtOpenGLWidgets import QOpenGLWidget
                from PySide6.QtGui import QSurfaceFormat
                fmt = QSurfaceFormat()
                fmt.setSamples(4)  # 4x MSAA
                QSurfaceFormat.setDefaultFormat(fmt)
                self.setViewport(QOpenGLWidget())
        except Exception:
            pass

    # ── public zoom API ────────────────────────────────────────────────────
    def zoom_in(self) -> None:
        self._apply_zoom(1.15)

    def zoom_out(self) -> None:
        self._apply_zoom(1 / 1.15)

    def reset_zoom(self) -> None:
        self.resetTransform()
        self._zoom_level = 1.0
        self.zoom_changed.emit(self._zoom_level)

    def fit_all(self) -> None:
        items_rect = self.scene().itemsBoundingRect()
        if not items_rect.isEmpty():
            self.fitInView(items_rect.adjusted(-60, -60, 60, 60),
                           Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom_level = self.transform().m11()
            self.zoom_changed.emit(self._zoom_level)

    def _apply_zoom(self, factor: float) -> None:
        new_z = self._zoom_level * factor
        if self._ZOOM_MIN <= new_z <= self._ZOOM_MAX:
            self._zoom_level = new_z
            self.scale(factor, factor)
            self.zoom_changed.emit(self._zoom_level)

    # ── wheel ──────────────────────────────────────────────────────────────
    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y()
        if delta == 0:
            super().wheelEvent(event)
            return
        factor = 1.12 if delta > 0 else 1 / 1.12
        self._apply_zoom(factor)
        event.accept()

    # ── mouse ──────────────────────────────────────────────────────────────
    def mousePressEvent(self, event: QMouseEvent) -> None:
        mid = event.button() == Qt.MouseButton.MiddleButton
        alt_left = (event.button() == Qt.MouseButton.LeftButton
                    and event.modifiers() & Qt.KeyboardModifier.AltModifier)
        space_left = (event.button() == Qt.MouseButton.LeftButton
                      and self._space_held)

        if mid or alt_left or space_left:
            self._panning = True
            self._pan_last = event.position().toPoint()
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._panning:
            delta = event.position().toPoint() - self._pan_last
            self._pan_last = event.position().toPoint()
            h = self.horizontalScrollBar()
            v = self.verticalScrollBar()
            h.setValue(h.value() - delta.x())
            v.setValue(v.value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._panning and event.button() in (
            Qt.MouseButton.MiddleButton,
            Qt.MouseButton.LeftButton,
        ):
            self._panning = False
            mode = QGraphicsView.DragMode.NoDrag if self._space_held \
                else QGraphicsView.DragMode.RubberBandDrag
            self.setDragMode(mode)
            cursor = Qt.CursorShape.OpenHandCursor if self._space_held \
                else Qt.CursorShape.ArrowCursor
            self.setCursor(cursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    # ── keyboard ───────────────────────────────────────────────────────────
    def keyPressEvent(self, event: QKeyEvent) -> None:
        k = event.key()
        if k == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_held = True
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
        elif k == Qt.Key.Key_F:
            self.fit_all()
            event.accept()
        elif k == Qt.Key.Key_0:
            self.reset_zoom()
            event.accept()
        elif k == Qt.Key.Key_Equal or k == Qt.Key.Key_Plus:
            self.zoom_in()
            event.accept()
        elif k == Qt.Key.Key_Minus:
            self.zoom_out()
            event.accept()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_held = False
            if not self._panning:
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().keyReleaseEvent(event)

    # ── drag-and-drop from node library ───────────────────────────────────
    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        if event.mimeData().hasText():
            type_id = event.mimeData().text()
            pos = self.mapToScene(event.position().toPoint())
            scene: FlowScene = self.scene()
            scene.create_node(type_id, pos)
            event.acceptProposedAction()
        else:
            event.ignore()
