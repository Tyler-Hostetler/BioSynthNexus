import sys
import os
import loadMainUI
from qt_material import apply_stylesheet

def find_path(relative_path):
    # Function for managing paths of files consistently defore and after pyinstaller packaging
    if getattr(sys, 'frozen', False):
        # Triggered if wrapped up in pyinstaller
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    # Initialize the application
    app = loadMainUI.QApplication(sys.argv)

    # Create the main Window
    UIWindow = loadMainUI.MainUI(find_path('ui_main_window.ui'))

    # Apply Material Design Stylesheet
    apply_stylesheet(app, theme=find_path('custom_ui_theme.xml'))

    # Show the main window
    UIWindow.window.show()

    # Run the application event loop
    sys.exit(app.exec())
