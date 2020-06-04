"""
A rule to sistr on each samples
"""
import pandas

include: "common.smk"

input_file = config.get("input_file", "../tests/input.txt")
index_col = config.get("index_col", "ID")

SAMPLES = pandas.read_csv(input_file, sep=None, engine='python',
                              encoding='utf8').set_index(index_col, drop=False)

rule gather:
    input: expand("{sample}/sistr.csv", sample=SAMPLES.index)
    output: "sistr_concat.csv"
    run:
        import pandas
        combined_tab = pandas.concat(
            [pandas.read_csv(f, engine='python', sep=None) for f in input])
        combined_tab.to_csv(output[0], index=False)

rule run_sistr:
    input:
        contigs = get_asm
    output:
        out="{sample}/sistr.csv"
    params:
        genome_name="{sample}"
    script: "run_sistr.py"

