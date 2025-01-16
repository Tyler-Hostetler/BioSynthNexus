import os
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel, QCheckBox, QPushButton, QComboBox, \
    QFileDialog, QLineEdit
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
import UniProtRequests as upr
import SqlRequests as sqlr
import find_similarity as f_simi



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
        self.similarity_df = None

        # Load UI
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        self.window.setWindowTitle("BioSynthNexus")

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

        # Disable button until user uses the Similarity Function
        self.similarity_button.setEnabled(False)

        # Set Output Type Box to UniProt Options
        self.update_output_combo(0)
        self.output_combo_view = self.output_type_combobox.view()
        self.output_combo_view.setFixedWidth(300)

        self.input_label.setText('Input: UniProt Accession ID(s)')
        self.output_label.setText('Output: FASTA-formatted Protein Sequence(s)')

        # Fill Request Types
        self.request_type_combobox.addItems(['UniProt','Genome Neighborhood Network'])

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


    # Changes items listed in Output Type Combobox based on the Request Type Selected
    def update_output_combo(self, index):
        self.output_type_combobox.clear()
        if index == 0:
            self.output_type_combobox.addItems(upr.REQUEST_TYPES)
        elif index == 1:
            if self.sql_path is not None:
                self.output_type_combobox.addItems(sqlr.REQUEST_TYPES)
                self.output_type_combobox.addItems(f_simi.REQUEST_TYPES)
            else:
                self.sql_button.setStyleSheet("border: 2px solid #ff1744; color: #ff1744")
                self.status_label.setStyleSheet("color: #ff1744")
                self.request_type_combobox.setCurrentIndex(0)

    # Updates the Input and Output Labels to Inform User what to input and what the expected output is
    def selection_hints(self):
        input_hint = 'Input: '
        output_hint = 'Output: '
        request_type = self.request_type_combobox.currentText()
        output_type = self.output_type_combobox.currentText()

        match output_type:
            case 'FASTA':
                input_hint += 'UniProt Accession ID(s)'
                output_hint += 'FASTA-Formatted Protein Sequence(s)'
            case 'Genome Accession ID in GenBank':
                input_hint += 'UniProt Accession ID(s)'
                output_hint += 'Genome Accession ID(s) annotated in GenBank'
            case 'Protein Accession ID in GenBank':
                input_hint += 'UniProt Accession ID(s)'
                output_hint += 'Protein Accession ID(s) annotated in GenBank'
            case 'ORF Name in Corresponding Genome':
                input_hint += 'UniProt Accession ID(s)'
                output_hint += 'Open Reading Frame (ORF) Name in corresponding genome annotated in GenBank'
            case 'Parent Accession ID':
                input_hint += 'Pfam ID(s) of Gene Neighbors'
                output_hint += 'Parent Accessions within Neighborhoods that contain All given Pfam(s)'
            case 'Genome Neighborhood ID':
                input_hint += 'Pfam ID(s) of Gene Neighbors'
                output_hint += 'Genome Neighborhoods that contain All Inputted Pfam(s)'
            case 'Genome Neighborhood Pfams':
                input_hint += 'Individual Genome Neighborhood ID'
                output_hint += 'Pfam(s) for each neighboring gene in given Genome Neighborhood'
            case 'Genome Neighborhood Accessions':
                input_hint += 'Individual Genome Neighborhood ID'
                output_hint += 'Accession ID(s) for each neighboring gene in given Genome Neighborhood'
            case 'Neighboring Gene Accessions by Pfam':
                input_hint += 'Genome Neighborhood IDs and Pfam(Secondary Input)'
                output_hint += 'Accession IDs of neighboring genes containing the specified Pfam ID <br>Accession ID_(Genome Neighborhood ID)'
            case 'Genome Neighborhood Pfam Comparison':
                input_hint += 'Pfam ID(s)<br>Optional: Pre-Filter with a Pfam (Secondary Input)'
                output_hint += 'Genome Neighborhood ID_(Number of Matching Pfams)'


        self.input_label.setText(input_hint)
        self.output_label.setText(output_hint)

    # Prompts User to upload SQLITE File
    def sql_upload(self):
        _sql_path = QFileDialog.getOpenFileName(self, 'Please Select GNN SQLITE File')
        self.sql_path = _sql_path[0]
        print(f"Attempting to Open {self.sql_path}")
        self.status_label.setText('Selected: ' + os.path.basename(self.sql_path))
        self.sql_button.setStyleSheet("border: 2px solid #4dd0e1; color: #4dd0e1")
        self.status_label.setStyleSheet("color: #4dd0e1")

    # Once the User clicks search this function determines request type and output type they requested and handles accordingly
    def search(self):
        print('Searching')
        self.output_type = self.output_type_combobox.currentText()
        self.input = self.input_textedit.toPlainText().split('\n')
        self.secondary_input = self.secondary_input_lineedit.text()
        temp_output = []

        # SQL Requests
        if self.output_type in sqlr.REQUEST_TYPES:
            # Need to determine if user is inputing a single value or a list
            if len(self.input) <= 1:
                self.input = self.input[0]
            temp_output, self.parents = sqlr.get_output(self.sql_path, self.input, self.output_type, self.secondary_input)
        
        # UniProt Requests
        elif self.output_type in upr.REQUEST_TYPES:
            for index, element in enumerate(self.input):

                if element == '':
                    print('Empty')
                    continue

                if self.parents is None:    # Checks if user is using accessions that aren't considered BGC IDs
                    _parents = None
                else:
                    _parents = self.parents[index]


                try:
                    temp_output.append(upr.uniprot_request(element, _parents, self.output_type))
                except:
                    print(f"Request Failed for {element}")
                    continue
        
        # BGC Similarity
        elif self.output_type in f_simi.REQUEST_TYPES:
            self.similarity_df, bgcIDs, true_counts = f_simi.output_table(self.sql_path, self.input, self.secondary_input)
            temp_output = bgcIDs
            self.parents = true_counts
            self.activate_similarity_button()


        self.output = temp_output
        self.fill_output()

    # Fills output field based on output type
    def fill_output(self):
        print('Outputting Search Results')
        self.output_count_label.setText("Count: " + str(len(self.output))) # Provides count of outputs
        self.output_text = ''   # Clears output field

        # Checks if output type is a sql request with parents (BGC IDs associated with accession ID) or its a similarity request (matches are treated as parents)
        if (self.output_type in sqlr.REQUEST_TYPES and self.parents is not None) or self.output_type in f_simi.REQUEST_TYPES:
            for i in range(len(self.output)):
                self.output_text += f'{self.output[i]}_({self.parents[i]})\n'
        else:
            for output_line in self.output:
                self.output_text += str(output_line) + '\n'
        self.output_textedit.setText(self.output_text)
        #self.parents = None

    # Prompts sser to save output field in a directory of their choosing
    def save_output(self):
        output_path, _ = QFileDialog.getSaveFileName(
                        self,
                        "Save Output", # Dialog Title
                        f"{self.output_type}_{get_current_date_time()}.txt", # Default file name
                        "Text Files (*.txt);;All Files (*)"
                        )
        with open(output_path, 'w') as file:
            file.write(self.output_text)

    # Replaces input filed with last generated output, ignores if any parent data is present
    def set_output_to_input(self):
        print('Filling input box with output results')
        input_text_string = ''
        for input_line in self.output:
            input_text_string += str(input_line) + '\n'
        self.input_textedit.setText(input_text_string)

    # Prompts user to save a *.csv similarity table
    def output_similarity_table(self):
        output_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Similarity Table", # Dialog Title
                f"{self.output_type}_{get_current_date_time()}.csv", # Default file name
                "Text Files (*.csv);;All Files (*)"
                )
        f_simi.save_similarity_table(self.similarity_df, output_path)

    # Once the user runs the BGC-PFam-similarity, the option to generate the similarity table *.csv is allowed
    def activate_similarity_button(self):
        self.similarity_button.setEnabled(True)
        self.similarity_button.setStyleSheet("border: 2px solid #4dd0e1; color: #4dd0e1")



def get_current_date_time():
    _current_date_time = str(datetime.now())
    _current_date_time = _current_date_time.replace(':', '.')
    _current_date_time = _current_date_time.replace(' ', '_')
    _current_date_time = _current_date_time[0:-7]
    return _current_date_time

