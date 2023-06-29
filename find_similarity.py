from more_itertools import distinct_combinations
import SqlRequests as sql
import pandas as pd

def output_table(sql_path, pfam_list):
    print()
    pep_accessions, pep_num = get_accessions_from_single_list(SQL_PATH, [])


def get_all_combinations(_search_list):
    combination_list = []
    for r in range(1, len(_search_list) + 1):
        combination_list.extend(distinct_combinations(_search_list, r))
    return combination_list


def get_accessions_from_single_list(sql_path, pfam_list):
    pfam_list.append('PF13714')
    accessions = sql.get_output(sql_path, pfam_list, 'PFam')
    num_accessions = len(accessions)
    return accessions, num_accessions


SQL_PATH = 'C:\\Users\\tyler\OneDrive - North Carolina State University\\Research\\Programming\\SNN_GNN_Access\\FfnD\\FfnD.sqlite'
SQL_PATH = 'FfnD\\FfnD.sqlite'
SQL_PATH = 'DhpA\\DhpA.sqlite'
search_list = ['PF00067', 'PF02775', 'PF00248', 'PF05426', 'PF01055']
search_list = ['PF02595', 'PF02615', 'PF00155', 'PF02775', 'PF00465', 'PF00266', 'PF13649']
match_list = {}
pep_accessions, pep_num = get_accessions_from_single_list(SQL_PATH, [])
pfam_combo = get_all_combinations(search_list)
print(pfam_combo)


for pfam in search_list:
    acc_match, acc_num = get_accessions_from_single_list(SQL_PATH, [pfam])
    match_list.update({pfam:acc_match})

#print(match_list)


#print(match_list.keys())

df = pd.DataFrame(columns=pep_accessions, index=match_list.keys())

for group in match_list:
    for acc in pep_accessions:
        if acc in match_list[group]:
            df.at[group, acc] = True
        else:
            df.at[group, acc] = False

#print(df)
transposed_df = df.transpose()
transposed_df.to_csv('similarity.csv', index=True)


# class Similarity:
#     def __init__(self, sql_path, pfam_search_list):
#         self.sql_path = sql_path
#         self.search_list = pfam_search_list
#         self.combination_list = []
#
#     def get_all_combinations(self):
#         for r in range(1, len(self.search_list) + 1):
#             self.combination_list.extend(distinct_combinations(self.search_list, r))
#         return self.combination_list
#
#     def get_hits_from_one_set(self):
#         print()

# for pfam_list in pfam_combo:
#     temp_search = []
#     pfam_name = ''
#     for pfam in pfam_list:
#         temp_search.append(pfam)
#         pfam_name += f"|{pfam}|"
#     acc_match, acc_num = get_accessions_from_single_list(SQL_PATH, temp_search)
#
#     match_list.update({pfam_name: acc_match})



