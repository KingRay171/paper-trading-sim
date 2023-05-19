from PySide6.QtWidgets import QGroupBox, QScrollArea, QWidget, QHBoxLayout, QVBoxLayout
import ta_widget

class TrendView(QGroupBox):
    def __init__(self, selected_ta):
        super().__init__()
        self.setTitle("Trend Indicators")
        self.setStyleSheet('background-color: white')
        self.setLayout(QHBoxLayout())

        self.trend_scrollarea = QScrollArea()
        self.trend_widget = QWidget()
        self.trend_widget.setFixedHeight(1500)
        self.trend_widget.setLayout(QVBoxLayout())
        self.trend_scrollarea.setWidget(self.trend_widget)
        self.layout().addWidget(self.trend_scrollarea)
        self.trend_widget.setFixedWidth(self.trend_scrollarea.width())

        trend_indicator_params = (
            ("Detrended Price Oscillator", "ta.trend.dpo", ((14, "Period"),)),
            ("KST Oscillator", "ta.trend.KSTIndicator", (
                (10, "Rate of Change 1 Length"), (15, "Rate of Change 2 Length"), (20, "Rate of Change 3 Length"),
                (30, "Rate of Change 4 Length"), (10, "Simple Moving Average 1 Length"), (10, "Simple Moving Average 2 Length"),
                (10, "Simple Moving Average 3 Length"), (15, "Simple Moving Average 4 Length"), (9, "Signal Line Length")
            )),
            (
                "Ichimoku Cloud", "ta.trend.IchimokuIndicator",
                ((9, "Conversion Line Length"), (26, "Base Line Length"), (52, "Leading Span Length"), (False, "Shift Medium"))
            ),
            ("Mass Index", "ta.trend.mass_index", ((9, "Fast Period"), (25, "Slow Period"))),
            (
                "Schaff Trend Cycle", "ta.trend.stc",
                ((50, "MACD Slow Period"), (23, "MACD Fast Period"), (10, "# of Cycles"), (3, "First %D Length"), (3, "Second %D Length"))
            ),
            ("Trix Indicator", "ta.trend.trix", ((15, "Period"),)),
            (
                "Parabolic SAR", "ta.trend.PSARIndicator", ((.02, "Acceleration Factor"), (.2, "Maximum Acceleration Factor"))
            ),
            ("Vortex Indicator", "ta.trend.VortexIndicator", ((14, "Period"),))
        )

        for (indicator_name, fn, defaults) in trend_indicator_params:
            self.trend_widget.layout().addWidget(
                ta_widget.create_ta_widget(
                    self, indicator_name, selected_ta, fn, defaults
                )
            )



