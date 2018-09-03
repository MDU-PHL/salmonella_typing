'''
Process the SISTR output
'''

import sys
import inspect

import pandas as pd
from SistrDF import SistrDF
import rules

rule_list = inspect.getmembers(rules, inspect.isfunction)
criteria = rules.criteria

def concat_results(results):
    '''
    Join the output from multiple SISTR runs in to a single Pandas table

    Input:
    -----
    results: list (paths to all relevant results)

    Output:
    ------
    tab: pandas.DataFrame

    >>> import io
    >>> res1 = io.StringIO('A,B\\n1,3\\n')
    >>> res2 = io.StringIO('A,B\\n5,6\\n')
    >>> concat_results([res1, res2])
       A  B
    0  1  3
    1  5  6
    '''

    res = [pd.read_csv(fn, engine='python', sep=None) for fn in results]
    return pd.concat(res, ignore_index=True)

def create_output(tab):
    '''
    Run the methods we created to format the table for MMS136 output

    Input:
    -----
    tab: pandas.DataFrame

    Output:
    -------
    tab: pandas.DataFrame (transformed to MMS136)

    >>> create_output(rules.test_tab)
    '''
    tab.mms136.gen_seqid()
    tab.mms136.gen_mduid()
    tab.mms136.apply_rules(rule_list, criteria)
    tab.mms136.call_status()
    tab.mms136.output_csv()
    tab.mms136.output_csv(outname='sistr_out_complete.csv', summary=False)
    tab.mms136.output_lims()
    return tab