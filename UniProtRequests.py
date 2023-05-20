import requests


def uniprot_request(protein_aID, output_type=None):
	url = 'https://rest.uniprot.org/uniprotkb/' + protein_aID + '?format=json'
	uniprotdata = requests.get(url)
	gene_bank_id = uniprotdata.json()['uniProtKBCrossReferences'][0]['id']
	gene_bank_name = uniprotdata.json()['uniProtKBCrossReferences'][0]['properties'][0]['value']
	fasta = uniprotdata.json()['sequence']['value']

	match output_type:
		case None:
			return gene_bank_id, gene_bank_name, fasta
		case "GenBankID":
			return gene_bank_id
		case "GenBank Protein Name":
			return gene_bank_name
		case "Sequence":
			return fasta


# Testing
'''
protein_accession = 'A0A5E9UHV6'
gene_bank_id, gene_bank_name, fasta = uniprot_request(protein_accession)
print(gene_bank_id)
'''