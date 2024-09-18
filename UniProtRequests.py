import requests

REQUEST_TYPES = ['FASTA', 'GenBankID', 'GenBank_Protein_ID', 'GenBank_ORF_ID']

# Handles uniprot requests made by user
def uniprot_request_v2(protein_aID, parent=None, request_type=None):
	print(protein_aID)
	url = 'https://rest.uniprot.org/uniprotkb/' + protein_aID + '?format=json'
	uniprotdata = requests.get(url)
	gene_bank_id = uniprotdata.json()['uniProtKBCrossReferences'][0]['id']
	gene_bank_name = uniprotdata.json()['uniProtKBCrossReferences'][0]['properties'][0]['value']
	gene_orf_id = uniprotdata.json()['genes'][0]['orfNames'][0]['value']
	fasta = uniprotdata.json()['sequence']['value']

	match request_type:
		case None:
			return 'Nothing Requested'
		case 'ALL':
			return gene_bank_id, gene_bank_name, fasta
		case "GenBankID":
			return gene_bank_id
		case "GenBank_Protein_ID":
			return gene_bank_name
		case "GenBank_ORF_ID":
			return gene_orf_id
		case "FASTA":
			if parent is None:
				return f">{protein_aID}\n{fasta}"
			else:
				return f">{protein_aID}_({parent})\n{fasta}"

