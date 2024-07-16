import yaml
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
                             QSystemTrayIcon, QMenu, QAction, QLineEdit, QComboBox, QCheckBox)


class RemoteControlUI(QWidget):
    def __init__(self):
        super().__init__()
        self.translator = QTranslator()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        font = QFont()
        font.setPointSize(12)

        self.language_selector = QComboBox()
        self.language_selector.setFont(font)
        self.language_selector.addItem("English")
        self.language_selector.addItem("中文")
        self.language_selector.currentIndexChanged.connect(self.change_language)
        self.layout.addWidget(self.language_selector)

        self.status_label = QLabel(self.tr("Server is stopped"))
        self.status_label.setFont(font)
        self.layout.addWidget(self.status_label)

        self.key_label = QLabel(self.tr("Enter AES Key:"))
        self.key_label.setFont(font)
        self.layout.addWidget(self.key_label)

        self.key_input = QLineEdit()
        self.key_input.setFont(font)
        self.key_input.setFixedHeight(30)
        self.layout.addWidget(self.key_input)

        self.set_key_button = QPushButton(self.tr("Set Key"))
        self.set_key_button.setFont(font)
        self.set_key_button.setFixedHeight(40)
        self.layout.addWidget(self.set_key_button)

        self.port_label = QLabel(self.tr("Enter Port (default: 51314):"))
        self.port_label.setFont(font)
        self.layout.addWidget(self.port_label)

        self.port_input = QLineEdit()
        self.port_input.setFont(font)
        self.port_input.setFixedHeight(30)
        self.layout.addWidget(self.port_input)

        self.autostart_checkbox = QCheckBox(self.tr("Start with Windows"))
        self.autostart_checkbox.setFont(font)
        self.layout.addWidget(self.autostart_checkbox)

        self.hide_on_start_checkbox = QCheckBox(self.tr("Hide on startup"))
        self.hide_on_start_checkbox.setFont(font)
        self.layout.addWidget(self.hide_on_start_checkbox)

        self.start_button = QPushButton(self.tr("Start Server"))
        self.start_button.setFont(font)
        self.start_button.setFixedHeight(40)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton(self.tr("Stop Server"))
        self.stop_button.setFont(font)
        self.stop_button.setFixedHeight(40)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        self.exit_button = QPushButton(self.tr("Exit Application"))
        self.exit_button.setFont(font)
        self.exit_button.setFixedHeight(40)
        self.layout.addWidget(self.exit_button)

        self.setLayout(self.layout)
        self.setWindowTitle(self.tr("Remote Control Server"))
        self.setWindowIcon(QIcon("./assets/icon_activated.png"))
        self.setGeometry(300, 300, 400, 600)

        # 居中界面
        qt_rectangle = self.frameGeometry()
        center_point = QApplication.desktop().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(self.get_icon_path(False)))  # 设置初始图标为未激活状态
        self.tray_icon.setToolTip(self.tr("Remote Control Server"))

        quit_action = QAction(self.tr("Exit"), self)
        tray_menu = QMenu()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

        quit_action.triggered.connect(self.exit_app)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def change_language(self):
        language = self.language_selector.currentText()
        if language == "中文":
            self.translator.load("translations/zh_CN.qm")
        else:
            self.translator.load("")
        QApplication.instance().installTranslator(self.translator)
        self.retranslateUi()

        # 将当前语言设置存储到配置文件中
        with open("config.yaml", 'r') as f:
            config = yaml.safe_load(f)
            config['language'] = language
        with open("config.yaml", 'w') as f:
            yaml.dump(config, f)

    def retranslateUi(self):
        self.status_label.setText(self.tr("Server is stopped"))
        self.key_label.setText(self.tr("Enter AES Key:"))
        self.set_key_button.setText(self.tr("Set Key"))
        self.port_label.setText(self.tr("Enter Port (default: 51314):"))
        self.autostart_checkbox.setText(self.tr("Start with Windows"))
        self.hide_on_start_checkbox.setText(self.tr("Hide on startup"))
        self.start_button.setText(self.tr("Start Server"))
        self.stop_button.setText(self.tr("Stop Server"))
        self.exit_button.setText(self.tr("Exit Application"))
        self.setWindowTitle(self.tr("Remote Control Server"))

    def exit_app(self):
        self.close()
        QApplication.instance().quit()

    def closeEvent(self, event):
        if self.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                self.tr("Remote Control Server"),
                self.tr("The application is still running in the system tray."),
                QSystemTrayIcon.Information,
                2000
            )

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()

    def get_icon_path(self, activated):
        if activated:
            return "./assets/icon_activated.png"
        else:
            return "./assets/icon_not_activated.png"

