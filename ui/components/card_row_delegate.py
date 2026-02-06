from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle
from PyQt6.QtCore import QRect, QModelIndex, Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush


class CardRowDelegate(QStyledItemDelegate):
    """Custom delegate that paints card-style rounded-rect backgrounds per table row.

    Provides:
    - Rounded rectangle card appearance per row
    - Hover tint
    - Blue selection highlight with left accent border
    - Subtle bottom separator between rows
    """

    # Colors (matching Theme "Cool Slate" palette)
    COLOR_SURFACE = QColor("#2C313A")
    COLOR_SURFACE_HOVER = QColor("#333842")
    COLOR_SELECTION = QColor("#2A3A50")
    COLOR_ACCENT = QColor("#4A90D9")
    COLOR_BORDER_LIGHT = QColor("#2F343D")
    COLOR_TEXT_PRIMARY = QColor("#D4D7DD")
    COLOR_TEXT_SELECTED = QColor("#4A90D9")

    CARD_MARGIN = 2
    CARD_RADIUS = 6
    ACCENT_WIDTH = 3

    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = option.rect
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        # Draw card background
        card_rect = QRect(
            rect.x() + self.CARD_MARGIN,
            rect.y() + 1,
            rect.width() - 2 * self.CARD_MARGIN,
            rect.height() - 2,
        )

        if is_selected:
            painter.setBrush(QBrush(self.COLOR_SELECTION))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(card_rect, self.CARD_RADIUS, self.CARD_RADIUS)

            # Left accent border for selected row
            accent_rect = QRect(
                card_rect.x(),
                card_rect.y(),
                self.ACCENT_WIDTH,
                card_rect.height(),
            )
            painter.setBrush(QBrush(self.COLOR_ACCENT))
            painter.drawRoundedRect(accent_rect, 2, 2)
        elif is_hovered:
            painter.setBrush(QBrush(self.COLOR_SURFACE_HOVER))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(card_rect, self.CARD_RADIUS, self.CARD_RADIUS)
        else:
            painter.setBrush(QBrush(self.COLOR_SURFACE))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(card_rect, self.CARD_RADIUS, self.CARD_RADIUS)

        # Draw bottom separator line
        separator_pen = QPen(self.COLOR_BORDER_LIGHT, 1)
        painter.setPen(separator_pen)
        painter.drawLine(
            rect.x() + self.CARD_MARGIN + 8,
            rect.bottom(),
            rect.right() - self.CARD_MARGIN - 8,
            rect.bottom(),
        )

        # Draw text
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            text_color = self.COLOR_TEXT_SELECTED if is_selected else self.COLOR_TEXT_PRIMARY
            painter.setPen(QPen(text_color))
            text_rect = QRect(
                card_rect.x() + 12 + (self.ACCENT_WIDTH if is_selected else 0),
                card_rect.y(),
                card_rect.width() - 24,
                card_rect.height(),
            )
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                str(text),
            )

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        return QSize(option.rect.width(), 36)
