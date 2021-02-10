from xmldiff import main, formatting
import os
import shutil
import time
import sys
import pandas

path = os.path.dirname(os.path.realpath(sys.argv[0]))


def readConfig():
    fopen = open(path + '\\config.txt', 'r')
    lines = fopen.readlines()

    for row in lines:

        if row.startswith('A_server'):
            A_server_path = row.split('|')[1]
        if row.startswith('B_server'):
            B_server_path = row.split('|')[1]

    fopen.close()

    return A_server_path, B_server_path


def compare_xmls(observed, expected):
    formatter = formatting.DiffFormatter()
    diff = main.diff_files(observed, expected, formatter=formatter)
    return diff


def readFolder(path):
    list = os.listdir(path.replace('\n', ''))
    return list


# def getFile(folder_path):
#
#     for

def strList(result_str):
    list_tmp = result_str.split('\n')
    result_list = []
    flag_5col = False

    for each in list_tmp:
        tmp = each[1:][0: -1].split(',', 4)

        # zip 4 elements
        if len(tmp) > 4:
            tmp = tmp[0:5]
            flag_5col = True
        elif len(tmp) < 4:
            tmp += ['' for i in range(4 - len(tmp))]

        result_list.append(tmp)

    return strDf(result_list, flag_5col)

# list to Dataframe
def strDf(lis, flag_5col=False):
    columns = ['Type', 'Position', 'Property', 'Value']
    if flag_5col:
        columns += ['Backup']
        df_each_file = pandas.DataFrame(lis, columns=columns)
    else:
        df_each_file = pandas.DataFrame(lis, columns=columns)
        df_each_file['Backup'] = ''

    return df_each_file


def main_work():
    A_server_path, B_server_path = readConfig()

    list_A = readFolder(A_server_path)
    list_B = readFolder(B_server_path)
    each_file_A = ''
    each_file_B = ''

    df_result = pandas.DataFrame()
    error = []
    for each_file_A in list_A:
        columns = ['Type_A', 'Position', 'Property', 'Value_A', 'Value_B', 'Backup_A', 'Backup_B']

        try:
            if '.xml' in each_file_A:
                tmp = each_file_A.split('_')
                lot = tmp[0]
                sort = tmp[1]
                file_start = lot + '_' + sort
                each_file_A = A_server_path.replace('\n', '') + '\\' + each_file_A
            # if len([each for each in list_B if each.startswith(file_start)]) == 1:

            tmp = [each for each in list_B if each.startswith(file_start)]
            if len(tmp) == 1:
                each_file_B = tmp[0]
                each_file_B = B_server_path.replace('\n', '') + '\\' + each_file_B

            # B to A
            out_AB = compare_xmls(each_file_A, each_file_B)
            df_AB = strList(out_AB)

            # A to B
            out_BA = compare_xmls(each_file_B, each_file_A)
            df_BA = strList(out_BA)

            df_each_file = pandas.merge(left=df_BA, right=df_AB, on=['Position', 'Property'],
                                        suffixes=('_A', '_B'))

            # if ('Backup' in df_BA.columns) and ('Backup' in df_AB.columns):
            #     columns += ['Backup_A', 'Backup_B']
            # elif ('Backup' in df_BA.columns) and ('Backup' not in df_AB.columns):
            #     columns += ['Backup']
            # elif ('Backup' not in df_BA.columns) and ('Backup' in df_AB.columns):
            #     columns += ['Backup']


            df_each_file = df_each_file[columns]

            df_each_file.rename(columns={'Type_A': 'Type'}, inplace=True)
            df_each_file.insert(0, 'lot_sort', file_start)

            df_result = pandas.concat([df_result, df_each_file])

        except:
            error += [file_start]
            continue

    df_result = df_result.reset_index(drop=True)
    df_result.to_csv('result.csv', index=0)
    df_error = pandas.DataFrame(error)

    if error:
        df_error.to_csv('error.csv', index=0)

    pass
    pass


main_work()
