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

def filter_edge_case_sofia(tab):
    '''

    >>> res = filter_edge_case_sofia(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.filter_edge_case_sofia)
    '''
    true_serovar = 'Sofia'
    new_serovar = tab.apply(lambda x: true_serovar if x.rule_edge_case_sofia else np.nan, axis=1)
    new_serovar.name = "filter_edge_case_sofia"
    return new_serovar
