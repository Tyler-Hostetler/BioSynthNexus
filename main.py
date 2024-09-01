import sys
import loadMainUI

if __name__ == '__main__':
    app = loadMainUI.QApplication(sys.argv)
    MainWindow = loadMainUI.QMainWindow()
    UIWindow = loadMainUI.MainUI('ui_main_window.ui')
    UIWindow.window.show()

    sys.exit(app.exec())
