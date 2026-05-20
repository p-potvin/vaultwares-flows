#!/usr/bin/env python3
"""Vaultwares Flows — entry point."""

from __future__ import annotations

import sys


def main() -> None:
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QFont, QFontDatabase
    except ImportError:
        print(
            "PySide6 is required. Install it with:\n"
            "  pip install PySide6\n",
            file=sys.stderr,
        )
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("Vaultwares Flows")
    app.setOrganizationName("Vaultwares")
    app.setApplicationVersion("0.1.0")

    # Apply global stylesheet
    from app.theme.palette import APP_STYLESHEET
    app.setStyleSheet(APP_STYLESHEET)

    # Load Inter font if available, fall back gracefully
    QFontDatabase.addApplicationFont(":/fonts/Inter-Regular.ttf")
    default_font = QFont("Inter", 12)
    default_font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(default_font)

    from app.main_window import FlowWindow
    window = FlowWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
