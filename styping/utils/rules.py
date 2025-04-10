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
# 3. All serovar calls must match exactly (serovar, serovar_antigen, serovar_cgmlst) OR following update to sistr nomenclature where serovar and serovar_cgmslt match and this string is contained in serovar_antigen (since new nomenclature means at times multiple are reported separated by a |)
pass_rules = [
    'rule_must_be_subsp_enterica',
    'rule_must_have_at_least_300_matching_alleles',
    'rule_all_serovar_calls_must_match'
]

# TRIGGER A REVIEW IF
# Requires all conditions below to be TRUE
# 1. NOT all serovar calls match
# 2. Serogroup inference is present
# 3. All antigens have inferences (h1, h2, and o-antigen)

review_rules_1 = [
    '~rule_all_serovar_calls_must_match',
    'rule_serogroup_inference_must_be_present',
    'rule_inferences_for_all_antigens_present'
]

# TRIGGER A REVIEW IF
# Requires all conditions below to be TRUE
# 1. NOT subspecies enterica
# 2. That there be at least 300 matching cgMLST alleles
# 3. All serovar calls must match exactly (serovar, serovar_antigen, serovar_cgmlst)

review_rules_2 = [
    '~rule_must_be_subsp_enterica',
    'rule_must_have_at_least_300_matching_alleles',
    'rule_all_serovar_calls_must_match'
]

# IMMEDIATE FAIL
# Requires ANY conditions below to be TRUE
# 1. Fewer than 100 cgMLST loci were matched

fail_rules = [
    'rule_must_have_fewer_100_matching_alleles',
    'rule_no_antigens_or_serogroup_found'
]

# TRIGGER REVIEW BECAUSE OF EDGE CASE
# Edge cases were identified during the course of 
# validation and/or use that should be immediately 
# triggered for review.
# Two edge cases are currently being used, and 
# review should be triggered on any of the three

edge_case_review_rules = [
    'rule_edge_case_dublin',
    'rule_edge_case_monophasic_typhimurium',
    'rule_edge_case_paratyphiBvJava',
    'rule_edge_case_paratyphiB'
]

# TRIGGER AN AUTOMATIC PASS OF EDGE CASE
# Edge cases were identified during the course of 
# validation and/or use that can be PASSED immediately 
# Currently, one edge case meets that criteria: Enteritidis
edge_case_pass_rules = [
    'rule_edge_case_enteritidis',
    'rule_edge_case_sbg_wshmptn',
    'rule_edge_case_tm_abony'
]

def build_rules(*args, is_or=False):
    '''
    A function to build criteria based on sets of rules. This function is 
    used to build the criteria dictionary below, using the sets of rules
    defined above.

    Input:
    ------
    rules: one or more lists
    is_or: Bool (a boolean to indicate if the elements should be grouped by or --- only useful for single list of rules)

    Output:
    -------
    criteria: str (a string indicating how different groups of rules should be applied)
    '''
    rule_sets = [*args]
    rules = []
    if len(rule_sets) > 1:
        for rule_set in rule_sets:
            sep = ' and '
            for rule in rule_set:
                if 'edge' in rule:
                    sep = ' or '
            rules.append(f"({sep.join(rule_set)})")
        rules = ' or '.join(rules)
    else:
        bool_operator = ' and ' if not is_or else ' or '
        rules = '(' + bool_operator.join(rule_sets[0]) + ')'
    return rules

criteria = {
    'PASS' : build_rules(pass_rules, edge_case_pass_rules),
    'REVIEW_1': build_rules(review_rules_1),
    'REVIEW_2': build_rules(review_rules_2),
    'FAIL':  build_rules(fail_rules, is_or=True),
    'EDGE': build_rules(edge_case_review_rules, is_or=True)
}

### RULES ###

def rule_must_be_subsp_enterica(tab):
    '''
    To pass this rule SISTR must have identified the sample as 
    subspecies entrica.

    >>> res = rule_must_be_subsp_enterica(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.rule_must_be_subsp_enterica)
    '''
    mask = tab.cgmlst_subspecies == 'enterica'
    mask.name = "rule_must_be_subsp_enterica"
    return mask

def rule_must_have_at_least_300_matching_alleles(tab):
    '''
    To pass this rule SISTR must have identified at least 300 
    matching alleles to its cgMLST scheme

    >>> res = rule_must_have_at_least_300_matching_alleles(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.rule_must_have_at_least_300_matching_alleles)
    '''
    mask = tab.cgmlst_matching_alleles >= 300
    mask.name = "rule_must_have_at_least_300_matching_alleles"
    return mask

def rule_must_have_fewer_100_matching_alleles(tab):
    '''
    To pass this rule SISTR must have identified fewer than 
    100 alleles to its cgMLST scheme

    This rule should lead to an automatic FAIL.

    >>> res = rule_must_have_fewer_100_matching_alleles(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.rule_must_have_fewer_100_matching_alleles)
    '''
    mask = tab.cgmlst_matching_alleles < 100
    mask.name = "rule_must_have_fewer_100_matching_alleles"
    return mask

def rule_inferences_for_all_antigens_present(tab):
    '''
    To pass this rule SISTR must have identified results for 
    all antigens: h1,h2,o_antigen

    At the moment, a missing prediction is identified with a "-"

    >>> res = rule_inferences_for_all_antigens_present(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.rule_inferences_for_all_antigens_present)
    '''
    missing_marker = "-"
    query = f"h1 != '{missing_marker}' and h2 != '{missing_marker}' and o_antigen != '{missing_marker}'"
    mask = tab.eval(query)
    mask.name = "rule_inferences_for_all_antigens_present"
    return mask

def rule_all_serovar_calls_must_match(tab):
    '''
    The three columns: serovar,serovar_antigen,serovar_cgmlst must match exactly.

    >>> res = rule_all_serovar_calls_must_match(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.rule_all_serovar_calls_must_match)
    '''
    def check(row):
        if row['serovar'] == row['serovar_cgmlst'] and row['serovar'] in row['serovar_antigen']:
            return True
        else:
            return False
    # query = 'serovar == serovar_antigen == serovar_cgmlst'
    mask = tab.apply(lambda x:check(x), axis = 1)
    mask.name = "rule_all_serovar_calls_must_match"
    return mask

def rule_serogroup_inference_must_be_present(tab):
    '''
    The serogroup column must have a call. In other words, it cannot be "-"

    >>> res =  rule_serogroup_inference_must_be_present(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.rule_serogroup_inference_must_be_present)
    '''
    query = "serogroup != '-'"
    mask = tab.eval(query)
    mask.name = "rule_serogroup_inference_must_be_present"
    return mask


def rule_no_antigens_or_serogroup_found(tab):
    '''
    To pass this rule, SISTR must not have found any antigens and was not able to infer a serogroup.

    In other words:
    h1="-"
    h2="-"
    o_antigen="-",
    serogroup="-"

    >>> res = rule_no_antigens_or_serogroup_found(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.rule_no_antigens_or_serogroup_found)
    '''
    query = ' == '.join([
        'h1',
        'h2',
        'o_antigen',
        'serogroup',
        '"-"'
    ])
    mask = tab.eval(query)
    mask.name = 'rule_no_antigens_or_serogroup_found'
    return mask

### EDGE CASES ###

def rule_edge_case_paratyphiBvJava(tab):
    '''
    During re-verification it was noted that sistr 1.1.1 would call a paratyphi B and paratyphi B var Java incorrectly when some cgmlst genomes were identified as the closest match.
    This happens when:
    cgmlst_genome_match is one of ['SRR1970070', 'SRR1968302','SRR1967079','SRR1965379','SRR1968102'] sistr 1.1.1 calls Paratyphi B when it SHOULD BE Paratyphi B var. Java
    and serovar == serovar_cgmlst == Paratyphi B
    and serovar_antigen == Paratyphi B|Paratyphi B var. Java|Limete
    and o_antigen == 1,4,[5],12
    and h1 = b
    and h2 = 1,2
    '''

    def check(row):
        varjava_genomes = ['SRR1970070', 'SRR1968302','SRR1967079','SRR1965379','SRR1968102']
        if (row['cgmlst_genome_match'] in varjava_genomes) & (row['serovar'] == 'Paratyphi B')& (row['serovar_cgmlst'] == 'Paratyphi B')& (row['serovar_antigen'] == 'Paratyphi B|Paratyphi B var. Java|Limete')& (row['o_antigen'] == '1,4,[5],12') & (row['h1'] == 'b')& (row['h2'] == '1,2'):
            return True
        else:
            return False

    mask = tab.apply(lambda x:check(x), axis = 1)
    mask.name = rule_edge_case_paratyphiBvJava
    return mask

def rule_edge_case_paratyphiB(tab):
    '''
    During re-verification it was noted that sistr 1.1.1 would call a paratyphi B and paratyphi B var Java incorrectly when some cgmlst genomes were identified as the closest match.
    This happens when:
    cgmlst_genome_match is one of ['17-7324', '17-2557'] sistr 1.1.1 calls Paratyphi B var Java when it SHOULD BE Paratyphi B 
    and serovar == serovar_cgmlst == Paratyphi B var. Java
    and serovar_antigen == Paratyphi B|Paratyphi B var. Java|Limete
    and o_antigen == 1,4,[5],12
    and h1 = b
    and h2 = 1,2
    '''

    def check(row):
        varjava_genomes = ['17-7324', '17-2557']
        if (row['cgmlst_genome_match'] in varjava_genomes) & (row['serovar'] == 'Paratyphi B var. Java') & (row['serovar_cgmlst'] == 'Paratyphi B var. Java') & (row['serovar_antigen'] == 'Paratyphi B|Paratyphi B var. Java|Limete') & (row['o_antigen'] == '1,4,[5],12') & (row['h1'] == 'b')& (row['h2'] == '1,2'):
            return True
        else:
            return False

    mask = tab.apply(lambda x:check(x), axis = 1)
    mask.name = rule_edge_case_paratyphiB
    return mask



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

    >>> res = rule_edge_case_dublin(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.rule_edge_case_dublin)
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
    mask.name = 'rule_edge_case_dublin'
    return mask

def rule_edge_case_sbg_wshmptn(tab):
    '''
    sistr v1.1.1 seems to have some odd genomes in the cgmlst database and will call serovar_antigen Westhampton a Senftenberg resulting in a REVIEW when it should be a PASS
    This happens when:
    cgmlst_genome_match == 'SRR1965561'
    and serovar_antigen == serovar == Senftenberg 
    and serovar_cgmlst == Westhampton
    and h1 == g,[s],t
    and h2 == -
    and o_antigen == 1,3,19
    '''
    query = ' and '.join(['cgmlst_genome_match=="SRR1965561"', 'h1=="g,[s],t"', 'h2=="-"', 'o_antigen=="1,3,19"','serovar_antigen=="Senftenberg"','serovar=="Senftenberg"', 'serovar_cgmlst=="Westhampton"' ])
    mask = tab.eval(query)
    mask.name = 'rule_edgecase_sbg_wshmptn'
    return mask

def rule_edge_case_tm_abony(tab):
    '''
    sistr v1.1.1 seems to have some odd genomes in the cgmlst database and will call serovar_antigen Tm|Lagos an Abony resulting in a REVIEW when it should be a PASS
    This happens when:
    cgmlst_genome_match == '2015-SEQ-0411'
    '''
    query = ' and '.join(['cgmlst_genome_match=="2015-SEQ-0411"', 'h1=="i"', 'h2=="1,2"', 'o_antigen=="-"','serovar_antigen=="Typhimurium|Lagos"','serovar=="Typhimurium|Lagos"', 'serovar_cgmlst=="Abony"'])
    mask = tab.eval(query)
    mask.name = 'rule_edgecase_tm_abony'
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

    >>> res = rule_edge_case_enteritidis(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.rule_edge_case_enteritidis)
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
    mask.name = 'rule_edge_case_enteritidis'
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

    >>> res = rule_edge_case_monophasic_typhimurium(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.rule_edge_case_monophasic_typhimurium)
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
    mask.name = 'rule_edge_case_monophasic_typhimurium'
    return mask

def rule_edge_case_sophia(tab):
    '''
    It has been noticed that SISTR will incorrectly classify Sophia serovars
    as Paratyphi B, when Sophia is subspecies salamae
    This happens when:
    cgmlst_subspecies="salamae"
    h1="b"
    h2="-" # missing
    serogroup="B"
    serovar="Paratyphi B var. Java monophasic"
    serovar_antigen=="II 1,4,[5],12,[27]:b:[e,n,x]"

    >>> res = rule_edge_case_sophia(test_tab)
    >>> pd.testing.assert_series_equal(res, test_tab.rule_edge_case_sophia)
    '''
    query = ' and '.join([
        'cgmlst_subspecies=="salamae"',
        'h1=="b"',
        'h2=="-"',
        'o_antigen=="1,4,12,27"',
        'serogroup=="B"',
        'serovar=="Paratyphi B var. Java monophasic"',
        'serovar_antigen=="II 1,4,[5],12,[27]:b:[e,n,x]"'
    ])
    mask = tab.eval(query)
    mask.name = "rule_edge_case_sophia"
    return mask
