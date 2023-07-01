import sqlite3


REQUEST_TYPES = ['PFam', 'Accession', 'BGC - Pfam', 'BGC - Accession']
SQL_FILE_PATH = None


def get_output(sql_file, search_index, search_type):
    global SQL_FILE_PATH
    SQL_FILE_PATH = sql_file
    output = None

    print(f"Search Type is: {search_type} and Search Index is: {search_index}")

    if search_type == 'Accession' and isinstance(search_index, list):
        search_type = "L_" + search_type

    match search_type:
        case 'Accession':
            print('Searching by Individual Pfam')
            output = parent_accessions_from_pfam(SQL_FILE_PATH, search_index)
        case 'L_Accession':
            print('Searching by Multi-Pfam')
            output = parent_accessions_from_input_list(SQL_FILE_PATH, search_index)
        case 'PFam':
            print()
        case 'BGC - Pfam':
            print('Search BGC by Parent Accession giving Pfams')
            output = pfams_in_cluster(search_index)
        case 'BGC - Accession':
            print('Search BGC by Parent Accession, giving Accessions')
            output = accessions_in_cluster(search_index)

    return sorted(output)


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


def pfams_in_cluster(search_input):
    return get_query_results(get_bgc_pfams_from_parent_accession, search_input)


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

get_bgc_pfams_from_parent_accession = """
    SELECT DISTINCT n.family
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

