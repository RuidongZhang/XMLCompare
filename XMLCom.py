from xmldiff import main, formatting
import os
import time
import sys
import pandas
import re

path = os.path.dirname(os.path.realpath(sys.argv[0]))

import xml.etree.ElementTree as ET


def get_xml_root(file):
    try:
        tree = ET.parse(file)  # 打开xml文档
        # root = ET.fromstring(country_string) #从字符串传递xml
        root = tree.getroot()  # 获得root节点
    except Exception as e:
        print("Error:cannot parse file:%s" % file + str(e))
        root = ''
        # sys.exit(1)
    return root


def readConfig():
    fopen = open(path + '\\config.txt', 'r')
    lines = fopen.readlines()

    for row in lines:
        if row.startswith('e142_format'):
            e142_format = row.split('|')[1]
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
                end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time + 24 * 3600))

    fopen.close()

    return A_server_path, B_server_path, output_path, start_time, end_time, e142_format


def get_data(file):
    f = open(file, 'r', encoding='utf-8')
    data = f.readlines()
    content = ''
    i = 0
    for each in data:
        i += 1
        # if '<RuleEvaluation' in each:
        #     each = each.replace('/>','>%s</RuleEvaluation>'%i)
        # elif '<Software' in each:
        #     each = each.replace('/>','>%s</Software>'%i)
        # elif '<RequestReference' in each:
        #     each = each.replace('/>','>%s</RequestReference>'%i)
        # elif '<Run ' in each:
        #     each = each.replace('/>','>%s</Run>'%i)
        if '<Runs />' in each:
            each = each.replace('<Runs />', '<Runs>') + each.replace('<Runs />', '</Runs>')
        elif '<RulesStatus />' in each:

            each = each.replace('<RulesStatus />', '<RulesStatus>') + each.replace('<RulesStatus />', '</RulesStatus>')

        content += each

    return content


def not_empty(s):
    return s and s.strip()


def get_lot_e142(file):
    f = open(file, 'r', encoding='utf-8')
    data = f.readlines()
    # observed = data_str(observed)
    # observed = data.split('\n')
    observed = list(filter(not_empty, data))

    for row in observed:
        if '<LotId>' in row:
            lot = row.split('<LotId>')[-1]
            lot = lot.split('<')[0]
            return lot


def data_str(observed):
    observed = observed.split('\n')
    observed = list(filter(not_empty, observed))

    data = []
    for row in observed:
        if not row:
            continue
        while ' ' in row:
            row = row.replace(' ', '')
        while '\t' in row:
            row = row.replace('\t', '')
        data.append(row)

    return data


def diff_eg(observed, expected):
    observed = data_str(observed)
    expected = data_str(expected)

    length = max([len(observed), len(expected)])

    while len(observed) < length:
        observed += ['']

    while len(expected) < length:
        expected += ['']

    i = 0
    diff = []
    while i < len(observed):
        if observed[i] == expected[i]:
            pass
        else:
            diff.append(['Update', 'Row - %d' % (i + 1), '', expected[i], ''])

        i += 1

    if not diff:
        diff = [[''] * 5]

    return pandas.DataFrame(diff, columns=['Type', 'Position', 'Property', 'Value', 'Backup'])


def compare_xmls(observed, expected, file_type='xml'):
    formatter = formatting.XMLFormatter()
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
    if file_type == 'xml':
        uniqueattrs = [('RuleEvaluation', 'Name')]
    else:
        uniqueattrs = [('RuleEvaluation', 'Name')]
    observed = get_data(observed)
    expected = get_data(expected)

    if (observed == '') and (expected == ''):
        df = pandas.DataFrame([{'Type': '', 'Position': '', 'Property': '', 'Value': '', 'Backup': '', }])
        return df
    else:
        i = 1
        pass

    if file_type == 'eg':
        # if observed == expected:
        if False:
            return ''
        return diff_eg(observed, expected)

    diff = main.diff_texts(observed, expected,
                           diff_options={'fast_match': True, 'F': 0.5, 'ratio_mode': 'fast',
                                         'uniqueattrs': [('RuleEvaluation', 'Index')]},
                           formatter=formatting.DiffFormatter())

    # diff = main.diff_files(observed, expected,
    #
    #                        formatter=formatting.XMLFormatter())

    return diff


def readFolder(path):
    list = os.listdir(path.replace('\n', ''))
    return list


# def getFile(folder_path):
#
#     for

def strList(result_str, format=None):
    if not result_str:
        return strDf([], False)

    list_tmp = result_str.split('\n')
    result_list = []
    flag_5col = False

    for each in list_tmp:
        tmp = each[1:][0: -1].split(',', 4)

        # zip 4 elements
        if format == '3':
            if len(tmp) == 3:
                tmp = tmp[0:2] + [''] + tmp[2:]
        elif len(tmp) > 4:
            tmp = tmp[0:5]
            flag_5col = True
        elif len(tmp) < 4:
            tmp += ['' for i in range(4 - len(tmp))]

        result_list.append(tmp)

    return strDf(result_list, flag_5col)


def reformat(row):
    proper = row['Property']
    value = row['Value']

    if type(proper) != str:
        return row
    if type(value) != str:
        return row

    if row['Type'] == 'insert':
        value = value.replace(' ', '')
        if value.isdecimal():
            value = int(value) + 1
            row['Value'] = value
            row['Position'] = row['Position'] + '/*[%d]' % value

    return row


# list to Dataframe
def strDf(lis, flag_5col=False):
    columns = ['Type', 'Position', 'Property', 'Value']
    if flag_5col:
        columns += ['Backup']
        df_each_file = pandas.DataFrame(lis, columns=columns)
    else:
        df_each_file = pandas.DataFrame(lis, columns=columns)
        df_each_file['Backup'] = ''

    df_each_file = df_each_file.apply(reformat, axis=1)

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
    elif '.eg' in file_path:
        file_type = 'eg'
    else:
        file_type = file_path.split('.')[-1]

    return file_type


def copyfile(src_file, dst_dir, file_type, suffix=None):
    import shutil
    if suffix:
        dst = dst_dir.rstrip('\n') + '\\' + src_file.split('\\')[-1].replace(file_type, 'xml').replace('.',
                                                                                                       '-%s.' % suffix)
    else:
        dst = dst_dir.rstrip('\n') + '\\' + src_file.split('\\')[-1].replace(file_type, 'xml')
    shutil.copyfile(src_file, dst)

    return dst


def deleted_tag(row, each_file_A):
    try:
        root = get_xml_root(each_file_A)
        positions = re.findall("\d+", row['Position'])

        for i in range(len(positions)):
            positions[i] = int(positions[i]) - 1

        if len(positions) == 3:
            tag = root[positions[0]][positions[1]][positions[2]].tag
            attrib = str(root[positions[0]][positions[1]][positions[2]].attrib)

        elif len(positions) == 2:
            tag = root[positions[0]][positions[1]].tag
            attrib = str(root[positions[0]][positions[1]].attrib)

        elif len(positions) == 1:
            tag = root[positions[0]].tag
            attrib = str(root[positions[0]].attrib)

        return tag + attrib
    except:
        return row['Value_A']


def main_work():
    print('2022-7-28 Update Error description')
    A_server_path, B_server_path, output_path, start_time, end_time, e142_format = readConfig()

    list_A = readFolder(A_server_path)
    list_B = readFolder(B_server_path)
    list_A.sort()
    list_B.sort()
    each_file_A = ''
    each_file_B = ''

    df_result = pandas.DataFrame()
    error = []
    i = 0
    for each_file_A in list_A:
        i += 1
        lot_e142 = ''
        print('Processing file %d:' % i + each_file_A)
        each_file_B = ''
        columns = ['Type_B', 'Position', 'Property', 'Value_A', 'Value_B', 'Backup_A', 'Backup_B']
        # if 'YZMEA2QMH700_FCRL_Hold_20211228125329.xml' in each_file_A:
        #     kk=1
        # reference before assigned
        file_start = each_file_A

        try:
            file_type = get_type(each_file_A)

            if file_type.lower() == 'xml':
                e142_format = 4


            if file_type in each_file_A:
                tmp = each_file_A.split('_')
                lot = tmp[0]
                sort = tmp[1]

                if e142_format in ['4', 4]:

                    if len(tmp) == 5:
                        sort += '_' + tmp[2]
                    file_start = lot + '_' + sort
                    if file_type in ['e142', 'E142']:
                        file_start += '_' + tmp[3]

                elif e142_format in ['3', 3]:

                    if len(tmp) == 4:
                        sort += '_' + tmp[2] + '_' + tmp[3]
                    file_start = lot + '_' + sort
                    # if file_type in ['e142', 'E142']:
                    #     file_start += '_' + tmp[3]

                each_file_A = A_server_path.replace('\n', '') + '\\' + each_file_A

                if file_type in ['e142']:
                    try:
                        lot_e142 = get_lot_e142(each_file_A)
                    except Exception as e1:
                        pass

                # skip file out of (start,end)
                create_time = os.path.getmtime(each_file_A)
                create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time))
                if create_time < start_time:
                    print(each_file_A, 'skip by time')
                    continue
                if end_time != 'now':
                    if create_time > end_time:
                        print(each_file_A, 'skip by time')
                        continue

                # same lot and sort but multiple files
                # tmp_A = [each for each in list_A if each.startswith(file_start)]
                tmp_B = [each for each in list_B if each.startswith(file_start)]

                # # position_A = tmp_A.index(each_file_A)
                # source_file_name_A = ''
                # if len(tmp_A) > 1 or len(tmp_B) > 1:
                if file_type in ['xml', 'XML']:
                    source_file_name_A = source_file_get(each_file_A)
                else:
                    source_file_name_A = ''
                # if file_type not in ['xml','XML']:
                #     source_file_name_A = '  '

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
                    if file_type in ['xml', 'XML']:
                        source_file_name_B = source_file_get(each_file_B)

                    if source_file_name_A == source_file_name_B:
                        break

                if source_file_name_A != source_file_name_B:
                    if each_file_A:
                        dic = {'File': each_file_A, 'lot': lot_e142}
                        error += [dic]
                        continue

                if each_file_B == '':
                    if each_file_A:
                        dic = {'File': each_file_A, 'lot': lot_e142}
                        error += [dic]
                        continue

                if file_type != 'xml':
                    if each_file_A.split('\\')[-1] == each_file_B.split('\\')[-1]:
                        suffix_A = 'A'
                        suffix_B = 'B'
                    else:
                        suffix_B = suffix_A = None

                    each_file_A = copyfile(each_file_A, output_path, file_type, suffix=suffix_A)
                    each_file_B = copyfile(each_file_B, output_path, file_type, suffix=suffix_B)

                #     shutil.copyfile(each_file_A, each_file_A.replace(file_type, 'xml'))
                #     shutil.copyfile(each_file_B, each_file_B.replace(file_type, 'xml'))

                #     os.rename(each_file_A, each_file_A.replace(file_type, 'xml'))
                #     os.rename(each_file_B, each_file_B.replace(file_type, 'xml'))
                #     each_file_A = each_file_A.replace(file_type, 'xml')
                #     each_file_B = each_file_B.replace(file_type, 'xml')

                if file_type == 'eg':
                    df_AB = compare_xmls(each_file_A, each_file_B, file_type)
                    df_BA = compare_xmls(each_file_B, each_file_A, file_type)

                else:
                    # B to A
                    out_AB = compare_xmls(each_file_A, each_file_B, file_type)
                    df_AB = strList(out_AB, e142_format)

                    # A to B
                    out_BA = compare_xmls(each_file_B, each_file_A, file_type)
                    df_BA = strList(out_BA, e142_format)

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
                # columns = ['Type_B', 'Position', 'Property', 'Value_A', 'Value_B', 'Backup_A', 'Backup_B']

                # fill del with insert
                if len(df_each_file):

                    A_del = df_BA[df_BA['Type'].isin(['insert', 'insert-attribute'])].copy()
                    if len(A_del):
                        A_del['Type'] = A_del['Type'].str.replace('insert', 'delete')
                        A_del.rename(columns={'Value': 'Value_A', 'Type': 'Type_B'}, inplace=True)
                        df_each_file = df_each_file[~df_each_file['Type_B'].isin(['delete', 'delete-attribute'])]
                        df_each_file = pandas.concat([df_each_file, A_del])

                df_each_file = df_each_file[columns]

                df_each_file.rename(columns={'Type_B': 'Type'}, inplace=True)
                df_each_file.insert(0, 'lot_sort', file_start)
                if source_file_name_A:
                    df_each_file['Backup_A'] = source_file_name_A

                df_each_file['Value_A'] = df_each_file.apply(
                    lambda row: deleted_tag(row, each_file_A) if ('delete' == row['Type']) else row['Value_A'], axis=1)

                if file_type in ['e142']:
                    df_each_file.insert(1, 'LotId', lot_e142)

                if file_type != 'xml':
                    os.remove(each_file_A)
                    os.remove(each_file_B)

                df_result = pandas.concat([df_result, df_each_file])



        except Exception as e:
            print(e, 'Error: %s' % each_file_A)
            if each_file_A:
                dic={'File':each_file_A,'lot':lot_e142}
                error += [dic]

            continue

    now = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))  # Time now
    report_name = output_path + '\\' + 'Result - ' + now + '.csv'

    # df_result['Value_A'] = df_result.apply(lambda row: deleted_tag(row) if ('delete' == row['Type']) else row['Value_A'],axis=1)

    try:
        df_result['Property'] = df_result['Property'].apply(
            lambda x: x.split('}', 1)[-1] if (('{' in x) and ('}' in x) and (x[-1] != '}')) else x)
    except Exception as e:
        print(e, 'Error:main Property')
    try:
        df_result['Value_A'] = df_result['Value_A'].apply(
            lambda x: x.split('}', 1)[-1] if (type(x) == str and '{http' in x and '}' in x) else x)
    except Exception as e:
        print(e, 'Error:main Value A')

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
