'''
A modification of to Pandas DataFrames to implement filtering of SISTTR 
output according to MMS136
'''

import re

import pandas as pd

MDUIDREG = re.compile(r'(?P<id>[0-9]{4}-[0-9]{5})-?(?P<itemcode>.{1,2})?')

@pd.api.extensions.register_dataframe_accessor("mms136")
class SistrDF(object):
    '''
    A dataframe accessor for MMS136 rules
    '''

    def __init__(self, pandas_obj):
        '''
        Pass the pandas object to the _obj attribute of the instance
        '''
        self._obj = pandas_obj

    def gen_seqid(self):
        '''
        Get the `genome` column, make it the first column, and create a item_code column
        '''
        self._obj.insert(0, 'SEQID', self._obj.genome)
        del self._obj['genome']

    def gen_mduid(self):
        '''
        Generate two columns: MDU ID and item code (if exists) using the seqid column
        '''
        new_tab = self._obj.apply(self._split_id, axis=1, result_type='expand')
        self._obj.insert(0, 'ITEMCODE', new_tab.ITEMCODE)
        self._obj.insert(0, 'MDUID', new_tab.MDUID)
    
    def apply_rules(self, rule_list, criteria):
        '''
        Given a list of tuples (rule_name, function), add masking columns
        to table

        rules are named with a 'rule_' prefix by default, this is removed
        when creating the colum name by subsetting the rule name

        criteria is a dictionary that specify how to generate PASS, REVIEW, FAIL, EDGE
        masking columns by grouping results from different rules.

        rules are defined in the rules.py module
        criteria are defined in the rules.py module
        '''
        for r,f in rule_list:
            self._obj[r[5:]] = f(self._obj)
        
        for k in criteria:
            self._obj[k] = self._obj.eval(criteria[k])

    def _split_id(self, row):
        '''
        Given a row with SEQID column, return MDUID and ITEMCODE columns
        '''
        m = MDUIDREG.match(row.SEQID)
        mduid = m.group('id')
        itemcode = m.group('itemcode') if m.group('itemcode') else ''
        return pd.Series([mduid, itemcode], index=['MDUID', 'ITEMCODE'])
