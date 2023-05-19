from PySide6.QtWidgets import QDialog, QPushButton
from minigame import main

class MinigameTab(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('background-color: deepskyblue;')

        self.minigame_btn = QPushButton(self)
        self.minigame_btn.setText("Launch Minigame")
        self.minigame_btn.setStyleSheet("background-color: white")
        self.minigame_btn.setGeometry(550, 200, 200, 200)
        self.minigame_btn.clicked.connect(main.run_game)