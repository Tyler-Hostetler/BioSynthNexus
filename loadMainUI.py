import os
from datetime import datetime
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
        self.output = None
        self.output_text = None
        self.output_type = None
        self.output_path = None
        self.parents = None
        self.secondary_input = None

        # Load UI
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)

        self.window.setWindowTitle("BioSynthNexus")

        # ui_file.close()

        # Sql Widgets
        self.status_label = self.window.findChild(QLabel, 'sql_label')
        self.sql_checkbox = self.window.findChild(QCheckBox, 'sql_checkbox')
        self.sql_button = self.window.findChild(QPushButton, 'sql_button')

        # Input Widgets
        self.input_label = self.window.findChild(QLabel, 'input_label')
        self.input_textedit = self.window.findChild(QTextEdit, 'input_textedit')
        self.secondary_input_lineedit = self.window.findChild(QLineEdit, 'secondary_input_lineedit')


        # Output Widgets
        self.output_label = self.window.findChild(QLabel, 'output_label')
        self.output_count_label = self.window.findChild(QLabel, 'output_count_label')
        self.output_textedit = self.window.findChild(QTextEdit, 'output_textedit')
        self.output_type_label = self.window.findChild(QLabel, 'output_type_label')
        self.output_type_combobox = self.window.findChild(QComboBox, 'output_type_combobox')
        self.request_type_combobox = self.window.findChild(QComboBox, 'request_type_combobox')
        self.similarity_button = self.window.findChild(QPushButton, 'similarity_button')

        # Set Output Type Box to UniProt Options
        self.update_output_combo(0)

        self.input_label.setText('Input: Accession ID')
        self.output_label.setText('Output: FASTA Sequence')

        # Fill Request Types
        self.request_type_combobox.addItems(['UniProt','BGC'])

        # Replace Input with Output Widget
        self.output_to_input_button = self.window.findChild(QPushButton, 'output_to_input_button')

        # Search Widget
        self.search_button = self.window.findChild(QPushButton, 'search_button')

        # Save Widget
        self.save_button = self.window.findChild(QPushButton, 'save_button')

        #Fix Text Coloration
        self.input_textedit.setStyleSheet("color: #ffffff")
        self.secondary_input_lineedit.setStyleSheet("color: #ffffff")
        self.output_textedit.setStyleSheet("color: #ffffff")

        # Inputs
        self.sql_button.clicked.connect(self.sql_upload)
        self.search_button.clicked.connect(self.search)
        self.save_button.clicked.connect(self.save_output)
        self.output_to_input_button.clicked.connect(self.set_output_to_input)
        self.similarity_button.clicked.connect(self.output_similarity_table)
        self.request_type_combobox.currentIndexChanged.connect(self.update_output_combo)
        self.output_type_combobox.currentIndexChanged.connect(self.selection_hints)



    def update_output_combo(self, index):
        self.output_type_combobox.clear()
        if index == 0:
            self.output_type_combobox.addItems(upr.REQUEST_TYPES)
        elif index == 1:
            if self.sql_path is not None:
                self.output_type_combobox.addItems(sqlr.REQUEST_TYPES)
            else:
                self.sql_button.setStyleSheet("border: 2px solid #ff1744; color: #ff1744")
                self.status_label.setStyleSheet("color: #ff1744")
                self.request_type_combobox.setCurrentIndex(0)

    def selection_hints(self):
        input_hint = 'Input: '
        output_hint = 'Output: '
        request_type = self.request_type_combobox.currentText()
        output_type = self.output_type_combobox.currentText()

        match output_type:
            case 'FASTA':
                input_hint += 'Accession ID'
                output_hint += 'FASTA Sequence'
            case 'GenBankID':
                input_hint += 'Accession ID'
                output_hint += 'GenBank(EMBL) Genome ID'
            case 'GenBank_Protein_ID':
                input_hint += 'Accession ID'
                output_hint += 'GenBank(EMBL) Protein ID'
            case 'GenBank_ORF_ID':
                input_hint += 'Accession ID'
                output_hint += 'GenBank(EMBL) Gene Open Reading Frame (ORF) ID'
            case 'Accession':
                input_hint += 'PFam ID(s) within BGCs'
                output_hint += 'Query Accessions within BGCs that contain Input PFam(s)'
            case 'BGC - Pfam':
                input_hint += 'BGC ID'
                output_hint += 'Pfam(s) found within given BGC'
            case 'BGC - Accession':
                input_hint += 'Accession ID(s) within given BGC'
                output_hint += 'Query Accessions within BGCs that contain Input PFam(s)'
            case 'Accessions from BGC by Pfam':
                input_hint += 'BGC IDs and PFam(Secondary Input)'
                output_hint += 'Accession of Proteins within given PFam in given BGCs <br>Accession_(BGC ID)'


        self.input_label.setText(input_hint)
        self.output_label.setText(output_hint)

    def sql_upload(self):
        _sql_path = QFileDialog.getOpenFileName(self, 'Please Select Sqlite3 File')
        self.sql_path = _sql_path[0]
        print(f"Attempting to Open {self.sql_path}")
        self.status_label.setText('Selected: ' + os.path.basename(self.sql_path))
        self.sql_button.setStyleSheet("border: 2px solid #4dd0e1; color: #4dd0e1")
        self.status_label.setStyleSheet("color: #4dd0e1")

    def search(self):
        print('Searching')
        self.output_type = self.output_type_combobox.currentText()
        self.input = self.input_textedit.toPlainText().split('\n')
        self.secondary_input = self.secondary_input_lineedit.text()
        temp_output = []

        if self.output_type in sqlr.REQUEST_TYPES:
            if len(self.input) <= 1:
                self.input = self.input[0]
            temp_output, self.parents = sqlr.get_output(self.sql_path, self.input, self.output_type, self.secondary_input)
        elif self.output_type in upr.REQUEST_TYPES:
            for index, element in enumerate(self.input):
                if self.parents is None:
                    _parents = None
                elif element == '':
                    continue
                else:
                    _parents = self.parents[index]
                try:
                    temp_output.append(upr.uniprot_request_v2(element, _parents, self.output_type))
                except:
                    print(f"Request Failed for {element}")
                    continue

        self.output = temp_output
        self.fill_output()

    def fill_output(self):
        print('Outputting Search Results')
        self.output_count_label.setText("Count: " + str(len(self.output)))
        self.output_text = ''
        if self.output_type in sqlr.REQUEST_TYPES and self.parents is not None:
            for i in range(len(self.output)):
                self.output_text += f'{self.output[i]}_({self.parents[i]})\n'
        else:
            for output_line in self.output:
                self.output_text += str(output_line) + '\n'
        self.output_textedit.setText(self.output_text)
        self.parents = None

    def save_output(self):
        print('Saving')
        self.output_path = QFileDialog.getExistingDirectory(self, 'Please Select Directory to Save Output')
        output_filename = f'{self.output_type}_{get_current_date_time()}.txt'
        output_file = os.path.join(self.output_path, output_filename)
        with open(output_file, 'w') as file:
            file.write(self.output_text)

    def set_output_to_input(self):
        print('Filling input box with output results')
        input_text_string = ''
        for input_line in self.output:
            input_text_string += str(input_line) + '\n'
        self.input_textedit.setText(input_text_string)

    def output_similarity_table(self):
        self.secondary_input = self.secondary_input_lineedit.text()
        search_input_list = self.input_textedit.toPlainText().split('\n')
        find_similarity.output_table(self.sql_path, search_input_list, self.secondary_input)


def get_current_date_time():
    _current_date_time = str(datetime.now())
    _current_date_time = _current_date_time.replace(':', '.')
    _current_date_time = _current_date_time.replace(' ', '_')
    _current_date_time = _current_date_time[0:-7]
    return _current_date_time

