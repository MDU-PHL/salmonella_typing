'''
A modification of to Pandas DataFrames to implement filtering of SISTTR 
output according to MMS136
'''

import re
import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

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
        self._obj.insert(0, 'ID', new_tab.ID)
    
    def apply_rules(self, rule_list, criteria):
        '''
        Given a list of tuples (rule_name, function), add masking columns
        to table

        rules are named with a 'rule_' prefix by default

        criteria is a dictionary that specify how to generate PASS, REVIEW, FAIL, EDGE
        masking columns by grouping results from different rules.

        rules are defined in the rules.py module
        criteria are defined in the rules.py module

        Adds an additional column: CONSISTENT --- this column should be equal to 1
        if the sample is True for only one criteria. If sum is different from 0, 
        the sample needs to be reviewed
        '''
        for rule,func in rule_list:
            self._obj[rule] = func(self._obj)
        
        for k in criteria:
            self._obj[k] = self._obj.eval(criteria[k])

        self._obj['CONSISTENT'] = self._obj[list(criteria)].sum(axis=1)
    
    def apply_filters(self, filter_list):
        '''
        Similar to rules above, given a list of tuples (filter_name, function), add 
        columns to the table with correct serovar call based on the verification work
        that has been done.

        Filters are named after the rules that define where which rows need a corrected
        serovar call.
        '''
        self._obj['serovar-original'] = self._obj.serovar
        filt_list = []
        for filt,func in filter_list:
            self._obj[filt] = func(self._obj)
            filt_list.append(filt)
        self._obj['FILTERS'] = self._obj[filt_list].apply(lambda x: sum(~x.isnull()), axis=1)
        self._obj['serovar'] = self._obj.apply(lambda x: x.serovar if x[filt_list].isnull().all() else x[filt_list].dropna()[0], axis = 1)
        
    
    def call_status(self):
        '''
        '''
        PASS = self._obj['PASS']
        REVIEW =  self._obj.loc[:,self._obj.columns.str.startswith('REVIEW')].any(axis = 1)
        FAIL = self._obj['FAIL']
        EDGE = self._obj['EDGE']
        CONSISTENT = self._obj['CONSISTENT'] == 1
        FILTERS_OK = self._obj['FILTERS'] <= 1
        conditions = [
            (PASS & CONSISTENT & FILTERS_OK),
            (REVIEW & CONSISTENT & FILTERS_OK),
            (EDGE & CONSISTENT & FILTERS_OK),
            (FAIL & CONSISTENT & FILTERS_OK)
        ]
        choices = ['PASS', 'REVIEW', 'REVIEW, EDGE', 'FAIL']
        self._obj['STATUS'] = np.select(conditions, choices, default='REVIEW, INCONSISTENT')
    
    def output_csv(self, outname="sistr_out.csv", summary=True):
        '''
        The off chance someone wants a CSV output. It will have the following
        data if summary is True:
        SEQID, Subspecies, Serovar, h1, h2, o_antigen, STATUS

        STATUS: PASS, REVIEW, FAIL

        Otherwise, output the complete table (minus ID and ITEMCODE)
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
        Generate a LIMS output

        The LIMS Excel sheet has an:
        - MMS136 sheet recording data that has passed
        - REVIEW sheet recording data that needs review or has failed
        - ALL sheet with the full output analysis
        '''
        summary_header = ['ID', 'ITEMCODE', 'SEQID',
            'cgmlst_subspecies', 'cgmlst_matching_alleles', 'serovar_cgmlst',
            'h1', 'h2', 'o_antigen', 'serogroup', 'serovar_antigen', 'serovar-original',
            'serovar', 'STATUS'
        ]
        writer = pd.ExcelWriter(outname, engine='xlsxwriter')
        pass_df = self._obj.query("STATUS == 'PASS'").loc[:,summary_header]
        pass_df.to_excel(writer, sheet_name='MMS136', index=False)
        review_df = self._obj.query("STATUS != 'PASS'").loc[:,summary_header].sort_values(by="STATUS", ascending=False)
        review_df.to_excel(writer, sheet_name='REVIEW', index=False)
        self._obj.to_excel(writer, sheet_name="ALL", index=False)
        writer.save()

    def _split_id(self, row):
        '''
        Given a row with SEQID column, return ID and ITEMCODE columns
        '''
        m = MDUIDREG.match(row.SEQID)
        if m is None:
            logger.warning("The ID do not appear to follow MDU ID standards. Using SEQID directly.")
            mduid = row.SEQID
            itemcode = ''
        else:
            mduid = m.group('id')
            itemcode = m.group('itemcode') if m.group('itemcode') else ''
        return pd.Series([mduid, itemcode], index=['ID', 'ITEMCODE'])
