import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QRadioButton, QMessageBox


class TriviaGame(QMainWindow):
    def timeout(self):
        self.show_final_score()

    def show_instruction_box(self):
        instruction = "Welcome to the Finance Trivia Game!\n\n"
        instruction += "Instructions:\n"
        instruction += "- You will be asked a series of finance-related questions.\n"
        instruction += "- Select the option you think is the correct answer.\n"
        instruction += "- You will earn 2 points for each correct answer.\n"
        instruction += "- You will lose 1 point for each wrong answer.\n"
        instruction += "- You have 2 attempts per question before moving on.\n"
        instruction += "- You have 4.5 minutes to complete the game.\n"
        instruction += "- If you complete the game within 4.5 minutes, you earn 5 extra points.\n\n"
        instruction += "Good luck!\n\n"
        instruction += "Why did the banker switch careers? Because he lost interest!"

        QMessageBox.information(self, "Instructions", instruction, QMessageBox.Ok)

        self.timer.start(270000)  # 4.5 minutes (270,000 milliseconds)

    def create_widgets(self):
        self.question_label = QLabel()
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setFont(QFont("Arial", 14))

        self.options = []
        for i in range(5):
            option = QRadioButton()
            option.setFont(QFont("Arial", 12))
            self.options.append(option)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.check_answer)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.question_label)
        for option in self.options:
            self.layout.addWidget(option)
        self.layout.addWidget(self.submit_button)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        # Set background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#E0F4F9"))  # Light blue background color
        self.setPalette(palette)

    def show_next_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.question_label.setText(question["question"])
            for i in range(5):
                self.options[i].setText(question["options"][i])
                self.options[i].setChecked(False)
                self.options[i].setStyleSheet("")
            self.submit_button.setEnabled(True)
        else:
            self.show_final_score()

    def check_answer(self):
        question = self.questions[self.current_question_index]
        selected_option = ""
        for i in range(5):
            if self.options[i].isChecked():
                selected_option = question["options"][i]
                break

        if selected_option == question["answer"]:
            self.score += 2
        else:
            self.score -= 1
            self.attempts -= 1
            self.options[self.options.index(
                self.options[question["options"].index(question["answer"])])].setStyleSheet("color: red; font-weight: bold;")

            if self.attempts == 0:
                self.options[self.options.index(
                    self.options[question["options"].index(question["answer"])])].setStyleSheet("")
                self.options[self.options.index(
                    self.options[question["options"].index(selected_option)])].setStyleSheet("color: red; font-weight: bold;")
                self.submit_button.setEnabled(False)

        self.current_question_index += 1
        self.show_next_question()

    def show_final_score(self):
        self.timer.stop()
        message = f"Game Over!\nYour score: {self.score}\n"
        if self.timer.remainingTime() <= 0:
            message += "Out of time! No extra points earned"
        else:
            message += "You completed the game within 4.5 minutes! You earned 5 extra points."
        play_again = QMessageBox.question(
            self, "Game Over", message + "\nDo you want to play again?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if play_again == QMessageBox.Yes:
            self.current_question_index = 0
            self.score = 0
            self.attempts = 2
            self.show_next_question()
            self.timer.start(270000)  # 4.5 minutes (270,000 milliseconds)
        else:
            self.close()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finance Trivia Game")
        self.current_question_index = 0
        self.score = 0
        self.attempts = 2

        self.questions = [
            {
                "question": "What is the largest stock exchange in the world?",
                "options": ["NYSE", "NASDAQ", "LSE", "TSE", "HKEX"],
                "answer": "NYSE"
            },
            {
                "question": "Whrat is the largest stock exchange in the world?",
                "options": ["NYSE", "NASDAQ", "LSE", "TSE", "HKEX"],
                "answer": "NYSE"
            },
            {
                "question": "Whrgat is the largest stock exchange in the world?",
                "options": ["NYSE", "NASDAQ", "LSE", "TSE", "HKEX"],
                "answer": "NYSE"
            },
            {
                "question": "Whrgrat is the largest stock exchange in the world?",
                "options": ["NYSE", "NASDAQ", "LSE", "TSE", "HKEX"],
                "answer": "NYSE"
            },
            # Add more questions here
        ]

        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)

        self.create_widgets()
        self.show_instruction_box()


if __name__ == "__main__":
    app = QApplication([])
    game = TriviaGame()
    game.show()
    sys.exit(app.exec())