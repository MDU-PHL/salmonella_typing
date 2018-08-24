'''
Run MDU sistr typing
'''

import pathlib

import pandas
import jinja2
from cleo import Command, argument, option

class SistrTyping(Command):
    '''
    Run SISTR typing following MMS136
    '''

    name = 'run_sistr'

    arguments = [
        argument("input_file", description="Table of isolates and path to assembly", required=True)
    ]

    options = [
        option("mdu_qc", "m", "If set, assume input is MDU QC input"),
        option("workdir", "w", "Change working directory",  default=f"{pathlib.Path.cwd().absolute()}", value_required=True)
    ]

    def handle(self):
        self.input = self._read_input(self.argument('input_file'), self.option("mdu_qc"))
        pass
    
    def _read_input(self, filename, is_mdu_qc):
        '''
        Use pandas to read the table, if `is_mdu_qc` filter out samples that 
        are not Salmonella

        Input:
        ------
        filename: str (path to input file)
        is_mdu_qc: bool (whether the input is MDU QC spreadsheet)

        Output:
        -------
        self.tab: pandas.DataFrame
        '''

        tab = pandas.read_csv(filename, sep=None, engine='python', encoding='utf8')
        if is_mdu_qc:
            tab = tab[tab.apply(lambda x: ('Salmonella' in x.SPECIES_EXP and 'Salmonella' in x.SPECIES_OBS), axis=1)]
            
            pass
