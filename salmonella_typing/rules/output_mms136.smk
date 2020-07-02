# apply rules here

rule apply_rules:
    input:
        "salmonella_typing.csv"
    output:
        "salmonella_typing_lims.csv"
    script:
        "mms136.py"
        

