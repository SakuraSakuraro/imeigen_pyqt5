import random
import os
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap
import configparser
import pygame

# Getting language strings from config.ini
config = configparser.ConfigParser()
config.read('./config.ini', encoding='utf-8-sig')
lang = config.get('Settings', 'Lang')

imei_num = config.get(lang, 'IMEINUM')
gen_num = config.get(lang, 'GENNUM')
clipbrd = config.get(lang, 'CLIPBRD')
gen_imei = config.get(lang, 'GENIMEI')
error1_msg = config.get(lang, 'ERROR1')
error2_msg = config.get(lang, 'ERROR2')
success_msg = config.get(lang, 'SUCCGEN')
prog_name = config.get(lang, 'NAMEPROG')

# Getting the list of phones from phone_models.txt and their corresponding IMEI
with open('./phone_models.txt') as f:
    phone_models_imei = dict(line.strip().split(':') for line in f.readlines())

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(prog_name)
        self.setFixedSize(353, 196)
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), 'icon.ico'))))

        # Setting a background image
        self.canvas = QtWidgets.QLabel(self)
        self.canvas.setGeometry(0, 0, 353, 196)
        bg_image_path = os.path.join(sys._MEIPASS, "background.png") if hasattr(sys, "_MEIPASS") else "./background.png"
        self.canvas.setPixmap(QPixmap(bg_image_path))

        # Setting positions interface items 
        self.phone_model_var = QtWidgets.QComboBox(self)
        self.phone_model_var.addItems(list(phone_models_imei.keys()))
        self.phone_model_var.setCurrentIndex(-1)  # Set the index to -1 for not selected by default
        self.phone_model_var.setGeometry(10, 9, 165, 25)
        self.phone_model_var.currentIndexChanged.connect(self.set_imei_prefix)

        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        self.imei_prefix_label = QtWidgets.QLabel(imei_num, self)
        self.imei_prefix_label.setGeometry(23, 35, 176, 20)
        self.imei_prefix_label.setFont(bold_font)
        self.imei_prefix_entry = QtWidgets.QLineEdit(self)
        self.imei_prefix_entry.setGeometry(17, 56, 148, 21)

        self.imei_prefix_button = QtWidgets.QPushButton(clipbrd, self)
        self.imei_prefix_button.setGeometry(10, 83, 180, 28)
        self.imei_prefix_button.clicked.connect(self.paste_imei_prefix)

        self.amount_to_generate_label = QtWidgets.QLabel(gen_num, self)
        self.amount_to_generate_label.setGeometry(23, 110, 176, 20)
        self.amount_to_generate_label.setFont(bold_font)
        self.amount_to_generate_entry = QtWidgets.QLineEdit(self)
        self.amount_to_generate_entry.setGeometry(23, 129, 148, 22)

        self.generate_button = QtWidgets.QPushButton(gen_imei, self)
        self.generate_button.setGeometry(10, 155, 173, 27)
        self.generate_button.clicked.connect(self.generate_imei)

        self.play_music()

    def calculate_imei(self, imei):
        odd_sum = 0
        even_sum = 0
        for i, digit in enumerate(imei):
            if i % 2 == 0:  # i is even
                even_sum += int(digit)
            else:  # i is odd
                even_digit = int(digit) * 2
                if even_digit > 9:
                    even_digit = even_digit // 10 + even_digit % 10
                even_sum += even_digit
        total = odd_sum + even_sum
        if total % 10 == 0:
            check_digit = 0
        else:
            check_digit = 10 - total % 10
        return imei + str(check_digit)

    def generate_imei(self):
        imei_prefix = self.imei_prefix_entry.text()
        amount_to_generate = self.amount_to_generate_entry.text()
        if not amount_to_generate.isdigit() or len(amount_to_generate) > 3:
            self.generate_button.setText(error2_msg)
            QtCore.QTimer.singleShot(2000, lambda: self.generate_button.setText(gen_imei))
            return
        amount_to_generate = int(amount_to_generate)
        if len(imei_prefix) != 8 or not imei_prefix.isdigit():
            self.generate_button.setText(error1_msg)
            QtCore.QTimer.singleShot(2000, lambda: self.generate_button.setText(gen_imei))
            return
        imei_list = []
        for _ in range(amount_to_generate):
            imei = imei_prefix + str(random.randint(0, 999999)).zfill(6)
            imei_with_check_digit = self.calculate_imei(imei)
            imei_list.append(imei_with_check_digit)
        with open('imei.txt', 'a') as f:
            f.write('\n'.join(imei_list) + '\n')
        self.generate_button.setText(success_msg)
        QtCore.QTimer.singleShot(2000, lambda: self.generate_button.setText(gen_imei))

    def paste_imei_prefix(self):
        clipboard = QtWidgets.QApplication.clipboard()
        self.imei_prefix_entry.setText(clipboard.text())

    def set_imei_prefix(self):
        selected_phone_model = self.phone_model_var.currentText()
        selected_imei = phone_models_imei.get(selected_phone_model, "")
        self.imei_prefix_entry.setText(selected_imei)

    def play_music(self):
        sound_enabled = config.getboolean('Settings', 'Sound')
        if sound_enabled:
            pygame.mixer.init()
            pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), "music.mp3"))
            pygame.mixer.music.play(-1)

app = QtWidgets.QApplication(sys.argv)

# Setting default font
font = QtGui.QFont("Calibri", 11)
app.setFont(font)

window = MainWindow()
window.show()
sys.exit(app.exec_())
