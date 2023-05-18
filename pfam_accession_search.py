import sys
import os
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QLineEdit, QTextEdit, QVBoxLayout, \
    QHBoxLayout, QFileDialog
import sqlite3

PROJECT_HOME = os.getcwd()


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("Filter by Pfam")

        # Create Widgets
        self.status_label = QLabel("No Sqlite File Uploaded")
        self.submit_sql = QPushButton("Upload Sqlite File")
        self.pfam_label = QLabel("Enter Pfam: ")
        self.pfam_lineedit = QLineEdit()
        self.search_button = QPushButton("Search")
        self.output_text = QTextEdit()

        self.sql_path = ''

        # Create Layout and add widgets
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.output_text)

        # Inner layout
        inner_layout = QVBoxLayout(self)
        inner_layout.addWidget(self.status_label)
        inner_layout.addWidget(self.submit_sql)
        inner_layout.addWidget(self.pfam_label)
        inner_layout.addWidget(self.pfam_lineedit)
        inner_layout.addWidget(self.search_button)
        inner_layout.addSpacing(200)

        # Add Inner to Outer Layer
        main_layout.addLayout(inner_layout)

        self.setLayout(main_layout)

        self.pfam_lineedit.setEnabled(False)
        self.search_button.setEnabled(False)

        self.submit_sql.clicked.connect(self.sql_file_search)
        self.search_button.clicked.connect(self.search_by_pfam)

    def sql_file_search(self):
        _sql_path = QFileDialog.getOpenFileName(self, 'Please Select Sqlite3 File')
        self.sql_path = _sql_path[0]
        self.status_label.setText('Selected: ' + os.path.basename(self.sql_path))
        self.pfam_lineedit.setEnabled(True)
        self.search_button.setEnabled(True)

    def search_by_pfam(self):
        output = ''
        pfam_input = (f"%{self.pfam_lineedit.text()}%")
        print(pfam_input)
        accessions = parent_accessions_from_pfam(self.sql_path, pfam_input)
        for acc in accessions:
            output += acc + '\n'
        self.output_text.setText(output)


def parent_accessions_from_pfam(_sql_path, pfam):
    conn = sqlite3.connect(_sql_path)
    cur = conn.cursor()
    cur.execute(get_accession_from_family, (pfam,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in results]


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
form.show()
app.exec()
