'''
A modification of to Pandas DataFrames to implement filtering of SISTTR 
output according to MMS136
'''

import re

import pandas as pd
import numpy as np

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

        Adds an additional column: CONSISTENT --- this column should be equal to 1
        if the sample is True for only one criteria. If sum is different from 0, 
        the sample needs to be reviewed
        '''
        for r,f in rule_list:
            self._obj[r[5:]] = f(self._obj)
        
        for k in criteria:
            self._obj[k] = self._obj.eval(criteria[k])

        self._obj['CONSISTENT'] = self._obj[list(criteria)].sum(axis=1)
    
    def call_status(self):
        '''
        '''
        PASS = self._obj['PASS']
        REVIEW =  self._obj.loc[:,self._obj.columns.str.startswith('REVIEW')].any(axis = 1)
        FAIL = self._obj['FAIL']
        EDGE = self._obj['EDGE']
        CONSISTENT = self._obj['CONSISTENT'] == 1
        conditions = [
            (PASS & CONSISTENT),
            (REVIEW & CONSISTENT),
            (EDGE & CONSISTENT),
            (FAIL & CONSISTENT)
        ]
        choices = ['PASS', 'REVIEW', 'REVIEW, EDGE', 'FAIL']
        self._obj['STATUS'] = np.select(conditions, choices, default='REVIEW, INCONSISTENT')
    
    def output_csv(self, outname="sistr_out.csv", summary=True):
        '''
        The off chance someone wants a CSV output. It will have the following
        data if summary is True:
        SEQID, Subspecies, Serovar, h1, h2, o_antigen, STATUS

        STATUS: PASS, REVIEW, FAIL

        Otherwise, output the complete table (minus MDUID and ITEMCODE)
        '''
        if summary:
            output_cols = ['SEQID', 'cgmlst_subspecies','serovar', 'h1', 'h2', 'o_antigen', 'STATUS']
        else:
            output_cols = self._obj.columns
        
        outtab = self._obj.loc[:,output_cols]
        outtab.rename(columns = {'cgmlst_subspecies': 'subspecies'}, inplace=True)
        outtab.to_csv(outname, index=False)
    
    def output_lims(self, outname="sistr_lims.xlsx"):
        '''
        '''
        pass

    def _split_id(self, row):
        '''
        Given a row with SEQID column, return MDUID and ITEMCODE columns
        '''
        m = MDUIDREG.match(row.SEQID)
        mduid = m.group('id')
        itemcode = m.group('itemcode') if m.group('itemcode') else ''
        return pd.Series([mduid, itemcode], index=['MDUID', 'ITEMCODE'])
