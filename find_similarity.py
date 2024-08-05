from more_itertools import distinct_combinations
import SqlRequests as sql
import pandas as pd


def output_table(sql_path, pfam_list, secondary_input):
    pep_accessions = get_accessions_from_single_list(sql_path, [], secondary_input)[0]
    match_list = {}
    for pfam in pfam_list:
        acc_match = get_accessions_from_single_list(sql_path, [pfam], secondary_input)[0]
        match_list.update({pfam: acc_match})

    print(f"PfamList: {pfam_list}\n Pep-Accessions: {pep_accessions}\nMatch_list: {match_list}")

    compare_list = []
    for group in match_list:
        true_false_list = []
        for acc in pep_accessions:
            if acc in match_list[group]:
                true_false_list.append('True')
            else:
                true_false_list.append('False')
        compare_list.append(true_false_list)

    df = pd.DataFrame(compare_list, columns=pep_accessions, index=match_list.keys())
    transposed_df = df.transpose()
    transposed_df.to_csv('similarity.csv', index=True)


def get_all_combinations(_search_list):
    combination_list = []
    for r in range(1, len(_search_list) + 1):
        combination_list.extend(distinct_combinations(_search_list, r))
    return combination_list


def get_accessions_from_single_list(sql_path, pfam_list, secondary_input):
    pfam_list.append(secondary_input)
    accessions = sql.get_output(sql_path, pfam_list, 'Accession', secondary_input)
    return accessions




