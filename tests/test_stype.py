import sys, pathlib, pandas, pytest, numpy, logging, collections

from unittest.mock import patch, PropertyMock

from styping.Typing import SetupTyping,RunTyping

test_folder = pathlib.Path(__file__).parent

def test_file_present():
    """
    assert true when the input file is true
    """
    with patch.object(SetupTyping, "__init__", lambda x: None):
        stype_obj = SetupTyping()
        stype_obj.logger = logging.getLogger(__name__)
        p = test_folder / "contigs.fa"
    
        assert stype_obj.file_present(p)


def test_check_run_type_batch():
    """
    assert true when a tab file is provided with two columns
    """
    with patch.object(SetupTyping, "__init__", lambda x: None):
        stype_obj = SetupTyping()
        stype_obj.contigs = f"{test_folder / 'batch.txt'}"
        stype_obj.prefix = ''
        stype_obj.logger = logging.getLogger(__name__)
        assert stype_obj._get_input_shape() == 'batch'

def test_check_run_type_single():
    """
    assert true when a contigs file is provided and batch recorded as assembly
    """
    with patch.object(SetupTyping, "__init__", lambda x: None):
        stype_obj = SetupTyping()
        stype_obj.contigs = f"{test_folder / 'contigs.fa'}"
        stype_obj.prefix = 'somename'
        stype_obj.logger = logging.getLogger(__name__)
        assert stype_obj._get_input_shape() == 'assembly'

def test_check_run_type_wrong_data():
    """
    assert true when error raised because input is wrong shape
    """
    with patch.object(SetupTyping, "__init__", lambda x: None):
        stype_obj = SetupTyping()
        stype_obj.contigs = f"{test_folder / 'batch_fail.txt'}"
        stype_obj.prefix = ''
        stype_obj.logger = logging.getLogger(__name__)
        with pytest.raises(SystemExit):
            stype_obj._get_input_shape()

def test_prefix_string():
    """
    assert True when non-empty string is given
    """
    with patch.object(SetupTyping, "__init__", lambda x: None):
        stype_obj = SetupTyping()
        stype_obj.prefix = "some_isolate"
        stype_obj.logger = logging.getLogger(__name__)
        assert stype_obj._check_prefix()

def test_prefix_empty():
    """
    assert True when non-empty string is given
    """
    with patch.object(SetupTyping, "__init__", lambda x: None):
        stype_obj = SetupTyping()
        stype_obj.prefix = ""
        stype_obj.logger = logging.getLogger(__name__)
        with pytest.raises(SystemExit):
            stype_obj._check_prefix()
       

def test_setup_contigs():
    with patch.object(SetupTyping, "__init__", lambda x: None):
        stype_obj = SetupTyping()
        stype_obj.contigs = f"{test_folder / 'contigs.fa'}"
        stype_obj.prefix = 'somename'
        stype_obj.jobs  = 16
        stype_obj.logger = logging.getLogger(__name__)
        T = collections.namedtuple('T', ['run_type', 'input', 'prefix', 'jobs'])
        input_data = T('assembly', stype_obj.contigs, stype_obj.prefix, stype_obj.jobs)
        assert stype_obj.setup() == input_data


def test_setup_fail():
    with patch.object(SetupTyping, "__init__", lambda x: None):
        stype_obj = SetupTyping()
        stype_obj.contigs = f"{test_folder / 'batch.txt'}"
        stype_obj.prefix = ''
        stype_obj.jobs  = 16
        stype_obj.logger = logging.getLogger(__name__)
        T = collections.namedtuple('T', ['run_type', 'input', 'prefix', 'jobs'])
        input_data = T('batch', stype_obj.contigs, stype_obj.prefix, stype_obj.jobs)
        assert stype_obj.setup() == input_data
 
def test_setup_fail():
    with patch.object(SetupTyping, "__init__", lambda x: None):
        stype_obj = SetupTyping()
        stype_obj.contigs = f"{test_folder / 'batch_fail.txt'}"
        stype_obj.prefix = ''
        stype_obj.jobs  = 16
        stype_obj.logger = logging.getLogger(__name__)
        T = collections.namedtuple('T', ['run_type', 'input', 'prefix', 'jobs'])
        input_data = T('batch', stype_obj.contigs, stype_obj.prefix, stype_obj.jobs)
        with pytest.raises(SystemExit):
            stype_obj.setup()


# def test_prefix_empty():
#     """
#     assert True when non-empty string is given
#     """
#     with patch.object(SetupTyping, "__init__", lambda x: None):
#         args = MDU("", 'tests/summary_matches.txt', 'tests/summary_matches.txt', 'tests/mdu_qc_checked.csv')
#         stype_obj = SetupMDU(args)
#         stype_obj.logger = logging.getLogger(__name__)
#         with pytest.raises(SystemExit):
#             stype_obj._check_runid()


# def test_mdu_setup_success():
#     """
#     assert True when non-empty string is given
#     """
#     with patch.object(SetupTyping, "__init__", lambda x: None):
#         args = MDU("RUNID", 'tests/summary_matches.txt', 'tests/summary_matches.txt', 'tests/mdu_qc_checked.csv')
#         stype_obj = SetupMDU(args)
#         Data = collections.namedtuple('Data', ['qc', 'matches', 'partials', 'db', 'runid'])
#         d = Data(args.qc, args.matches, args.partial, stype_obj.db, args.runid)
#         stype_obj.logger = logging.getLogger(__name__)
#         assert stype_obj.setup() == d


# def test_mdu_setup_fail():
#     """
#     assert True when non-empty string is given
#     """
#     with patch.object(SetupTyping, "__init__", lambda x: None):
#         args = MDU("RUNID", 'tests/summarymatches.txt', 'tests/summary_matches.txt', 'tests/mdu_qc_checked.csv')
#         stype_obj = SetupMDU(args)
#         Data = collections.namedtuple('Data', ['qc', 'matches', 'partials', 'db', 'runid'])
#         d = Data(args.qc, args.matches, args.partial, stype_obj.db, args.runid)
#         stype_obj.logger = logging.getLogger(__name__)
#         with pytest.raises(SystemExit):
#             stype_obj.setup()

# test RunTyping

Data = collections.namedtuple('Data', ['run_type', 'input', 'prefix', 'jobs'])
def test_batch_cmd():
    """
    assert True when non-empty string is given
    """
    with patch.object(RunTyping, "__init__", lambda x: None):
        
        args = Data("batch", 'tests/batch.txt', '', 9)
        stype_obj = RunTyping()
        stype_obj.run_type = args.run_type
        stype_obj.prefix = args.prefix
        stype_obj.jobs = args.jobs
        stype_obj.input = args.input
        cmd = f"parallel -j {args.jobs} --colsep '\\t' 'tmp_dir=$(mktemp -d -t sistr-XXXXXXXXXX) && mkdir -p {{1}} && sistr -i {{2}} {{1}} -f csv -o {{1}}/sistr.csv --threads 1 --tmp-dir $tmp_dir -m && rm -r $tmp_dir' :::: {args.input}"
        stype_obj.logger = logging.getLogger(__name__)
        assert stype_obj._batch_cmd() == cmd

def test_single_cmd():
    """
    assert True when non-empty string is given
    """
    with patch.object(RunTyping, "__init__", lambda x: None):
        args = Data("batch", 'tests/contigs.fa', 'somename', 9)
        stype_obj = RunTyping()
        stype_obj.run_type = args.run_type
        stype_obj.prefix = args.prefix
        stype_obj.jobs = args.jobs
        stype_obj.input = args.input
        cmd = f"tmp_dir=$(mktemp -d -t sistr-XXXXXXXXXX) && mkdir -p {args.prefix} && sistr -i {args.input} {args.prefix} -f csv -o {args.prefix}/sistr.csv --threads {self.jobs} --tmp-dir $tmp_dir -m && rm -r $tmp_dir"
        stype_obj.logger = logging.getLogger()
        assert stype_obj._single_cmd() == cmd

