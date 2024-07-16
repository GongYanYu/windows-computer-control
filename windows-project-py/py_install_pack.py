import sys

from PyQt5.QtWidgets import QApplication
from app import RemoteControlApp

def main():
    app = QApplication(sys.argv)
    ex = RemoteControlApp()
    ex.show()
    sys.exit(app.exec_())


main()


