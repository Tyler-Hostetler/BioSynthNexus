import sqlite3
import os
import pandas as pd

PROTEIN_NAME = 'FfnD'
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


#Gets accession and gene key from a given Pfam
# Accession and gene key of the homologs of the initial protein
# .neighbors.gene_key = .attributes.sort_key
accession_gene_key_query = 	"""
							SELECT DISTINCT attributes.accession, neighbors.gene_key
							FROM attributes
							JOIN neighbors ON attributes.sort_key = neighbors.gene_key
							WHERE neighbors.family = ?
							"""


# Gets the pfams from 
get_family_from_family = """
				        SELECT DISTINCT neighbors.family
				        FROM neighbors
				        JOIN (
				            SELECT gene_key
				            FROM neighbors
				            WHERE family = ?
				        ) AS n ON neighbors.gene_key = n.gene_key
				        """

get_accession_from_family = """
							SELECT DISTINCT attributes.accession
							FROM attributes
							JOIN (SELECT gene_key
							FROM neighbors
							WHERE family = ?)
							AS n ON attributes.sort_key = n.gene_key;
							"""
'''
Gets the accessions from a given Pfam
Finds proteins in .neighbors which contain a given pfam
Uses each protein's gene_key to use as a reference to sort_key in .attributes
Finds the parent proteins (homologs of the initial) via
.neighbors.gene_key = .attributes.sort_key
'''


#Gets 
# .neighbors.gene_key = .attributes.sort_key
get_gene_key_from_family = 	"""
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


def get_query_results(query_input, index):
	cur.execute(query_input, (index,))
	results = cur.fetchall()
	return [row[0] for row in results]


family_index = 'PF13714'
parent_accessions = get_query_results(get_accession_from_family, family_index)
parent_gene_keys = get_query_results(get_gene_key_from_family, family_index)
#parent_families = get_query_results(get_family_from_family, family_index)

gene_key_index = '51'
local_neighborhood = get_query_results(get_local_neighborhood_from_gene_key, (gene_key_index))

#print(local_neighborhood)

accession_neighborhoods = []
for gene_code in parent_gene_keys:
	temp_neighborhood = get_query_results(get_local_neighborhood_from_gene_key, (gene_code))
	accession_neighborhoods.append(temp_neighborhood)

target_pfams = accession_neighborhoods[0][8:13]
#print(target_pfams)




#Pandas Testing
data = {
	"homolog_accession": parent_accessions,
	"neighbors_pfam": accession_neighborhoods
}

df = pd.DataFrame(data)

def has_common_neighbors(neighbors, criteria):
	count = 0
	for neighbor in neighbors:
		if neighbor in criteria:
			count += 1
		if count >= 2:
			return True
	return False

def matches_criteria(row, criteria):
    num_matches = 0
    for neighbor in row["neighbors_pfam"]:
        if neighbor in criteria:
            num_matches += 1
    return num_matches / len(row["neighbors_pfam"]) * 100


def matches_criteria(row, criteria):
    count = sum(neighbor in row["neighbors_pfam"] for neighbor in criteria)
    return count / len(criteria) * 100



criteria = accession_neighborhoods[0][7:14]
#print(criteria)

#df["common_neighbors"] = df["neighbors_pfam"].apply(lambda x: has_common_neighbors(x, criteria))
df["matches_criteria"] = df.apply(matches_criteria, args=(criteria,), axis=1)

#Output as table in html
table = df.to_html(index=False)
with open('output_table.html', 'w') as html_file:
	html_file.write(table)




'''
matching_accessions = []
hits = []

index_counter = 0
identical_count = 0

for neighbors in accession_neighborhoods:
	for pfams in neighbors:
		for target in target_pfams:
			if target in pfams:
				if parent_accessions[index_counter] not in matching_accessions:
					matching_accessions.append(parent_accessions[index_counter])
				else:
					identical_count += 1

	#print(identical_count)
	identical_count = 0
	index_counter += 1
'''

#print(matching_accessions)
#print(len(matching_accessions))
#print(hits)


'''
with open(OUTPUT_FILE_PATH, 'w') as output_file:
	for accession_hits in matching_accessions:
		output_file.write(accession_hits + '\n')
'''


cur.close()
conn.close()

'''

previous = None
for neighbors in accession_neighborhoods:
	for pfams in neighbors:
		if pfams in target_pfams:
			if not previous == parent_accessions[index_counter]:
				matching_accessions.append(parent_accessions[index_counter])
			else:
				identical_count += 1
				hits.append(identical_count)

			previous = parent_accessions[index_counter]
	identical_count = 0
	index_counter += 1

	'''


