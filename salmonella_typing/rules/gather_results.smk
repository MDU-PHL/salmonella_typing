rule process_results:
    input:
        res = outputs
    output:
        out = "salmonella_typing.csv"
    run:
        import pandas as pd
        res = [pd.read_csv(fn, engine="python", sep=None) for fn in input.res]
        tab = pd.concat(res, sort=True)
        tab.to_csv(output.out, index=False)
