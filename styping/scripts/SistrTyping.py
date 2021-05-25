'''
Run MDU sistr typing
'''

import pathlib
import os
import tempfile
import contextlib
import subprocess
import pandas
import jinja2
import sh
from cleo import Command, argument, option


@contextlib.contextmanager
def working_directory(path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = pathlib.Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


class RunSistrWorkflow(Command):
    '''
    Run SISTR typing following MMS136
    '''

    name = 'run'

    arguments = [
        argument("input_file", description="Table of isolates and path to assembly", required=True)
    ]

    options = [
        option("mdu_qc", "m", "If set, assume input is MDU QC input"),
        option("prefix", "p", "Prefix for naming output file.", default = "sistr", value_required = True),
        option("workdir", "w", "Change working directory",
               default=f"{pathlib.Path.cwd().absolute()}", value_required=True),
        option("fields", "f", "If input file has no header, use this comma-separated list of values (e.g., -f 'ID,ASM').",
               default=None, value_required=True),
        option("resource_path", "r", "Path to Snakefile and config.yaml templates to use",
               default=f"{pathlib.Path(__file__).parent.parent }", value_required=True),
        option("control_path", "c", "Path to FASTA for positive controls to use",
               default=f"{pathlib.Path(__file__).parent.parent / 'data'}", value_required=True),
        option("threads", "t", "How many threads to give Snakemake",
               default=2, value_required=True)
    ]

    def handle(self):
        input_file = pathlib.Path(self.argument("input_file"))
        
        if self.option("mdu_qc"):
            # input_file = pathlib.Path("distribute_table.txt")
            path_to_assemblies = "QC/"
            qc = 'true'
            workdir = "QC/"
            mms136 = 'true'
        else:
            
            workdir = self.option("workdir")
            path_to_assemblies = workdir
            qc = 'false'
            mms136 = 'false'
            self._read_input(input_file, self.option("fields"))
        
        self._exists(input_file)
        self._exists(pathlib.Path(workdir))

        resource_path = pathlib.Path(self.option('resource_path'))
        self._exists(resource_path)
        control_path = pathlib.Path(self.option('control_path'))
        prefix = self.option('prefix')
        self._exists(control_path)
        self._setup_working_dir(input_file, workdir, self.option("mdu_qc"), control_path)
        self._write_workflow(prefix,path_to_assemblies, qc, mms136,resource_path, workdir)
        self._run_workflow(workdir, self.option("threads"), resource_path)
        
    def _exists(self, path):
        if not path.exists():
            self.error(f"Could not find {path.name}")
            raise FileNotFoundError(f"{path.name}")
        # else:
        #     self.info(f"Found {path.name}.")
    def _setup_working_dir(self, input_file, workdir, is_mdu_qc, positive):
        '''
        open input file and copy assemblies to sample directories
        '''
        poscmd = f"mkdir -p {workdir}/9999-99999-1 && cp {positive}/SentericaLT2.fasta  {workdir}/9999-99999-1/contigs.fa"
        subprocess.run(poscmd, shell = True)
        if not is_mdu_qc:
            self.comment("Setting up directory.")
            for row in self.tab.iterrows():
                seq = row[1]['SEQID']
                ctgs = row[1]['ASM']
                self._exists(pathlib.Path(ctgs))
                tg_dir = pathlib.Path(workdir, seq)
                if not tg_dir.exists():
                    tg_dir.mkdir()
                
                cmd = f"cp -n {ctgs} {tg_dir}/contigs.fa"
                subprocess.run(cmd, shell = True)

    def _read_input(self, filename, fields):
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
        
        tab = pandas.read_csv(filename, sep=None, engine='python',
                              encoding='utf8', header=header, names=names)

        if 'ASM' not in tab.columns:
            self.error(
                f"{filename} does not include a field called ASM with the path to the assembly.")
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
                tab = tab.rename(columns={tab.columns[0]: 'SEQID'})
        self.tab = tab

    def _write_workflow(self, prefix,path_to_assemblies, qc, mms136,resources, workdir):
        '''
        Load Snakefile file and config.yaml templates
        '''
        self.info("Setting up configuration.")        
        cfg_dict = {
            'prefix': prefix,
            'path_to_assemblies': path_to_assemblies,
            'workdir': workdir,
            'qc': qc,
            'mms136': mms136
        }
        cfg_tmpl = jinja2.Template(pathlib.Path(
            resources,'templates', 'nextflow.config.j2').read_text())
        cfg = pathlib.Path('nextflow.config')
        cfg.write_text(cfg_tmpl.render(cfg_dict))

        # skf_tmpl = resources / 'Snakefile'
        # skf = workdir / 'Snakefile.sistr'
        # skf.write_text(skf_tmpl.read_text())

        self.info(f"Successfully wrote workflow to {cfg.parent}")

    def _run_workflow(self, workdir, threads, resources):
        '''
        Given all the elements have been put in place, run the workflow
        '''
    
        # os.chdir(workdir)
        # snakemake = sh.Command('snakemake')
        # runwf = snakemake("-s", "Snakefile.sistr", "-j", f"{threads}").wait()
        cmd = f"nextflow {pathlib.Path(resources, 'main.nf')} -resume"
        wkf = subprocess.run(cmd, shell = True)
        while True:
            if wkf.stdout != None:
                line = wkf.stdout.readline().strip()
                if not line:
                    break
            line = ''
            break
            self.info(f"{line}")
        



class CleanSistrWorkflow(Command):
    """
    Clean up the output from running SISTR workflow
    """

    name = "clean"

    # options = [
    #     option(
    #         "all", "a", "Delete all files including .nextflow.log, config, cached results and input files?")
    # ]

    def handle(self):
        self.comment("Removing all outputs from SISTR workflow.")
        
        self._remove()

    def _remove(self):
        to_remove = ['.nextflow.log*', 'nextflow.config', 'work']
        for t in to_remove:
            cmd = f"rm -rf {t}"
            self.info(cmd)
            subprocess.run(cmd, shell = True)
