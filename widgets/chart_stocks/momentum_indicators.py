from PySide6.QtWidgets import QGroupBox, QScrollArea, QWidget, QHBoxLayout, QVBoxLayout
import ta_widget

class MomentumView(QGroupBox):
    def __init__(self, selected_ta):
        super().__init__()
        self.setTitle("Momentum Indicators")
        self.setStyleSheet('background-color: white')
        self.setLayout(QHBoxLayout())
        self.momentum_scrollarea = QScrollArea()
        self.momentum_widget = QWidget()
        self.momentum_widget.setFixedHeight(1500)
        self.momentum_widget.setLayout(QVBoxLayout())
        self.momentum_scrollarea.setWidget(self.momentum_widget)
        self.layout().addWidget(self.momentum_scrollarea)
        self.momentum_widget.setFixedWidth(self.momentum_scrollarea.width())

        momentum_indicator_params = (
            ("Average Directional Movement", "talib.ADX", ((14, "Period"),)),
            ("ADX Rating", "talib.ADXR", ((14, "Period"),)),
            ("Absolute Price Oscillator", "talib.APO", ((12, "Fast MA Period"), (26, "Slow MA Period"), (0, "MA Type"))),
            ("Aroon", "talib.AROON", ((14, "Period"),)),
            ("Aroon Oscillator", "talib.AROONOSC", ((14, "Period"),)),
            ("Balance of Power", "talib.BOP", ()),
            ("Commodity Channel Index", "talib.CCI", ((14, "Period"),)),
            ("Chande Momentum Oscillator", "talib.CMO", ((14, "Period"),)),
            ("Directional Movement Index", "talib.DX", ((14, "Period"),)),
            (
                "MACD", "talib.MACDEXT",
                (
                    (12, "Fast Period"), (0, "Fast MA Type"), (26, "Slow Period"),
                    (0, "Slow MA Type"), (9, "Signal Period"), (0, "Signal MA Type")
                )
            ),
            ("Money Flow Index", "talib.MFI", ((14, "Period"),)),
            ("Minus Directional Indicator", "talib.MINUS_DI", ((14, "Period"),)),
            ("Minus Directional Movement", "talib.MINUS_DM", ((14, "Period"),)),
            ("Momentum", "talib.MOM", ((10, "Period"),)),
            ("Plus Directional Indicator", "talib.PLUS_DI", ((14, "Period"),)),
            ("Plus Directional Movement", "talib.PLUS_DM", ((14, "Period"),)),
            ("KAMA Indicator", "ta.momentum.kama", ((10, "Efficiency Ratio"), (2, "Fast EMA Period"), (30, "Slow EMA Period"))),
            (
                "Percentage Volume Oscillator", "ta.momentum.pvo",
                (
                    (12, "Slow MA Period"), (26, "Fast MA Period"), (9, "Signal Period")
                )
            ),
            ("Rate of Change", "talib.ROC", ((10, "Period"),)),
            ("ROC Percentage", "talib.ROCP", ((10, "Period"),)),
            ("ROC Ratio", "talib.ROCR", ((10, "Period"),)),
            ("ROCR Indexed to 100", "talib.ROCR100", ((10, "Period"),)),
            ("Relative Strength Index", "talib.RSI", ((20, "Period"),)),
            (
                "Slow Stochastic", "talib.STOCH",
                (
                    (5, "Fast %k Period"), (3, "Slow %k Period"), (0, "Slow %k MA Type"),
                    (3, "Slow %d Period"), (0, "Slow %d MA Type")
                )
            ),
            ("Fast Stochastic", "talib.STOCHF", ((5, "Fast %k Period"), (3, "Fast %d Period"), (0, "Fast %d MA Type"))),
            (
                "Stochastic RSI", "talib.STOCHRSI",
                (
                    (14, "RSI Period"), (5, "Fast %k Period"), (3, "Fast %d Period"), (0, "Fast %d MA Type")
                )
            ),
            ("True Strength Index", "ta.momentum.tsi", ((13, "Fast Period"), (25, "Slow Period"))),
            ("Ultimate Oscillator", "talib.ULTOSC", ((7, "Fast Length"), (14, "Medium Length"), (28, "Slow Length"))),
            ("Williams %R", "talib.WILLR", ((14, "Period"),))
        )

        for (indicator_name, fn, defaults) in momentum_indicator_params:
            self.momentum_widget.layout().addWidget(
                ta_widget.create_ta_widget(
                    self, indicator_name, selected_ta, fn, defaults
                )
            )



