import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel, QCheckBox, QPushButton, QComboBox, \
    QFileDialog, QLineEdit
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
import UniProtRequests as upr
import SqlRequests as sqlr
import find_similarity


class MainUI(QMainWindow):
    def __init__(self, ui_file, parent=None):
        super(MainUI, self).__init__(parent)

        # Initialize Variables
        self.sql_path = None
        self.input = None
        self.input_type = None
        self.output = None
        self.output_type = None
        self.secondary_input = None

        # Load UI
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        # ui_file.close()

        # Sql Widgets
        self.status_label = self.window.findChild(QLabel, 'sql_label')
        self.sql_checkbox = self.window.findChild(QCheckBox, 'sql_checkbox')
        self.sql_button = self.window.findChild(QPushButton, 'sql_button')

        # Input Widgets
        self.input_label = self.window.findChild(QLabel, 'input_label')
        self.input_textedit = self.window.findChild(QTextEdit, 'input_textedit')
        self.input_type_label = self.window.findChild(QLabel, 'input_type_label')
        self.input_type_combobox = self.window.findChild(QComboBox, 'input_type_combobox')
        self.input_type_combobox.addItems(['Accession', 'PFam'])
        self.secondary_input_lineedit = self.window.findChild(QLineEdit, 'secondary_input_lineedit')

        # Output Widgets
        self.output_label = self.window.findChild(QLabel, 'output_label')
        self.output_count_label = self.window.findChild(QLabel, 'output_count_label')
        self.output_textedit = self.window.findChild(QTextEdit, 'output_textedit')
        self.output_type_label = self.window.findChild(QLabel, 'output_type_label')
        self.output_type_combobox = self.window.findChild(QComboBox, 'output_type_combobox')
        self.output_type_combobox.addItems(upr.REQUEST_TYPES)
        self.output_type_combobox.addItems(sqlr.REQUEST_TYPES)
        self.similarity_button = self.window.findChild(QPushButton, 'similarity_button')

        # Note: Use First combobox for a selection between SQL and Uniprot, fill second combobox accordingly

        # Replace Input with Output Widget
        self.output_to_input_button = self.window.findChild(QPushButton, 'output_to_input_button')

        # Search Widget
        self.search_button = self.window.findChild(QPushButton, 'search_button')

        # Save Widget
        self.save_button = self.window.findChild(QPushButton, 'save_button')

        # Inputs
        self.sql_button.clicked.connect(self.sql_upload)
        self.search_button.clicked.connect(self.search)
        self.save_button.clicked.connect(self.save_output)
        self.output_to_input_button.clicked.connect(self.set_output_to_input)
        self.similarity_button.clicked.connect(self.output_similarity_table)

    def sql_upload(self):
        _sql_path = QFileDialog.getOpenFileName(self, 'Please Select Sqlite3 File')
        self.sql_path = _sql_path[0]
        print(f"Attempting to Open {self.sql_path}")
        self.status_label.setText('Selected: ' + os.path.basename(self.sql_path))

    def search(self):
        print('Searching')
        self.input_type = self.input_type_combobox.currentText()
        self.output_type = self.output_type_combobox.currentText()
        self.input = self.input_textedit.toPlainText().split('\n')
        self.secondary_input = self.secondary_input_lineedit.text()
        temp_output = []

        if self.output_type in sqlr.REQUEST_TYPES:
            if len(self.input) <= 1:
                self.input = self.input[0]
            temp_output = sqlr.get_output(self.sql_path, self.input, self.output_type, self.secondary_input)
        elif self.output_type in upr.REQUEST_TYPES:
            for element in self.input:
                try:
                    temp_output.append(upr.uniprot_request_v2(element, self.output_type))
                except:
                    print(f"Request Failed for {element}")
                    continue

        self.output = temp_output
        self.fill_output()

    def fill_output(self):
        print('Outputting Search Results')
        self.output_count_label.setText("Count: " + str(len(self.output)))
        output_text_string = ''
        for output_line in self.output:
            output_text_string += str(output_line) + '\n'
        self.output_textedit.setText(output_text_string)

    def save_output(self):
        print('Saving')

    def set_output_to_input(self):
        print('Filling input box with output results')
        input_text_string = ''
        for input_line in self.output:
            input_text_string += str(input_line) + '\n'
        self.input_textedit.setText(input_text_string)

    def output_similarity_table(self):
        search_input_list = self.input_textedit.toPlainText().split('\n')
        find_similarity.output_table(self.sql_path, search_input_list)


