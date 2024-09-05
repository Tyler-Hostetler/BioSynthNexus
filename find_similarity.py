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
                true_false_list.append('TRUE')
            else:
                true_false_list.append('FALSE')
        compare_list.append(true_false_list)

    df = pd.DataFrame(compare_list, columns=pep_accessions, index=match_list.keys())
    df = df.transpose()

    # Create a column the number of PFams a BGC has similar to the searched PFams
    df['TRUE Count'] = (df == 'TRUE').sum(axis=1)
    df_sorted = df.sort_values(by='TRUE Count', ascending=False)
    df_sorted = df_sorted.reset_index()
    df_sorted.to_csv('similarity.csv', index=False)


def get_all_combinations(_search_list):
    combination_list = []
    for r in range(1, len(_search_list) + 1):
        combination_list.extend(distinct_combinations(_search_list, r))
    return combination_list


def get_accessions_from_single_list(sql_path, pfam_list, secondary_input):
    pfam_list.append(secondary_input)
    accessions = sql.get_output(sql_path, pfam_list, 'Accession', secondary_input)
    return accessions




