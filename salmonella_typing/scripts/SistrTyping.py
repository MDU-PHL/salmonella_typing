'''
Run MDU sistr typing
'''

import pathlib
import os

import pandas
import jinja2
import sh
from cleo import Command, argument, option

class RunSistrWorkflow(Command):
    '''
    Run SISTR typing following MMS136
    '''

    name = 'run'

    arguments = [
        argument("input_file", description="Table of isolates and path to assembly")
    ]

    options = [
        option("mdu_qc", "m", "If set, assume input is MDU QC input"),
        option("workdir", "w", "Change working directory",  default=f"{pathlib.Path.cwd().absolute()}", value_required=True),
        option("fields", "f", "If input file has no header, use this comma-separated list of values (e.g., -f 'ID,ASM').", default=None, value_required=True),
        option("resource_path", "r", "Path to Snakefile and config.yaml templates to use", default=f"{pathlib.Path(__file__).parent.parent / 'templates'}", value_required=True),
        option("control_path", "c", "Path to FASTA for positive controls to use", default=f"{pathlib.Path(__file__).parent.parent / 'data'}", value_required=True),
        option("threads", "t", "How many threads to give Snakemake", default=2, value_required=True)
    ]

    def handle(self):
        # print('Starting')
        input_file = pathlib.Path(self.argument("input_file"))
        self._exists(input_file)
        workdir = pathlib.Path(self.option("workdir"))
        self._exists(workdir)
        resource_path = pathlib.Path(self.option('resource_path'))
        self._exists(resource_path)
        control_path = pathlib.Path(self.option('control_path'))
        self._exists(control_path)
        self._read_input(input_file, self.option("mdu_qc"), self.option("fields"))
        self._write_input(workdir)
        self._write_workflow(resource_path, control_path, workdir)
        self._run_workflow(workdir, self.option("threads"))

    def _exists(self, path):
        if not path.exists():
            self.error(f"Could not find {path.name}")
            raise FileNotFoundError(f"{path.name}")
        else:
            self.info(f"Found {path.name}.")
    
    def _read_input(self, filename, is_mdu_qc, fields):
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
        # A bit of a complicated if/else clause to allow for the default behaviour
        # of Pandas when header is in the file
        if fields is None:
            # The case when we should use the default
            names = None
            header = 0
        else:
            # Othwerwise, when a header is not specified and the user provides
            # it with the command line
            names = header.split(',')
            header = None
        tab = pandas.read_csv(filename, sep=None, engine='python', encoding='utf8', header=header, names=names)
        # print(tab)
        if is_mdu_qc:
            tab = tab[tab.apply(lambda x: ('Salmonella' in x.SPECIES_EXP and 'Salmonella' in x.SPECIES_OBS), axis=1)]
            tab['ASM'] = tab.apply(lambda x: pathlib.Path(f"{x.SEQID}/contigs.fa"), axis=1)
        else:
            if 'ASM' not in tab.columns:
                self.error(f"{filename} does not include a field called ASM with the path to the assembly.")
                table = self.table()
                table.headers('ID', 'ASM')
                table.set_rows([
                    ['2099-99999', '/path/to/asm/contig.fa'],
                    ['2099-99998-1', '/path/to/asm/contig.fa']
                ])
                self.error("Here is an example minimal file:")
                table.render()
                raise AttributeError(f"Did not find ASM field in {filename}")
            else:
                self.info("Found ASM field... Proceeding with analysis.")
                if 'SEQID' not in tab.columns:
                    self.comment(f"Assuming {tab.columns[0]} is SEQID")
                    tab = tab.rename(columns={tab.columns[0]:'SEQID'})
        self.tab = tab

    def _write_input(self, workdir):
        '''
        Write the input file for use with Snakefile to generate the sistr results

        Input:
        -----
        workdir: a pathlib.Path object (path to the current working directory)
        '''
        # print(tab)
        tab = self.tab[['SEQID', 'ASM']]
        input_file = pathlib.Path(workdir, 'input_sistr.txt')
        tab.to_csv(input_file, index=False)
        self.info(f"Succesfully wrote sistr_input.txt to {input_file.parent}")
    

    def _write_workflow(self, resources, controls, workdir):
        '''
        Load Snakefile file and config.yaml templates
        '''
        self.info("Loading Snakefile and config.yaml...")

        stm_control = controls / "SentericaLT2.fasta"

        cfg_tmpl = jinja2.Template(pathlib.Path(resources, 'config.yaml').read_text())
        cfg = workdir / 'config_sistr.yaml'
        cfg.write_text(cfg_tmpl.render(input_file='input_sistr.txt', stm_control=f"{stm_control.absolute()}"))
        
        skf_tmpl = resources / 'Snakefile'
        skf = workdir / 'Snakefile.sistr'
        skf.write_text(skf_tmpl.read_text())

        self.info(f"Successfully wrote workflow to {cfg.parent}")

    def _run_workflow(self, workdir, threads):
        '''
        Given all the elements have been put in place, run the workflow
        '''
        os.chdir(workdir)
        snakemake = sh.Command('snakemake')
        runwf = snakemake("-s", "Snakefile.sistr", "-j", f"{threads}").wait()

class CleanSistrWorkflow(Command):
    """
    Clean up the output from running SISTR workflow
    """

    name = "clean"

    options = [
        option("snakefile", "s", "Snakefile used for run", default='Snakefile.sistr', value_required=True),
        option("config", "c", "Config file to remove", default="config_sistr.yaml", value_required=True),
        option("input_file", "i", "Input file to remove", default="input_sistr.txt", value_required=True),
        option("all", "a", "Delete all files including Snakefile, config, and input files?")
    ]

    def handle(self):
        self.comment("Removing all outputs from SISTR workflow.")
        snakemake = sh.Command('snakemake')
        runsk = snakemake("-s", self.option('snakefile'), "--delete-all-output")
        if self.option("all"):
            self._unlink(self.option("snakefile"))
            self._unlink(self.option("config"))
            self._unlink(self.option("input_file"))

    def _unlink(self, filename):
        path = pathlib.Path(filename)
        if path.exists():
            self.comment(f"Removing {path}")
            path.unlink()
        else:
            self.comment(f"Did not find {apth}")

class UnlockSistrWorkflow(Command):
    """
    If workflow gets interrupted for some reason, unlock it.
    """

    name = "unlock"

    options = [
        option("snakefile", "s", "Snakefile used for run", default='Snakefile.sistr', value_required=True),
    ]

    def handle(self):
        snakemake = sh.Command('snakemake')
        runsk = snakemake("-s", self.option('snakefile'), "--unlock")
