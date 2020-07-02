"""
Run Sistr
"""

import collections
import logging
import os
import tempfile
import subprocess
# from sistr.sistr_cmd import sistr_predict
# from sistr.src.writers import write
from snakemake import shell

logging.basicConfig(level=logging.CRITICAL)
# os.environ["PYTHON_EGG_CACHE"] = "/tmp"
contigs = f"{snakemake.input}"
genome_name = f"{snakemake.params.genome_name}"
out = f"{snakemake.output.out}"
tempdir = tempfile.TemporaryDirectory()
cmd = f"sistr -i {contigs} {genome_name} -f csv -o {out} --tmp-dir {tempdir.name} -m "
subprocess.run(cmd, shell = True)
