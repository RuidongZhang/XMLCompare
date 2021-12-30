from xmldiff import main, formatting
import os
import time
import sys
import pandas
import xml

def compare_xmls(observed, expected,file_type='xml'):
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
    # if file_type == 'xml':
    #     uniqueattrs = [('RuleEvaluation', 'Name')]
    # else:
    #     uniqueattrs = [('RuleEvaluation', 'Name')]
    # observed=observed.replace('xml','html')
    # expected=expected.replace('xml','html')
    def get_data(file):
        f = open(file,'r',encoding='utf-8')
        data = f.readlines()
        content = ''
        i=0
        for each in data:
            i+=1
            # if '<RuleEvaluation' in each:
            #     each = each.replace('/>','>%s</RuleEvaluation>'%i)
            # elif '<Software' in each:
            #     each = each.replace('/>','>%s</Software>'%i)
            # elif '<RequestReference' in each:
            #     each = each.replace('/>','>%s</RequestReference>'%i)
            # elif '<Run ' in each:
            #     each = each.replace('/>','>%s</Run>'%i)


            content+=each


        return content

    observed = get_data(observed)
    expected = get_data(expected)


    diff = main.diff_texts(observed, expected,
                           diff_options={'fast_match':True,'F': 0.5, 'ratio_mode': 'faster',},
                           formatter=formatting.DiffFormatter())

    # diff = main.diff_files(observed, expected,
    #
    #                        formatter=formatting.XMLFormatter())


    return diff


if __name__ == '__main__':

    observed='E:\\XMLCompare\\FT\\A\\DV57833_CP1_PHN_Release_20210220112111.xml'
    expected='E:\\XMLCompare\\FT\\B\\DV57833_CP1_PHN_Release_20210220112021.xml'
    compare_xmls(observed, expected, file_type='xml')

