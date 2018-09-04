'''
Process the SISTR output
'''

import inspect
import pathlib

import pandas as pd
from cleo import Command, argument, option

from scripts.SistrDF import SistrDF
import scripts.rules

rule_list = inspect.getmembers(scripts.rules, inspect.isfunction)
criteria = scripts.rules.criteria

class ParseSistrOuput(Command):
    '''
    Parse the output from SISTR implementing the MMS136 rules. By default do not output the LIMS Excel.
    '''

    name = "parse"

    arguments = [
        argument("input_files", description="One or more SISTR output CSV results", required=True, is_list=True)
    ]

    options = [
        option("--lims", "-l", description="Whether to output a LIMs Excel Sheet"),
        option("--prefix", "-p", description="Prefix of output file", value_required=True, default="sistr_out"),
        option("--full", "-f", description="When outputting CSV, output all fields? If not, just summary.")
    ]

    def handle(self):
        '''
        Hangle the arguments
        '''
        self.input_files = [pathlib.Path(f) for f in self.argument("input_files")]
        self.concat_results()
        self.create_output()



    def concat_results(self):
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

        res = [pd.read_csv(fn, engine='python', sep=None) for fn in self.input_files]
        self.tab = pd.concat(res, ignore_index=True)

    def create_output(self):
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
        self.tab.mms136.gen_seqid()
        self.tab.mms136.gen_mduid()
        self.tab.mms136.apply_rules(rule_list, criteria)
        self.tab.mms136.call_status()
        if self.option("lims"):
            outfile = pathlib.Path(pathlib.Path.cwd(), self.option("prefix") + '.xlsx')
            self.tab.mms136.output_lims(outname=outfile)
        else:
            outfile = pathlib.Path(pathlib.Path.cwd(), self.option("prefix") + '.csv')
            self.tab.mms136.output_csv(outname=outfile, summary=(not self.option("full")))