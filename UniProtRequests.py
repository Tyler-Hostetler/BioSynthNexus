import requests
import re

REQUEST_TYPES = ['FASTA', 'Genome Accession ID in GenBank', 'Protein Accession ID in GenBank', 'ORF Name in Corresponding Genome']


def uniprot_request(protein_aID, parent=None, request_type=None):
	flatfile_content = fetch_protein_flatfile(protein_aID)
	output = extract_information(flatfile_content)

	match request_type:
		case 'FASTA':
			if parent is None:
				return f">{protein_aID}\n{output['Sequence']}"
			else:
				return f">{protein_aID}_({parent})\n{output['Sequence']}"
		case 'Genome Accession ID in GenBank':
			return output['Genome ID']
		case 'Protein Accession ID in GenBank':
			return output['Protein ID']
		case "ORF Name in Corresponding Genome":
			return output['ORF']


# Fetches EMBL flatfile using EBI API
def fetch_protein_flatfile(accession_id):

	base_url = "https://www.ebi.ac.uk/proteins/api/proteins/"
	request_url = f"{base_url}{accession_id}"

	try:
		# Send the request
		response = requests.get(request_url, headers={"Accept": "text/x-flatfile"})
		response.raise_for_status()
		return response.text  # Return the flatfile content

	except requests.exceptions.RequestException:
		return (f"Error fetching data for {accession_id}")

# Extracts relavant information from flatfile
def extract_information(flatfile_content):

	# Define regex patterns for the fields
	embl_pattern = re.compile(r"DR\s+EMBL;\s+([A-Z0-9]+);")
	protein_id_pattern = re.compile(r"DR\s+EMBL;\s+\S+;\s+([A-Z0-9_.]+);")
	sequence_pattern = re.compile(r"SQ\s+SEQUENCE.+\n([\s\S]+)")
	orf_pattern = re.compile(r"(?:ORFNames|OrderedLocusNames)=([A-Za-z0-9_]+)\s?")


	# Extract EMBL ID
	embl_match = embl_pattern.search(flatfile_content)
	embl_id = embl_match.group(1) if embl_match else "Not found"

	# Extract Protein ID
	protein_id_match = protein_id_pattern.search(flatfile_content)
	protein_id = protein_id_match.group(1) if protein_id_match else "Not found"

	# Extract sequence
	sequence_match = sequence_pattern.search(flatfile_content)
	sequence = sequence_match.group(1).replace("\n", "").replace(" ", "").replace("//", "") if sequence_match else "Not found"

	# Extract ORF Name
	orf_match = orf_pattern.search(flatfile_content)
	orf_id = orf_match.group(1) if orf_match else "Not found"

	return {
		"Genome ID": embl_id,
		"Protein ID": protein_id,
		"ORF": orf_id,
		"Sequence": sequence.strip() if sequence != "Not found" else sequence
    		}