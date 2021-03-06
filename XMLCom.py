from xmldiff import main, formatting
import os
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
        if row.startswith('Output'):
            output_path = row.split('|')[1].rstrip('\n')
        if row.startswith('Start_time'):
            start_time = row.split('|')[1].rstrip('\n')
            start_time = time.mktime(time.strptime(start_time, "%Y-%m-%d"))
            start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        if row.startswith('End_time'):
            end_time = row.split('|')[1].rstrip('\n')
            if 'now' in end_time:
                end_time = 'now'
            else:
                end_time = time.mktime(time.strptime(end_time, "%Y-%m-%d"))
                end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))

    fopen.close()

    return A_server_path, B_server_path, output_path, start_time, end_time


def compare_xmls(observed, expected):
    formatter = formatting.DiffFormatter()
    # FYI: https://xmldiff.readthedocs.io/en/stable
    #
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
    diff = main.diff_files(observed, expected, diff_options={'F': 0.5, 'ratio_mode': 'accurate',
                                                             'uniqueattrs': [('RuleEvaluation', 'Name')]},
                           formatter=formatter)
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

    # os.rename(file_path, file_path.replace(file_type, 'txt'))

    fopen = open(file_path, 'r', encoding='utf-8')

    # blank list without seek
    fopen.seek(0, 0)
    lines = fopen.readlines()

    for row in lines:
        if 'FileName=' in row:
            tmp = row.split('FileName=')[1]
            tmp = tmp.split('"')[1]
            tmp = ''.join(tmp.split('.')[0:-1])
            fopen.close()
            # os.rename(file_path.replace(file_type, 'txt'), file_path)

            return tmp

    return ''

def get_type(file_path):
    if '.xml' in file_path:
        file_type = 'xml'
    elif '.e142' in file_path:
        file_type = 'e142'
    else:
        file_type = file_path.split('.')[-1]

    return file_type

def copyfile(src_file,dst_dir,file_type):
    import shutil

    dst = dst_dir.rstrip('\n') + '\\' + src_file.split('\\')[-1].replace(file_type,'xml')
    shutil.copyfile(src_file, dst)

    return dst

def main_work():
    A_server_path, B_server_path, output_path, start_time, end_time = readConfig()

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

        # reference before assigned
        file_start = each_file_A

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

                # skip file out of (start,end)
                create_time = os.path.getmtime(each_file_A)
                create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time))
                if create_time < start_time:
                    print(file_start, 'skip by time')
                    continue
                if end_time != 'now':
                    if create_time > end_time:
                        print(file_start, 'skip by time')
                        continue

                # same lot and sort but multiple files
                # tmp_A = [each for each in list_A if each.startswith(file_start)]
                tmp_B = [each for each in list_B if each.startswith(file_start)]

                # # position_A = tmp_A.index(each_file_A)
                # source_file_name_A = ''
                # if len(tmp_A) > 1 or len(tmp_B) > 1:
                source_file_name_A = source_file_get(each_file_A)
                if file_type not in ['xml','XML']:
                    source_file_name_A = '  '

                source_file_name_B = ''
                #
                # if len(tmp_B) == 1:
                #     each_file_B = tmp_B[0]
                #     each_file_B = B_server_path.replace('\n', '') + '\\' + each_file_B
                #     if len(tmp_A) > 1:
                #         source_file_name_B = source_file_get(each_file_B)
                #
                # if len(tmp_B) > 1:
                for each_file_B in tmp_B:
                    each_file_B = B_server_path.replace('\n', '') + '\\' + each_file_B
                    source_file_name_B = source_file_get(each_file_B)
                    if source_file_name_A == source_file_name_B:
                        break

                if source_file_name_A != source_file_name_B:
                    error += [file_start]
                    continue

                if file_type != 'xml':
                    each_file_A=copyfile(each_file_A,output_path,file_type)
                    each_file_B=copyfile(each_file_B,output_path,file_type)

                #     shutil.copyfile(each_file_A, each_file_A.replace(file_type, 'xml'))
                #     shutil.copyfile(each_file_B, each_file_B.replace(file_type, 'xml'))

                #     os.rename(each_file_A, each_file_A.replace(file_type, 'xml'))
                #     os.rename(each_file_B, each_file_B.replace(file_type, 'xml'))
                #     each_file_A = each_file_A.replace(file_type, 'xml')
                #     each_file_B = each_file_B.replace(file_type, 'xml')

                # B to A
                out_AB = compare_xmls(each_file_A, each_file_B)
                df_AB = strList(out_AB)

                # A to B
                out_BA = compare_xmls(each_file_B, each_file_A)
                df_BA = strList(out_BA)

                if file_type != 'xml':
                    os.remove(each_file_A)
                    os.remove(each_file_B)
                #
                #
                #
                #     os.rename(each_file_A, each_file_A.replace('xml', file_type))
                #     os.rename(each_file_B, each_file_B.replace('xml', file_type))

                df_each_file = pandas.merge(left=df_BA, right=df_AB, on=['Position', 'Property'],
                                            suffixes=('_A', '_B'), how='right')

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



        except Exception as e:
            print(e, 'Error: %s' % file_start)
            error += [file_start]
            # error += [each_file_A.split('\\')[-1]]

            continue

    now = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))  # Time now
    report_name = output_path + '\\' + 'Result - ' + now + '.csv'

    df_result = df_result.reset_index(drop=True)
    df_result.to_csv(report_name, index=False)
    df_error = pandas.DataFrame(error)

    if error:
        report_name = output_path + '\\' + 'Error - ' + now + '.csv'

        df_error.to_csv(report_name, index=False)

    pass
    pass


try:
    main_work()
except Exception as e:
    print(e, 'Error:main')

print('finish')

from threading import Thread

input_str = 0


def wait_input():
    global input_str

    input_str = input('Input any key and press "Enter" to prevent being closed.')
    print('You need close the window manually.')


thd = Thread(target=wait_input)
thd.daemon = True
thd.start()

seconds = 10
time.sleep(seconds)

if input_str:
    while 1:
        time.sleep(10)
