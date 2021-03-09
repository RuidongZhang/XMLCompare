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
    # diff_options: A dictionary containing options that will be passed into the Differ(): F: A value between 0 and 1
    # that determines how similar two XML nodes must be to match as the same in both trees. Defaults to 0.5.
    #
    # A higher value requires a smaller difference between two nodes for them to match. Set the value high,
    # and you will see more nodes inserted and deleted instead of being updated. Set the value low, and you will get
    # more updates instead of inserts and deletes.
    #
    # uniqueattrs: A list of XML node attributes that will uniquely identify a node. See Unique Attributes for more
    # info.
    #
    # Defaults to ['{http://www.w3.org/XML/1998/namespace}id'].
    #
    # ratio_mode:
    #
    # The ratio_mode determines how accurately the similarity between two nodes is calculated. The choices are
    # 'accurate', 'fast' and 'faster'. Defaults to 'fast'.
    #
    # Using 'faster' often results in less optimal edits scripts, in other words, you will have more actions to
    # achieve the same result. Using 'accurate' will be significantly slower, especially if your nodes have long
    # texts or many attributes.
    diff = main.diff_files(observed, expected,diff_options={'F': 0.5, 'ratio_mode': 'accurate'}, formatter=formatter)
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


def source_file_get(file_path):
    file_type = get_type(file_path)

    os.rename(file_path, file_path.replace(file_type, 'txt'))

    fopen = open(file_path.replace(file_type, 'txt'), 'r', encoding='utf-8')

    # blank list without seek
    fopen.seek(0, 0)
    lines = fopen.readlines()

    for row in lines:
        if 'FileName=' in row:
            tmp = row.split('FileName=')[1]
            tmp = tmp.split('"')[1]
            tmp = ''.join(tmp.split('.')[0:-1])
            fopen.close()
            os.rename(file_path.replace(file_type, 'txt'), file_path)

            return tmp


def get_type(file_path):
    if '.xml' in file_path:
        file_type = 'xml'
    elif '.e142' in file_path:
        file_type = 'e142'
    else:
        file_type = file_path.split('.')[-1]

    return file_type


def main_work():
    A_server_path, B_server_path = readConfig()

    list_A = readFolder(A_server_path)
    list_B = readFolder(B_server_path)
    list_A.sort()
    list_B.sort()
    each_file_A = ''
    each_file_B = ''

    df_result = pandas.DataFrame()
    error = []
    for each_file_A in list_A:
        columns = ['Type_B', 'Position', 'Property', 'Value_A', 'Value_B', 'Backup_A', 'Backup_B']

        try:
            file_type = get_type(each_file_A)

            if file_type in each_file_A:
                tmp = each_file_A.split('_')
                lot = tmp[0]

                sort = tmp[1]
                if len(tmp) == 5:
                    sort += '_' + tmp[2]
                file_start = lot + '_' + sort
                each_file_A = A_server_path.replace('\n', '') + '\\' + each_file_A

                # same lot and sort but multiple files
                tmp_A = [each for each in list_A if each.startswith(file_start)]
                tmp_B = [each for each in list_B if each.startswith(file_start)]

                # position_A = tmp_A.index(each_file_A)
                source_file_name_A = ''
                source_file_name_B = ''
                if len(tmp_A) > 1 or len(tmp_B) > 1:
                    source_file_name_A = source_file_get(each_file_A)

                if len(tmp_B) == 1:
                    each_file_B = tmp_B[0]
                    each_file_B = B_server_path.replace('\n', '') + '\\' + each_file_B
                    if len(tmp_A) > 1:
                        source_file_name_B = source_file_get(each_file_B)

                if len(tmp_B) > 1:
                    for each_file_B in tmp_B:
                        each_file_B = B_server_path.replace('\n', '') + '\\' + each_file_B
                        source_file_name_B = source_file_get(each_file_B)
                        if source_file_name_A == source_file_name_B:
                            break

                if source_file_name_A != source_file_name_B:
                    error += [file_start]
                    continue

                if file_type != 'xml':
                    os.rename(each_file_A, each_file_A.replace(file_type, 'xml'))
                    os.rename(each_file_B, each_file_B.replace(file_type, 'xml'))
                    each_file_A = each_file_A.replace(file_type, 'xml')
                    each_file_B = each_file_B.replace(file_type, 'xml')

                # B to A
                out_AB = compare_xmls(each_file_A, each_file_B)
                df_AB = strList(out_AB)

                # A to B
                out_BA = compare_xmls(each_file_B, each_file_A)
                df_BA = strList(out_BA)

                if file_type != 'xml':
                    os.rename(each_file_A, each_file_A.replace('xml', file_type))
                    os.rename(each_file_B, each_file_B.replace('xml', file_type))

                df_each_file = pandas.merge(left=df_BA, right=df_AB, on=['Position', 'Property'],
                                            suffixes=('_A', '_B'),how='left')

                # if ('Backup' in df_BA.columns) and ('Backup' in df_AB.columns):
                #     columns += ['Backup_A', 'Backup_B']
                # elif ('Backup' in df_BA.columns) and ('Backup' not in df_AB.columns):
                #     columns += ['Backup']
                # elif ('Backup' not in df_BA.columns) and ('Backup' in df_AB.columns):
                #     columns += ['Backup']

                df_each_file = df_each_file[columns]

                df_each_file.rename(columns={'Type_B': 'Type'}, inplace=True)
                df_each_file.insert(0, 'lot_sort', file_start)
                if source_file_name_A:
                    df_each_file['Backup_A'] = source_file_name_A

                df_result = pandas.concat([df_result, df_each_file])



        except:
            error += [file_start]
            # error += [each_file_A.split('\\')[-1]]

            continue

    now = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))  # Time now
    report_name = 'Result - ' + now + '.csv'

    df_result = df_result.reset_index(drop=True)
    df_result.to_csv(report_name, index=False)
    df_error = pandas.DataFrame(error)

    if error:
        report_name = 'Error - ' + now + '.csv'

        df_error.to_csv(report_name, index=False)

    pass
    pass


main_work()
