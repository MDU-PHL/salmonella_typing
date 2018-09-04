'''
Individual rules to apply to the data set to filter according to 
MMS136 

Each rule is a function. Rules must start with `rule_` and be named
in a way that is meaningful for the rule. 

The function must accept as input a pandas.DataFrame, and return a 
Series with Boolean values depending on whether the row is Pass or 
Fail
'''

import sys

import pandas as pd

if 'pytest' in sys.modules:
    ### SOME TEST DATA FOR DOCSTRING TESTS ###
    ### To test run:
    ###     PYTHONPATH=. pytest --doctest-modules rules.py

    test_data = "rule_test/sistr_test_rules.csv"
    test_tab = pd.read_csv(test_data)

### CRITERIA ###

# IMMEDIATE PASS
# Requires all the conditions below to be TRUE
# 1. That subspecies be enterica
# 2. That there be at least 300 matching cgMLST alleles
# 3. All serovar calls must match exactly (serovar, serovar_antigen, serovar_cgmlst)
pass_rules = [
    'must_be_subsp_enterica',
    'must_have_at_least_300_matching_alleles',
    'all_serovar_calls_must_match'
]

# TRIGGER A REVIEW IF
# Requires all conditions below to be TRUE
# 1. NOT all serovar calls match
# 2. Serogroup inference is present
# 3. All antigens have inferences (h1, h2, and o-antigen)

review_rules_1 = [
    '~all_serovar_calls_must_match',
    'serogroup_inference_must_be_present',
    'inferences_for_all_antigens_present'
]

# TRIGGER A REVIEW IF
# Requires all conditions below to be TRUE
# 1. NOT subspecies enterica
# 2. That there be at least 300 matching cgMLST alleles
# 3. All serovar calls must match exactly (serovar, serovar_antigen, serovar_cgmlst)

review_rules_2 = [
    '~must_be_subsp_enterica',
    'must_have_at_least_300_matching_alleles',
    'all_serovar_calls_must_match'
]

# IMMEDIATE FAIL
# Requires ANY conditions below to be TRUE
# 1. Fewer than 100 cgMLST loci were matched

fail_rules = [
    'must_have_fewer_100_matching_alleles',
    'no_antigens_or_serogroup_found'
]

# TRIGGER REVIEW BECAUSE OF EDGE CASE
# Edge cases were identified during the course of 
# validation and/or use that should be immediately 
# triggered for review.
# Three edge cases are currently being used, and 
# review should be triggered on any of the three

edge_case_rules = [
    'edge_case_dublin',
    'edge_case_enteritidis',
    'edge_case_monophasic_typhimurium'
]

criteria = {
    'PASS' : ' and '.join(pass_rules),
    'REVIEW_1': ' and '.join(review_rules_1),
    'REVIEW_2': ' and '.join(review_rules_2),
    'FAIL':  ' or '.join(fail_rules),
    'EDGE': ' or '.join(edge_case_rules)
}

### RULES ###

def rule_must_be_subsp_enterica(tab):
    '''
    To pass this rule SISTR must have identified the sample as 
    subspecies entrica.

    >>> rule_must_be_subsp_enterica(test_tab)
    0      True
    1      True
    2      True
    3      True
    4      True
    5     False
    6     False
    7      True
    8      True
    9     False
    10     True
    11     True
    Name: must_be_subsp_enterica, dtype: bool
    '''
    mask = tab.cgmlst_subspecies == 'enterica'
    mask.name = "must_be_subsp_enterica"
    return mask

def rule_must_have_at_least_300_matching_alleles(tab):
    '''
    To pass this rule SISTR must have identified at least 300 
    matching alleles to its cgMLST scheme

    >>> rule_must_have_at_least_300_matching_alleles(test_tab)
    0      True
    1      True
    2      True
    3      True
    4      True
    5     False
    6     False
    7      True
    8      True
    9      True
    10     True
    11     True
    Name: must_have_at_least_300_matching_alleles, dtype: bool
    '''
    mask = tab.cgmlst_matching_alleles >= 300
    mask.name = "must_have_at_least_300_matching_alleles"
    return mask

def rule_must_have_fewer_100_matching_alleles(tab):
    '''
    To pass this rule SISTR must have identified fewer than 
    100 alleles to its cgMLST scheme

    This rule should lead to an automatic FAIL.

    >>> rule_must_have_fewer_100_matching_alleles(test_tab)
    0     False
    1     False
    2     False
    3     False
    4     False
    5     False
    6      True
    7     False
    8     False
    9     False
    10    False
    11    False
    Name: must_have_fewer_100_matching_alleles, dtype: bool
    '''
    mask = tab.cgmlst_matching_alleles < 100
    mask.name = "must_have_fewer_100_matching_alleles"
    return mask

def rule_inferences_for_all_antigens_present(tab):
    '''
    To pass this rule SISTR must have identified results for 
    all antigens: h1,h2,o_antigen

    At the moment, a missing prediction is identified with a "-"

    >>> rule_inferences_for_all_antigens_present(test_tab)
    0     False
    1      True
    2      True
    3     False
    4     False
    5     False
    6     False
    7      True
    8     False
    9      True
    10    False
    11    False
    Name: inferences_for_all_antigens_present, dtype: bool
    '''
    missing_marker = "-"
    query = f"h1 != '{missing_marker}' and h2 != '{missing_marker}' and o_antigen != '{missing_marker}'"
    mask = tab.eval(query)
    mask.name = "inferences_for_all_antigens_present"
    return mask

def rule_all_serovar_calls_must_match(tab):
    '''
    The three columns: serovar,serovar_antigen,serovar_cgmlst must match exactly.

    >>> rule_all_serovar_calls_must_match(test_tab)
    0      True
    1     False
    2      True
    3      True
    4     False
    5     False
    6     False
    7     False
    8      True
    9      True
    10    False
    11    False
    Name: all_serovar_calls_must_match, dtype: bool
    '''
    query = 'serovar == serovar_antigen == serovar_cgmlst'
    mask = tab.eval(query)
    mask.name = "all_serovar_calls_must_match"
    return mask

def rule_serogroup_inference_must_be_present(tab):
    '''
    The serogroup column must have a call. In other words, it cannot be "-"

    >>> rule_serogroup_inference_must_be_present(test_tab)
    0      True
    1      True
    2      True
    3      True
    4      True
    5     False
    6     False
    7      True
    8      True
    9      True
    10     True
    11     True
    Name: serogroup_inference_must_be_present, dtype: bool
    '''
    query = "serogroup != '-'"
    mask = tab.eval(query)
    mask.name = "serogroup_inference_must_be_present"
    return mask


def rule_no_antigens_or_serogroup_found(tab):
    '''
    To pass this rule, SISTR must not have found any antigens and was not able to infer a serogroup.

    In other words:
    h1="-"
    h2="-"
    o_antigen="-",
    serogroup="-"

    >>> rule_no_antigens_or_serogroup_found(test_tab)
    0     False
    1     False
    2     False
    3     False
    4     False
    5      True
    6      True
    7     False
    8     False
    9     False
    10    False
    11    False
    Name: no_antigens_or_serogroup_found, dtype: bool
    '''
    query = ' == '.join([
        'h1',
        'h2',
        'o_antigen',
        'serogroup',
        '"-"'
    ])
    mask = tab.eval(query)
    mask.name = 'no_antigens_or_serogroup_found'
    return mask

### EDGE CASES ###

def rule_edge_case_dublin(tab):
    '''
    It has been noticed that SISTR will sometimes classify Dublin samples
    as Enteritidis. This happens when:
    h1="g,p"
    h2="-"
    o_antigen="1,9,12"
    serogroup="D1"
    serovar=serovar_cgmlst="Enteritidis"
    serovar_antigen="Blegdam|Dublin|Enteritidis|Gueuletapee|Hillingdon|Kiel|Moscow|Naestved|Nitra|Rostock"

    >>> rule_edge_case_dublin(test_tab)
    0     False
    1     False
    2     False
    3     False
    4     False
    5     False
    6     False
    7     False
    8     False
    9     False
    10    False
    11     True
    Name: edge_case_dublin, dtype: bool
    '''
    query = ' and '.join([
        'h1=="g,p"',
        'h2=="-"',
        'o_antigen=="1,9,12"',
        'serogroup=="D1"',
        'serovar=="Enteritidis"',
        'serovar_antigen=="Blegdam|Dublin|Enteritidis|Gueuletapee|Hillingdon|Kiel|Moscow|Naestved|Nitra|Rostock"'
    ])
    mask = tab.eval(query)
    mask.name = 'edge_case_dublin'
    return mask

def rule_edge_case_enteritidis(tab):
    '''
    It has been noticed that SISTR will sometimes have trouble classifying Enteritidis samples
    This happens when:
    h1="g,m"
    h2="-"
    o_antigen="1,9,12"
    serogroup="D1"
    serovar=serovar_cgmlst="Enteritidis"
    serovar_antigen="Blegdam|Dublin|Enteritidis|Gueuletapee|Hillingdon|Kiel|Moscow|Naestved|Nitra|Rostock"

    **NOTE** this is one element different from the Dublin edge case. Here, h1="g,m". In the
    Dublin case it is h1="g,p"

    >>> rule_edge_case_enteritidis(test_tab)
    0     False
    1     False
    2     False
    3     False
    4     False
    5     False
    6     False
    7     False
    8     False
    9     False
    10     True
    11    False
    Name: edge_case_enteritidis, dtype: bool
    '''
    query = ' and '.join([
        'h1=="g,m"',
        'h2=="-"',
        'o_antigen=="1,9,12"',
        'serogroup=="D1"',
        'serovar=="Enteritidis"',
        'serovar_antigen=="Blegdam|Dublin|Enteritidis|Gueuletapee|Hillingdon|Kiel|Moscow|Naestved|Nitra|Rostock"'
    ])
    mask = tab.eval(query)
    mask.name = 'edge_case_enteritidis'
    return mask

def rule_edge_case_monophasic_typhimurium(tab):
    '''
    It has been noticed that SISTR will often classify monophasic Typhimurium as 
    Typhimurium
    This happens when:
    h1="i"
    h2="-"
    o_antigen="1,4,[5],12"
    serogroup="B"
    serovar="Typhimurium"
    serovar_antigen="I 4,[5],12:i:-" 

    >>> rule_edge_case_monophasic_typhimurium(test_tab)
    0     False
    1     False
    2     False
    3     False
    4      True
    5     False
    6     False
    7     False
    8     False
    9     False
    10    False
    11    False
    Name: edge_case_monophasic_typhimurium, dtype: bool
    '''
    query = ' and '.join([
        'h1=="i"',
        'h2=="-"',
        'o_antigen=="1,4,[5],12"',
        'serogroup=="B"',
        'serovar=="Typhimurium"',
        'serovar_antigen=="I 4,[5],12:i:-"'
    ])
    mask = tab.eval(query)
    mask.name = 'edge_case_monophasic_typhimurium'
    return mask