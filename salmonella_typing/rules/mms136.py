
import inspect
import pathlib
import pandas
from . import rules
from . import filters


tab = pandas.read_csv(f"{snakemake.input}")

output_file = f"{snakemake.output_file}"

rule_list = [
    (name, function)
    for name, function in inspect.getmembers(rules, inspect.isfunction)
    if name.startswith("rule_")
]
criteria = rules.criteria
filter_list = [
    (name, function)
    for name, function in inspect.getmembers(filters, inspect.isfunction)
    if name.startswith("filter_")
]

def apply_rules(tab, rule_list, criteria):

    for rule, func in rule_list:
        tab[rule] = func(tab) #for each rule, make a column by applying rules
    
    for k in criteria:
            tab[k] = tab.eval(criteria[k])

    tab['CONSISTENT'] = tab[list(criteria)].sum(axis=1)

    return tab

def filter_rules(tab, filter_list):
    tab['serovar-original'] = tab.serovar
    filt_list = []
    for filt, func in filter_list:
        tab[filt] = func(tab) #for each filter add a column which corresponds to filter to the df
        filt_list.append(filt)
    tab['FILTERS'] = tab[filt_list].apply(lambda x: sum(~x.isnull()), axis=1)
    tab['serovar'] = tab.apply(lambda x: x.serovar if x[filt_list].isnull().all() else x[filt_list].dropna()[0], axis=1)

    return tab

def call_status(tab):

    PASS = tab['PASS']
    REVIEW = tab.loc[:, self._obj.columns.str.startswith('REVIEW')].any(axis=1)
    FAIL = tab['FAIL']
    EDGE = tab['EDGE']
    CONSISTENT = tab['CONSISTENT'] == 1 # True of False if this column == 1
    FILTERS_OK = tab['FILTERS'] <= 1 # True of False if this column <= 1
    conditions = [
        (PASS & CONSISTENT & FILTERS_OK),
        (REVIEW & CONSISTENT & FILTERS_OK),
        (EDGE & CONSISTENT & FILTERS_OK),
        (FAIL & CONSISTENT & FILTERS_OK)
    ]
    choices = ['PASS', 'REVIEW', 'REVIEW, EDGE', 'FAIL']
    tab['STATUS'] = np.select(conditions, choices, default='REVIEW, INCONSISTENT')

    return tab

# apply rules
tab = apply_rules(tab = tab, rule_list=rule_list, criteria=criteria)

# apply filters
tab = filter_rules(tab = tab, filter_list = filter_list)

# call status
tab = call_status(tab)

# save table to output
tab.to_csv(output_file, index = False)