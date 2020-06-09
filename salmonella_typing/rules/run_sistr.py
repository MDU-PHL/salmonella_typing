"""
Run Sistr
"""

import collections
import logging
import os
import tempfile
import subprocess
from sistr.sistr_cmd import sistr_predict
from sistr.src.writers import write
# from snakemake import shell

logging.basicConfig(level=logging.CRITICAL)
# os.environ["PYTHON_EGG_CACHE"] = "/tmp"
contigs = f"{snakemake.input}"
genome_name = f"{snakemake.params.genome_name}"
out = f"{snakemake.output.out}"

cmd = f"sistr -i {contigs} {genome_name} -f csv -o {out} --tmp-dir /tmp/sistr_cmd -m "
print(cmd)
subprocess.run(cmd, shell = True)
# Args = collections.namedtuple(
#     "args", ["run_mash", "no_cgmlst", "qc", "use_full_cgmlst_db"]
# )
# args = Args(True, False, False, False)

# with tempfile.TemporaryDirectory() as tempdir:
#     # print(tempdir) 
#     res = sistr_predict(
#         contigs, genome_name, tempdir, False, args
#     )
# prediction_outputs, cgmlst_results = res

# write(snakemake.output.out, "csv", [prediction_outputs], more_results=False)
