from more_itertools import distinct_combinations
import SqlRequests as sql
import pandas as pd


def output_table(sql_path, pfam_list):
    pep_accessions = get_accessions_from_single_list(sql_path, [])
    match_list = {}
    for pfam in pfam_list:
        acc_match = get_accessions_from_single_list(sql_path, [pfam])
        match_list.update({pfam: acc_match})

    print(f"PfamList: {pfam_list}\n Pep-Accessions: {pep_accessions}\nMatch_list: {match_list}")

    df = pd.DataFrame(columns=pep_accessions, index=match_list.keys())

    for group in match_list:
        for acc in pep_accessions:
            if acc in match_list[group]:
                df.at[group, acc] = True
            else:
                df.at[group, acc] = False

    transposed_df = df.transpose()
    transposed_df.to_csv('similarity.csv', index=True)


def get_all_combinations(_search_list):
    combination_list = []
    for r in range(1, len(_search_list) + 1):
        combination_list.extend(distinct_combinations(_search_list, r))
    return combination_list


def get_accessions_from_single_list(sql_path, pfam_list):
    pfam_list.append('PF13714')
    accessions = sql.get_output(sql_path, pfam_list, 'Accession')
    return accessions




