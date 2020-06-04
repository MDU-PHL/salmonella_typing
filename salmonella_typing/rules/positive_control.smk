"""
A rule for positive control
"""

include: "common.smk"

rule test_controls:
    input:
        contig = get_positive_control
    output:
        out="sistr_control.csv"
    log: "positive_control.log"
    params:
        genome_name="9999-99999-1"
    script: "run_sistr.py"
