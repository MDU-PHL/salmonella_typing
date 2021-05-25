#!/usr/bin/env python3
import inspect, pathlib, pandas, re, logging, subprocess
import numpy as np
from styping.CustomLog import CustomFormatter
import styping.utils.rules as rules
import styping.utils.filters as filters


LOGGER =logging.getLogger(__name__) 
LOGGER.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
fh = logging.FileHandler('styper.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s:%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') 
fh.setFormatter(formatter)
LOGGER.addHandler(ch) 
LOGGER.addHandler(fh)


class ParseSistr:
    """
    A class to apply business logic to sistr results to address discrepancies found during validation at MDU
    """
    # sistr_data = Data(self.run_type, self.input, self.prefix)
    def __init__(self, args):

        self.prefix = args.prefix
        self.run_type = args.run_type
        self.input = args.input


        self.rule_list = [
            (name, function)
            for name, function in inspect.getmembers(rules, inspect.isfunction)
            if name.startswith("rule_")
        ]
        self.criteria = rules.criteria

        self.filter_list = [
            (name, function)
            for name, function in inspect.getmembers(filters, inspect.isfunction)
            if name.startswith("filter_")
        ]

    def apply_rules(self, tab):
        
        for rule, func in self.rule_list:
            tab[rule] = func(tab) #for each rule, make a column by applying rules
        
        for k in self.criteria:
                tab[k] = tab.eval(self.criteria[k])

        tab['CONSISTENT'] = tab[list(self.criteria)].sum(axis=1)

        return tab

    def filter_rules(self,tab):
        tab['serovar-original'] = tab.serovar
        filt_list = []
        for filt, func in self.filter_list:
            tab[filt] = func(tab) #for each filter add a column which corresponds to filter to the df
            filt_list.append(filt)
        tab['FILTERS'] = tab[filt_list].apply(lambda x: sum(~x.isnull()), axis=1)
        tab['serovar'] = tab.apply(lambda x: x.serovar if x[filt_list].isnull().all() else x[filt_list].dropna()[0], axis=1)
    
        return tab

    def call_status(self, tab):

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

    def _run_concat(self, sistrs):

        cmd = f"csvtk concat {' '.join(sistrs)} > sistr_concatenated.csv"
        LOGGER.info(f"Concatenating results : {cmd}")
        p = subprocess.run(cmd, shell = True, capture_output = True , encoding = "utf-8")
        if p.returncode == 0:
            return True
        else:
            return False

    def _concat_sistr(self):

        sistrs = []
        LOGGER.info(f"Opening {self.input} to concatenate results")
        with open(self.input , 'r') as f:
            data = f.read().strip().split('\n')
            for d in data:
                cmd = d.split('\t')[0]
                sistrs.append(f"{cmd}/sistr.csv")
        if self._run_concat(sistrs):
            LOGGER.info(f"Concatenating sistr output to a single file.")
            return "sistr_concatenated.csv"
        else:
            LOGGER.critical(f"There seems that something has gone wrong with concatenating your sistr outputs. Please try again.")
            raise SystemExit

    def _get_input_file(self):

        input_file = f"{self.prefix}/sistr.csv" if self.run_type == 'assembly' else self._concat_sistr()

        return input_file

    def _filter_sistr(self, input_file):
        # get tab
        LOGGER.info(f"Opening {input_file}")
        tab = pandas.read_csv(input_file)
        LOGGER.info(f"Applying rules")
        # apply rules
        tab = self.apply_rules(tab = tab)
        # apply filters
        LOGGER.info(f"Applying filters")
        tab = self.filter_rules(tab = tab)
        # call status
        LOGGER.info(f"Calling status of each sample.")
        tab = self.call_status(tab)
        return tab


    def parse(self):
        input_file = self._get_input_file()
        tab = self._filter_sistr(input_file = input_file)
        outfile = 'sistr_filtered.csv' if self.run_type == 'batch' else f"{self.prefix}/sistr_filtered.csv"
        # save table to output
        LOGGER.info(f"Saving filtered results as {outfile}")
        tab.to_csv(f'{outfile}', index = False)

class MduifySistr:

    def __init__(self, args):
        self.runid = args.runid
        self.input = args.input
        self.MDUIDREG = re.compile(r'(?P<id>[0-9]{4}-[0-9]{5,6})-?(?P<itemcode>.{1,2})?')

    def make_spreadsheet(self, tab, prefix):
        # mdu specific functions... sub class?
        def assign_itemcode(mduid):
            m = self.MDUIDREG.match(mduid)
            itemcode = m.group('itemcode') if m.group('itemcode') else ''
            return itemcode

        def assign_mduid(mduid):
            m = self.MDUIDREG.match(mduid)
            mduid = m.group('id')
            return mduid
        LOGGER.info('Generating spreadsheet')
        tab = tab.rename(columns = {'genome': 'SEQID'})
        tab['ID'] = tab['SEQID'].apply(lambda x:assign_mduid(x))
        tab['ITEMCODE'] = tab['SEQID'].apply(lambda x:assign_itemcode(x))
        cols = ["ID","ITEMCODE","SEQID","cgmlst_subspecies","cgmlst_matching_alleles","serovar_cgmlst","o_antigen","h1","h2","serogroup","serovar_antigen","serovar-original","serovar","STATUS"]
        mms136 = tab[tab['STATUS'] == 'PASS'][cols]
        review = tab[~tab['STATUS'].isin(['PASS', 'FAIL'])][cols]
        LOGGER.info(f"Saving spreadsheet")
        writer = pandas.ExcelWriter(f'{prefix}_sistr.xlsx')
        mms136.to_excel(writer, sheet_name = "MMS136", index = False)
        review.to_excel(writer, sheet_name = "REVIEW", index = False)
        tab.to_excel(writer, sheet_name = "ALL", index = False)
        writer.close()

    # function to run
    def mduify(self):
        LOGGER.info(f"Opening concatenated file.")
        tab = pandas.read_csv(self.input)
        self.make_spreadsheet(tab, self.runid)