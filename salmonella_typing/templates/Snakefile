'''
A Snakefile for Salmonella typing at MDU
'''

import pandas

configfile: 'config_sistr.yaml'
input_file = config['input_file']
stm_control = config['stm_control']

SAMPLES = pandas.read_csv(input_file, sep=None, engine='python',
                          encoding='utf8').set_index("SEQID", drop=False)


def get_asm(wildcards):
    return SAMPLES.loc[wildcards.sample]["ASM"]


rule all:
    input:
        "SISTR_LIMS.xlsx",
        input_file

rule test_controls:
    input:
        stm = stm_control,
    output:
        "sistr_control.csv"
    params:
        prefix = "sistr_control"
    threads: 2
    shell:
        """
        DIR=$(mktemp -d)
        SISTR_DB=/opt/sistr_db
        PY_VERSION=$(python --version | cut -d" " -f2 | cut -f1,2 -d\.)
        PYTHON_EGG_CACHE=${{DIR}}/.python_egg_cache
        DATA_DIR=${{PYTHON_EGG_CACHE}}/sistr_cmd-${{SISTR_VERSION}}-py${{PY_VERSION}}.egg-tmp/sistr/data
        mkdir -p ${{DATA_DIR}}
        cp -R ${{SISTR_DB}} ${{DATA_DIR}}
        sistr -i "{input.stm}" "9999-99999-1" -f csv -o {params.prefix} -T $DIR --qc --threads {threads}
        rm -rf ${{DIR}}
        """

rule run_sistr:
    input:
        "sistr_control.csv",
        asm = get_asm

    output:
        "{sample}/sistr.csv"
    threads: 2
    shell:
        """
        DIR=$(mktemp -d)
        SISTR_DB=/opt/sistr_db
        PY_VERSION=$(python --version | cut -d" " -f2 | cut -f1,2 -d\.)
        PYTHON_EGG_CACHE=${{DIR}}/.python_egg_cache
        DATA_DIR=${{PYTHON_EGG_CACHE}}/sistr_cmd-${{SISTR_VERSION}}-py${{PY_VERSION}}.egg-tmp/sistr/data
        mkdir -p ${{DATA_DIR}}
        cp -R ${{SISTR_DB}} ${{DATA_DIR}}
        sistr -i {input.asm:q} {wildcards.sample} -f csv -o {wildcards.sample}/sistr -T $DIR --qc --threads {threads}
        rm -rf ${{DIR}}
        """

rule gather:
    input: expand("{sample}/sistr.csv", sample=SAMPLES.index)
    output: "sistr_concat.csv"
    run:
        import pandas
        combined_tab = pandas.concat(
            [pandas.read_csv(f, engine='python', sep=None) for f in input])
        combined_tab.to_csv(output[0], index=False)

rule process_results:
    input:
        res = "sistr_concat.csv",
        cont = "sistr_control.csv"
    output:
        "SISTR_LIMS.xlsx"
    params:
        prefix = "SISTR_LIMS"
    shell:
        '''
        stype_cli.py parse -l -p {params.prefix} {input.cont} {input.res}
        '''
