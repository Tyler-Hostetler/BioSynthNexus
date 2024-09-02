import sys
import loadMainUI
from qt_material import apply_stylesheet

if __name__ == '__main__':
    app = loadMainUI.QApplication(sys.argv)
    MainWindow = loadMainUI.QMainWindow()
    UIWindow = loadMainUI.MainUI('ui_main_window.ui')
    UIWindow.window.show()

    # Changing UI Style
    apply_stylesheet(app, theme='custom_ui_theme.xml')

    sys.exit(app.exec())
