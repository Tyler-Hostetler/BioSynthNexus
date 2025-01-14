from more_itertools import distinct_combinations
import SqlRequests as sql
import pandas as pd

REQUEST_TYPES = ['Genome Neighborhood Pfam Comparison']

def output_table(sql_path, pfam_list, secondary_input):
    bgc_accessions = get_accessions_from_single_list(sql_path, [], secondary_input)[0] # Gets a list of BGC IDs to search through
    match_list = {}
    for pfam in pfam_list: # For each PFam listed in input, they are individually searched within the given BGC list
        acc_match = get_accessions_from_single_list(sql_path, [pfam], secondary_input)[0]
        match_list.update({pfam: acc_match})

    #print(f"PfamList: {pfam_list}\n Pep-Accessions: {bgc_accessions}\nMatch_list: {match_list}")

    # Determines what PFams are found in which BGCs
    compare_list = []
    for group in match_list:
        true_false_list = []
        for acc in bgc_accessions:
            if acc in match_list[group]:
                true_false_list.append('TRUE')
            else:
                true_false_list.append('FALSE')
        compare_list.append(true_false_list)

    df = pd.DataFrame(compare_list, columns=bgc_accessions, index=match_list.keys())
    df = df.transpose()

    # Create a column the number of PFams a BGC has similar to the searched PFams
    df['TRUE Count'] = (df == 'TRUE').sum(axis=1)
    df_sorted = df.sort_values(by='TRUE Count', ascending=False)
    df_sorted = df_sorted.reset_index()
    #df_sorted.to_csv('similarity.csv', index=False)

    bgc_ids = df_sorted.iloc[:,0].tolist()
    true_counts = df_sorted['TRUE Count'].tolist()


    return df_sorted, bgc_ids, true_counts


def save_similarity_table(simi_df, file_path):
    simi_df.to_csv(file_path, index=False)


# Gets the BGCs that contain a PFam and optionally contain a standard PFam(inputed as the secondary input)
def get_accessions_from_single_list(sql_path, pfam_list, secondary_input):
    pfam_list.append(secondary_input)
    accessions = sql.get_output(sql_path, pfam_list, 'Accession', secondary_input)
    return accessions




