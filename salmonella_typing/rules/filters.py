'''
Individual filters to apply to the data set to change the serovar output from SISTR
when we know it is incorrect

A filter should be tied to a specific rule that identifies the rows that need to 
be changed. In general, the filter and rule will have the same name with the 
exception of the prefix, which is either "rule_" or "filter_"

Each filter is a function. Filters will be named with the prefix "filter_" and
have, as mentioned above, will have the same name as the rule it applies to.

The function will accept as input a pandas.DataFrame, and return a Series with
the correct serovar call in the appropriate rows, and Nan otherwise.
'''

import sys

import numpy as np
import pandas as pd

if 'pytest' in sys.modules:
    ### SOME TEST DATA FOR DOCSTRING TESTS ###
    ### To test run:
    ###     PYTHONPATH=. pytest --doctest-modules filters.py

    test_data = "rule_test/sistr_test_rules.csv"
    test_tab = pd.read_csv(test_data)

### FILTERS ###

def filter_edge_case_sophia(tab):
    '''

    >>> res = filter_edge_case_sophia(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.filter_edge_case_sophia)
    '''
    true_serovar = 'Sophia'
    new_serovar = tab.apply(lambda x: true_serovar if x.rule_edge_case_sophia else np.nan, axis=1)
    new_serovar.name = "filter_edge_case_sophia"
    return new_serovar

def filter_edge_case_tm_abony(tab):

    true_serovar = 'Typhimurium|Lagos'
    new_serovar = tab.apply(lambda x: true_serovar if x.rule_edge_case_tm_abony else np.nan, axis=1)
    new_serovar.name = "filter_edge_case_tm_abony"
    return new_serovar


def filter_edge_case_sbg_wshmptn(tab):

    true_serovar = 'Senftenberg'
    new_serovar = tab.apply(lambda x: true_serovar if x.rule_edge_case_sbg_wshmptn else np.nan, axis=1)
    new_serovar.name = "filter_edge_case_sbg_wshmptn"
    return new_serovar

def filter_edge_case_paratyphiB(tab):

    true_serovar = 'Paratyphi B'
    new_serovar = tab.apply(lambda x: true_serovar if x.rule_edge_case_paratyphiB else np.nan, axis=1)
    new_serovar.name = "filter_edge_case_paratyphiB"
    return new_serovar


def filter_edge_case_paratyphiBvJava(tab):

    true_serovar = 'Paratyphi B var. Java'
    new_serovar = tab.apply(lambda x: true_serovar if x.rule_edge_case_paratyphiBvJava else np.nan, axis=1)
    new_serovar.name = "filter_edge_case_paratyphiBvJava"
    return new_serovar

