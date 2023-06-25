import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QLineEdit, QTextEdit, QVBoxLayout, \
    QHBoxLayout, QFileDialog, QSizePolicy, QComboBox, QCheckBox
import sqlite3

import UniProtRequests as upr



PROJECT_HOME = os.getcwd()

logo = """   ______   _   __   _   __
  / ____/  / | / /  / | / /
 / / __   /  |/ /  /  |/ /
/ /_/ /  / /|  /  / /|  /
\____/__/_/ |_/  /_/ |_/      __       __             ____  ____
  / ___/___  ____ ___________/ /_     / /_  __  __   / __ \/ __/___ _____ ___
  \__ \/ _ \/ __ `/ ___/ ___/ __ \   / __ \/ / / /  / /_/ / /_/ __ `/ __ `__ \\
 ___/ /  __/ /_/ / /  / /__/ / / /  / /_/ / /_/ /  / ____/ __/ /_/ / / / / / /
/____/\___/\__,_/_/   \___/_/ /_/  /_.___/\__, /  /_/   /_/  \__,_/_/ /_/ /_/
                                         /____/
  """
print(logo)


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("Filter by Pfam")

        # Initialize Variables
        self.current_input_type = None
        self.current_output_type = None
        self.current_output = None

        # Create Widgets
        # Sql Submission
        self.status_label = QLabel("No Sqlite File Uploaded")
        self.submit_sql = QPushButton("Upload Sqlite File")
        self.sql_path = ''

        # Input
        self.input_label = QLabel("Select Search Type: ")
        self.input_type = QComboBox()
        self.input_lineedit = QLineEdit()
        self.use_output = QCheckBox('Use Output as Input')

        # Output
        self.output_label = QLabel("Select Output Type")
        self.output_type = QComboBox()
        self.search_button = QPushButton("Search")
        self.output_text = QTextEdit()
        self.save_button = QPushButton("Save")

        self.status_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Create Layout and add widgets
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.output_text)

        # Inner layout
        inner_layout = QVBoxLayout(self)
        inner_layout.addWidget(self.status_label)
        inner_layout.addWidget(self.submit_sql)
        inner_layout.addWidget(self.input_label)
        inner_layout.addWidget(self.input_type)
        inner_layout.addWidget(self.input_lineedit)
        inner_layout.addWidget(self.output_label)
        inner_layout.addWidget(self.output_type)
        inner_layout.addWidget(self.search_button)
        inner_layout.addWidget(self.use_output)
        #inner_layout.addSpacing(200)
        inner_layout.addWidget(self.save_button)

        # x1 = self.status_label.sizeHint().width()
        # y1 = self.status_label.sizeHint().height()
        # x2 = inner_layout.totalSizeHint().width()
        # y2 = inner_layout.totalSizeHint().height()
        # print(x1)
        # print(y1)
        # self.status_label.setMaximumSize(x2, y2)

        # Add Inner to Outer Layer
        main_layout.addLayout(inner_layout)

        # Initialize
        self.setLayout(main_layout)
        self.save_button.setEnabled(False)
        self.search_button.setDefault(True)

        # Input and Output Types
        self.input_type.addItems(['Pfam', 'Accession'])
        self.output_type.addItems(['Accession', 'Pfam', 'GenBankID', 'GenBank Protein Name', 'Sequence', 'ALL'])

        # Button Actions
        self.submit_sql.clicked.connect(self.sql_file_search)
        self.search_button.clicked.connect(self.search)
        self.save_button.clicked.connect(self.save_output)

        self.show()

    def sql_file_search(self):
        _sql_path = QFileDialog.getOpenFileName(self, 'Please Select Sqlite3 File')
        self.sql_path = _sql_path[0]
        self.status_label.setText('Selected: ' + os.path.basename(self.sql_path))

    def search(self):
        # Checks if input is from previous output
        if self.use_output.isChecked():
            self.search_by_output()
            return

        search_input_type = self.input_type.currentText()
        raw_text = self.input_lineedit.text()
        if ',' in raw_text:
            print(f'Searching a List of {search_input_type}s')
            self.search_by_input_list()
        else:
            print(f'Searching a Single {search_input_type}')
            self.search_by_input()

    def search_by_input(self):
        search_input = f"%{self.input_lineedit.text()}%"
        search_input = search_input.replace(" ", "")
        search_input_type = self.input_type.currentText()
        print(search_input)
        match search_input_type:
            case 'Pfam':
                output = parent_accessions_from_input(self.sql_path, search_input)
            case 'Accession':
                output = 'Accession'


        # accessions = parent_accessions_from_input(self.sql_path, search_input)
        # self.fill_output(accessions)
        self.fill_output(output)

    def search_by_input_list(self):
        input_list = self.input_lineedit.text()
        input_list = input_list.replace(" ", "")
        search_list = input_list.split(',')
        print(f"List Search Criteria: {search_list}")
        accessions = parent_accessions_from_input_list(self.sql_path, search_list)
        self.fill_output(accessions)

    def search_by_output(self):
        print('Using Output as Input')
        output = []
        if self.current_output_type == 'Accession':
            print(self.current_output)
            for element in self.current_output:
                print(f"Requesting: {element} {self.output_type.currentText()}")
                try:
                    temp_out = upr.uniprot_request(element, self.output_type.currentText())
                except:
                    print(f"Request Failed for {element}")
                    continue

                if self.output_type.currentText() == 'Sequence':
                    temp_out = f">{element}\n" + temp_out

                output.append(temp_out)

            self.fill_output(output)




    def fill_output(self, _output):
        output_text_string = ''
        self.current_output = _output
        for element in _output:
            output_text_string += element + '\n'
        self.output_text.setText(output_text_string)
        self.save_button.setEnabled(True)
        self.current_output_type = self.output_type.currentText()

    def save_output(self):
        output_file = 'temporary_output.txt'
        with open(output_file, 'w') as file:
            file.write(self.output_text.toPlainText())
        print(self.output_text.toPlainText())
        subprocess.Popen(["notepad.exe", output_file])


def parent_accessions_from_input(_sql_path, input):
    conn = sqlite3.connect(_sql_path)
    cur = conn.cursor()
    cur.execute(get_accession_from_family, (input,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in results]


def parent_accessions_from_input_list(_sql_path, input_list):
    # Connects to Sqlite file
    conn = sqlite3.connect(_sql_path)
    cur = conn.cursor()

    # Gets all accessions for each Pfam search independently
    hits = []
    for input in input_list:
        temp_input = f"%{input}%"
        cur.execute(get_accession_from_family, (temp_input,))
        temp_results = cur.fetchall()
        hits.append([row[0] for row in temp_results])

    # Finds matching accessions within all accession lists within hits
    matches = hits[0]
    for index in range(len(hits)):
        matches = set(matches).intersection(hits[index])

    cur.close()
    conn.close()
    return matches


get_accession_from_family = """
                            SELECT DISTINCT attributes.accession
                            FROM attributes
                            JOIN (SELECT gene_key
                            FROM neighbors
                            WHERE family LIKE ?)
                            AS n ON attributes.sort_key = n.gene_key;
                            """

app = QApplication(sys.argv)
form = Form()
app.exec()
