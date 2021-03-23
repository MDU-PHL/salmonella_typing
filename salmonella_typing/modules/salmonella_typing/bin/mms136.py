#!/usr/bin/env python3
import inspect
import numpy as np
import pathlib
import pandas
import rules
import filters
import sys

MDUIDREG = re.compile(r'(?P<id>[0-9]{4}-[0-9]{5,6})-?(?P<itemcode>.{1,2})?')

tab = pandas.read_csv(sys.argv[1])

output_prefix = sys.argv[2]

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
    REVIEW = tab.loc[:, tab.columns.str.startswith('REVIEW')].any(axis=1)
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
def assign_itemcode(mduid):
    m = MDUIDREG.match(mduid)
    itemcode = m.group('itemcode') if m.group('itemcode') else ''
    return itemcode

def assign_mduid(mduid):
    m = MDUIDREG.match(mduid)
    mduid = m.group('id')
    return mduid

def make_spreadsheet(tab, prefix):
    tab = tab.rename(columns = {'genome': 'SEQID'})
    tab['ID'] = tab['SEQID'].apply(lambda x:assign_mduid(x), axis = 1)
    tab['ITEMCODE'] = tab['SEQID'].apply(lambda x:assign_itemcode(x), axis = 1)
    cols = ["ID","ITEMCODE","SEQID","cgmlst_subspecies","cgmlst_matching_alleles","serovar_cgmlst","o_antigen","h1","h2","serogroup","serovar_antigen","serovar-original","serovar","STATUS"]
    mms136 = tab[tab['STATUS'] == 'PASS'][cols]
    review = tab[~tab['STATUS'].isin(['PASS', 'FAIL'])][cols]

    writer = pandas.ExcelWriter(f'{prefix}_sistr.xlsx')
    mms136.to_excel(writer, sheet_name = "MMS136")
    review.to_excel(writer, sheet_name = "REVIEW")
    tab.to_excel(writer, sheet_name = "ALL")
    writer.close()

# apply rules
tab = apply_rules(tab = tab, rule_list=rule_list, criteria=criteria)

# apply filters
tab = filter_rules(tab = tab, filter_list = filter_list)

# call status
tab = call_status(tab)

# save table to output
# tab.to_csv(output_file, index = False)
make_spreadsheet(tab, output_prefix)