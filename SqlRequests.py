import sqlite3
import collections


REQUEST_TYPES = ['PFam', 'Accession', 'BGC - P', 'BGC - A']
SQL_FILE_PATH = None


def get_output(sql_file, search_index, search_type):
    global SQL_FILE_PATH
    SQL_FILE_PATH = sql_file
    output = None
    # if '\n' in search_index:
    #     print("Searching Entry List")
    #     list = True
    #     output_type = "L_" + output_type
    # else:
    #     print("Searching Entry")


    print(f"Search Type is: {search_type} and Search Index is: {search_index}")
    print(type(search_index))


    if search_type == 'PFam' and isinstance(search_index, list):
        print("Searching by Pfam List")
        search_type = "L_" + search_type
    else:
        print("Searching By Individual Pfam")

    match search_type:
        case 'PFam':
            print('Searching by Individual Pfam')
            output = parent_accessions_from_pfam(SQL_FILE_PATH, search_index)
        case 'L_PFam':
            print('Searching by Multi-Pfam')
            output = parent_accessions_from_input_list(SQL_FILE_PATH, search_index)
        case 'Accession':
            print()
        case 'BGC - P':
            print('Search BGC by Parent Accession')
            output = accessions_in_cluster(search_index)
        case 'BGC - A':
            print()

    return output


def parent_accessions_from_pfam(_sql_path, pfam):
    pfam = f"%{pfam}%"
    conn = sqlite3.connect(_sql_path)
    cur = conn.cursor()
    cur.execute(get_accession_from_family, (pfam,))
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
    for element in input_list:
        temp_input = f"%{element}%"
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


def accessions_in_cluster(search_input):
    return get_query_results(get_bgc_accessions_from_parent_accession, search_input)


def get_query_results(query_input, element):
    conn = sqlite3.connect(SQL_FILE_PATH)
    cur = conn.cursor()
    cur.execute(query_input, (element,))
    results = cur.fetchall()
    print(results)
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


get_bgc_accessions_from_parent_accession = """
    SELECT DISTINCT n.accession
    FROM neighbors AS n
    JOIN attributes AS a ON n.gene_key = a.sort_key
    WHERE a.accession = ?
"""

get_bgc_accessions_from_other_accession = """
    SELECT DISTINCT accession
    FROM neighbors
    WHERE gene_key = (
        SELECT gene_key
        FROM neighbors
        WHERE accession = ?)
"""


get_accessions_from_bgc = """
SELECT DISTINCT neighbors.accessions
FROM 
                        
                         
                         
                          """


get_gene_key_from_family = """
SELECT DISTINCT neighbors.gene_key
FROM attributes
JOIN neighbors ON attributes.sort_key = neighbors.gene_key
WHERE neighbors.family = ?
"""

get_local_neighborhood_from_gene_key = """
SELECT DISTINCT neighbors.family
FROM neighbors
WHERE neighbors.gene_key = ?
"""

