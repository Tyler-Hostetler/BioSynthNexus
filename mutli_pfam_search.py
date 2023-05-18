import sqlite3
import os


PROTEIN_NAME = 'DfmD'
PROTEIN_PATH = PROTEIN_NAME
MAIN_PATH = os.getcwd()

OUTPUT_FILE = PROTEIN_NAME + '-Output.txt'
OUTPUT_FILE_PATH = os.path.join(MAIN_PATH,OUTPUT_FILE)

SQL_FILE = PROTEIN_NAME + '.sqlite'
SQL_PATH = os.path.join(MAIN_PATH, PROTEIN_PATH)
SQL_FILE_PATH = os.path.join(SQL_PATH, SQL_FILE)

print(SQL_FILE_PATH)

conn = sqlite3.connect(SQL_FILE_PATH)
cur = conn.cursor()

# Define a list of families
given_families = ['PF13714', 'PF13279', 'PF05853', 'PF11215']
given_families = ('PF13714', 'PF13279', 'PF05853', 'PF11215')



'''
get_accession_from_family = f"""
    SELECT DISTINCT attributes.accession
    FROM attributes
    JOIN neighbors ON attributes.sort_key = neighbors.gene_key
    WHERE neighbors.family IN ({placeholders})
    GROUP BY attributes.accession
    HAVING COUNT(DISTINCT neighbors.family) = {len(given_families)}
"""
'''
'''
get_accession_from_family = f"""
    SELECT DISTINCT attributes.accession
    FROM attributes
    JOIN neighbors ON attributes.sort_key = neighbors.gene_key
    WHERE neighbors.family IN ({placeholders})
        OR neighbors.family LIKE ? OR neighbors.family LIKE ? OR neighbors.family LIKE ?
"""
'''
get_accession_from_family = """
    SELECT DISTINCT attributes.accession
    FROM attributes
    JOIN (SELECT gene_key
    FROM neighbors
    WHERE family LIKE ?)
    AS n ON attributes.sort_key = n.gene_key;
"""

# Construct the list of values to pass to the query
#query_values = given_families + [f'%{family}%' for family in given_families]

#print(query_values)
# Execute the query
#cur.execute(get_accession_from_family, query_values)

# Execute the query
#cur.execute(get_accession_from_family, [given_families,])

#search_pfams = [f"%{fam}%" for fam in given_families]
#print(search_pfams)
#cur.execute(get_accession_from_family, search_pfams)
cur.execute(get_accession_from_family, ('%PF13714%',))
results = cur.fetchall()


search_pfams = ['PF13714', 'PF08448', 'PF00171', 'PF00589']
hits = []

for pfam in search_pfams:
    temp_pfam = f"%{pfam}%"
    cur.execute(get_accession_from_family, (temp_pfam,))
    temp_results = cur.fetchall()
    hits.append([row[0] for row in temp_results])

matches = hits[0]

for index in range(len(hits)):
    matches = set(matches).intersection(hits[index])

print(matches)

for match in matches:
   print(match)

#print(set(hits[0]).intersection(hits[1]))




# Process the results
accessions = [row[0] for row in results]
#print(accessions)
#for acc in accessions:
    #print(acc)
#print('GG')


cur.close()
conn.close()

