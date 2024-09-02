import sys
import loadMainUI
from qt_material import apply_stylesheet

if __name__ == '__main__':
    # Initialize the application
    app = loadMainUI.QApplication(sys.argv)

    # Create the main Window
    UIWindow = loadMainUI.MainUI('ui_main_window.ui')

    # Apply Material Design Stylesheet
    apply_stylesheet(app, theme='custom_ui_theme.xml')
    #apply_stylesheet(app, theme='dark_cyan.xml')

    # Show the main window
    UIWindow.window.show()

    # Run the application event loop
    sys.exit(app.exec())
