import base64
import os
import sys
import threading
import winreg

import yaml
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMessageBox)

from app_ui import RemoteControlUI


class RemoteControlApp(RemoteControlUI):
    def __init__(self):
        super().__init__()
        self.waitress_thread = None
        self.key = None
        self.port = 51314  # 默认端口
        self.key_path = "config.yaml"  # 配置文件存储在当前目录下的 config.yaml
        self.load_settings()

        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)
        self.set_key_button.clicked.connect(self.set_key)
        self.exit_button.clicked.connect(self.exit_app)
        self.autostart_checkbox.stateChanged.connect(self.set_autostart)

    def start_server(self):
        if not self.key:
            QMessageBox.warning(self, self.tr('Error'), self.tr('Please set AES Key first.'))
            return

        self.port = int(self.port_input.text() or 51314)
        self.waitress_thread = threading.Thread(target=self.run_waitress)
        self.waitress_thread.start()
        self.status_label.setText(self.tr('Server is running'))
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.tray_icon.setIcon(QIcon(self.get_icon_path(True)))  # 切换图标为已激活状态

    def stop_server(self):
        if self.waitress_thread:
            self.waitress_thread.do_run = False
            self.waitress_thread.join()
            self.waitress_thread = None
            self.status_label.setText(self.tr('Server is stopped'))
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.tray_icon.setIcon(QIcon(self.get_icon_path(False)))  # 切换图标为未激活状态

    def run_waitress(self):
        from waitress import serve
        import wsgi
        wsgi.set_key(self.key)
        serve(wsgi.app, host='0.0.0.0', port=self.port)

    def set_key(self):
        self.key = self.key_input.text().encode('utf-8')
        config = self.load_config()
        config['key'] = base64.b64encode(self.key).decode('utf-8')
        self.save_config(config)
        QMessageBox.information(self, self.tr('Key Set'), self.tr('AES Key has been set successfully.'))

    def set_autostart(self, state):
        config = self.load_config()
        if state == Qt.Checked:
            config['autostart'] = True
            self.add_to_startup()
        else:
            config['autostart'] = False
            self.remove_from_startup()
        self.save_config(config)

    def add_to_startup(self):
        try:
            key = winreg.HKEY_CURRENT_USER
            key_value = r'Software\Microsoft\Windows\CurrentVersion\Run'
            key_obj = winreg.OpenKey(key, key_value, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key_obj, "RemoteControlServer", 0, winreg.REG_SZ, sys.executable)
            winreg.CloseKey(key_obj)
        except Exception as e:
            print(e)

    def remove_from_startup(self):
        try:
            key = winreg.HKEY_CURRENT_USER
            key_value = r'Software\Microsoft\Windows\CurrentVersion\Run'
            key_obj = winreg.OpenKey(key, key_value, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key_obj, "RemoteControlServer")
            winreg.CloseKey(key_obj)
        except Exception as e:
            print(e)

    def load_settings(self):
        config = self.load_config()
        self.key = base64.b64decode(config.get('key', ''))
        self.port = config.get('port', 51314)
        self.autostart_checkbox.setChecked(config.get('autostart', False))
        self.hide_on_start_checkbox.setChecked(config.get('hide_on_start', False))
        self.port_input.setText(str(self.port))
        language = config.get('language', 'English')
        if language == "中文":
            self.language_selector.setCurrentIndex(1)
            self.translator.load("translations/zh_CN.qm")
        else:
            self.language_selector.setCurrentIndex(0)
            self.translator.load("")
        QApplication.instance().installTranslator(self.translator)
        self.retranslateUi()

        if config.get('hide_on_start', False):
            self.hide()

    def load_config(self):
        if not os.path.exists(self.key_path):
            return {}
        with open(self.key_path, 'r') as f:
            return yaml.safe_load(f)

    def save_config(self, config):
        with open(self.key_path, 'w') as f:
            yaml.dump(config, f)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RemoteControlApp()
    ex.show()
    sys.exit(app.exec_())
