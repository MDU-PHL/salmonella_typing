"""
Common functions for Snakefile
"""

def get_asm(wildcards):
    return SAMPLES.loc[wildcards.sample]["ASM"]

def get_positive_control(wildcards):
    positive_control = config.get("stm_control", None)
    if positive_control is None:
        positive_control = "../data/SentericaLT2.fasta"
    return positive_control
    