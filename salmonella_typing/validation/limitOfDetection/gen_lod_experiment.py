#!/usr/bin/env python3
'''
A script that will prepare a limit of detection input file based on a table 
of sample IDs, paths to read files, and a set of depths and replicates
'''

import random
import itertools
import logging
import pathlib
import inspect
import itertools

import pandas as pd

from cleo import Command, argument, option
from cleo.validators import Integer
from cleo.exceptions.exception import UsageException

logger = logging.getLogger(__name__)

class LODCommand(Command):

    name = 'lod_generator'

    description = "Generate a LOD experiment"

    arguments = [
        argument("input_file", description="Table of isolates and path to reads", required=True)
    ]

    options = [
        option("workdir", "w", "Change working directory",  default=f"{pathlib.Path.cwd().absolute()}", value_required=True),
        option("depth", "d", "Comma-separated list of values (e.g., 10,20,30).", default=None, value_required=True),
        option("reps", "e", "Number of replicates of each depth for each sample", default=2, value_required=True),
        option("seed", "s", "Seed for random number generator when generating seeds for subsampling reads", default=42, value_required=True, validator=Integer()),
        option("min_seed", "i", "Minimum seed value to randomly subsample reads", default=10, value_required=True, validator=Integer()),
        option("max_seed", "x", "Maximum seed value to randomly subsample reads", default=10**8, value_required=True, validator=Integer()),
        option("resource_path", "r", "Path to Snakefile and config.yaml templates to use", default=f"{pathlib.Path(__file__).parent.parent / 'validation'/ 'limitOfDetection' / 'templates'}", value_required=True),
        option("control_path", "c", "Path to FASTA for positive controls to use", default=f"{pathlib.Path(__file__).parent.parent / 'data'}", value_required=True),
        option("threads", "t", "How many threads to give Snakemake", default=2, value_required=True, validator=Integer())
    ]

    def handle(self):
        self.info("Starting up new LOD experiment...")
        self._parse_args()
        self._parse_opts()
        self._test_reqs()
        self._parse_depth()
        self.fn = pathlib.Path(self.infile)
        self.info("Loading input table...")
        self._read_table()
        self.reps = list(range(1,self.reps+1))
        self.info("Generating LOD table...")
        self._generate_lod_table()
        # self.outname = outname
        # logger.info("Saving table...")
        # self._save_lod_table()
    
    def _parse_args(self):
        '''
        Parse the arguments and put add them to objects attributes
        '''
        self.info("Loading arguments...")
        args = self.argument()
        self.infile = pathlib.Path(args['input_file'])
    
    def _parse_opts(self):
        '''
        Parse the options
        '''
        self.info("Loading options...")
        opts = self.option()
        for opt in ['workdir', 
                    'depth', 
                    'reps', 
                    'seed', 
                    'min_seed', 
                    'max_seed',
                    'resource_path',
                    'threads']:
            setattr(self, opt, opts[opt])
    
    def _req_depth_cannot_be_none(self):
        '''
        Test if depth option is None.
        '''
        return self.depth is not None

    def _test_reqs(self):
        '''
        Test requirements
        '''
        requirements = {k:m() for k,m in inspect.getmembers(self, predicate=inspect.ismethod) if k.startswith("_req")}
        failed_requirements = list(itertools.filterfalse(requirements.get, requirements))
        if len(failed_requirements) > 0:
            raise UsageException(f"Bad options {' '.join(failed_requirements)}")
        self.info("All options look good.")
    
    def _parse_depth(self):
        self.depth = self.depth.split(",")

    def _read_table(self):
        '''
        Read a filename and return a Pandas DataFrame

        Input:
        -----
        filename: str (path to a filename)

        Output:
        self.tab: pandas.DataFrame
        '''
        fn = self.fn
        if not fn.exists():
            raise FileNotFoundError(f"Could not find {filename}")
        if not fn.is_file():
            raise OSError(f"{filename} is not a file")
        if fn.suffix in ('.csv', '.txt', '.tab'):
            tab = pd.read_csv(fn, sep=None, engine="python", encoding='utf8')
        elif fn.suffix in ('.xls', '.xlsx'):
            tab = pd.read_excel(fn)
        else:
            raise ValueError(f"No rule availalbe to load file with suffix: {fn.suffix}")
        self.tab = tab
            

    def _generate_lod_table(self):
        '''
        A function to return a table with all the experiments required
        for limit of detection

        Input:
        -----
        tab: pd.DataFrame (a DataFrame with at least three columns: ID, R1, and R2)
        depth: list (a list of depth values to subsample the data)
        reps: int (how many replicates to perform for each depth/sample combination)
        seed: int (a number to set the random seed to generate seeds for subsampling reads)
        MIN: int (the minimum seed value for subsampling reads)
        MAX: int (the maximum seed value for subsampling reads)

        Output:
        ------
        self.tab_lod: pd.DataFrame (table with all the experiments need to run)

        >>> depth = [10,80]
        >>> reps = 2
        >>> seed = 42
        >>> filename = 'dummy.txt'
        >>> lod = LOD(filename, depth, reps, seed)
        >>> data = [{'ID': 'samp1', 'R1': '/path/to/samp1_R1.fq.gz', 'R2': '/path/to/samp1_R2.fq.gz'}]
        >>> data.append({'ID': 'samp2', 'R1': '/path/to/samp2_R1.fq.gz', 'R2': '/path/to/samp2_R2.fq.gz'})
        >>> tab = pd.DataFrame(data)
        >>> tab
              ID                       R1                       R2
        0  samp1  /path/to/samp1_R1.fq.gz  /path/to/samp1_R2.fq.gz
        1  samp2  /path/to/samp2_R1.fq.gz  /path/to/samp2_R2.fq.gz
        >>> lod.tab = tab
        >>> lod.generate_lod_table()
        >>> lod.tab_lod
           ix  depth  rep      seed     ID                       R1                       R2
        0   0     10    1  85822422  samp1  /path/to/samp1_R1.fq.gz  /path/to/samp1_R2.fq.gz
        1   0     10    2  14942613  samp1  /path/to/samp1_R1.fq.gz  /path/to/samp1_R2.fq.gz
        2   0     80    1   3356896  samp1  /path/to/samp1_R1.fq.gz  /path/to/samp1_R2.fq.gz
        3   0     80    2  99529233  samp1  /path/to/samp1_R1.fq.gz  /path/to/samp1_R2.fq.gz
        4   1     10    1  36913820  samp2  /path/to/samp2_R1.fq.gz  /path/to/samp2_R2.fq.gz
        5   1     10    2  32868838  samp2  /path/to/samp2_R1.fq.gz  /path/to/samp2_R2.fq.gz
        6   1     80    1  29958848  samp2  /path/to/samp2_R1.fq.gz  /path/to/samp2_R2.fq.gz
        7   1     80    2  18728473  samp2  /path/to/samp2_R1.fq.gz  /path/to/samp2_R2.fq.gz
        '''
        random.seed(self.seed)
        comb_list = [list(self.tab.index), self.depth, self.reps]
        comb = list(itertools.product(*comb_list))
        tab_lod = pd.DataFrame(comb, columns=['ix', 'depth', 'rep'])
        tab_lod['seed'] = tab_lod.apply(lambda ix: random.randint(self.min_seed, self.max_seed), axis=1)
        tab_lod = tab_lod.join(self.tab, on='ix')
        self.tab_lod = tab_lod
    
    def _save_lod_table(self):
        """
        Save the LOD table to self.outname

        Input:
        ------
        self.outname: str (filename to save content to)

        Output:
        ------
        outname: file (csv format)
        """
        self.tab_lod.to_csv(self.outname, index=False, sep='\t')

# def main(filename, outname, depth, reps, seed, min_seed=10, max_seed=10**8):
#     '''
#     Make a "limit of detection" experiment

#     Input:
#     -----
#     filename: str (path to a file with at least three named columns: ID, R1, R2)
#     outname: str (name of output filename)
#     depth: list (a list of depth values: [10,20,30])
#     reps: int (repeat each depth/sample combination how many times?)
#     seed: int (set the seed value to generate random seeds for subsampling reads)
#     min-seed: int (minimum value for a seed to subsample reads, default: 10)
#     max-seed: int (maximum value for a seed to subsample reads, default:10^8)

#     Output:
#     ------
#     outname: file (a file with a new experiment)
#     '''
#     lod = LOD()
#     lod.run(filename, outname, depth, reps, seed, min_seed, max_seed)