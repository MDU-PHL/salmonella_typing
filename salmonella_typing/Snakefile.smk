'''
A Snakefile for Salmonella typing at MDU
'''

import tempfile
import pathlib
import pandas

configfile: 'config_sistr.yaml'
input_file = config['input_file']
stm_control = config['stm_control']
# mdu_qc = config['is_mdu_qc']
outfile = config.get("outfile", "salmonella_typing_lims.csv")
print(outfile)

rule all:
    input: outfile

include: "rules/positive_control.smk"

if pathlib.Path(input_file).exists():
    outputs = ["sistr_concat.csv", "sistr_control.csv"]
    include: "rules/run_sample.smk"
else:
    outputs = ["sistr_control.csv"]

include: "rules/gather_results.smk"

include: "rules/output_mms136.smk"
