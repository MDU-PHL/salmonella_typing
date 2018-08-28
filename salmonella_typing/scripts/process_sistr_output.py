'''
Process the SISTR output
'''

import sys

import pandas as pd
from .SistrDF import SistrDF

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

    >>> data = [
    ... {'cgmlst_ST': 1156141401, 'genome': '2999-99999', 'serotype':'Ent'},
    ... {'cgmlst_ST': 1156141401, 'genome': '2999-00999-1', 'serotype':'Tym'}
    ... ]
    >>> tab = pd.DataFrame(data)
    >>> create_output(tab)
    '''
    tab.mms136.gen_seqid()
    tab.mms136.gen_mduid()
    return tab