"""
Run Sistr
"""

import collections
import logging
import os
import tempfile
from sistr.sistr_cmd import sistr_predict
from sistr.src.writers import write

logging.basicConfig(level=logging.CRITICAL)
# os.environ["PYTHON_EGG_CACHE"] = "/tmp"

Args = collections.namedtuple(
    "args", ["run_mash", "no_cgmlst", "qc", "use_full_cgmlst_db"]
)
args = Args(True, False, False, False)

with tempfile.TemporaryDirectory() as tempdir:
    res = sistr_predict(
        snakemake.input.contig, snakemake.params.genome_name, tempdir, False, args
    )
prediction_outputs, cgmlst_results = res

write(snakemake.output.out, "csv", [prediction_outputs], more_results=False)
