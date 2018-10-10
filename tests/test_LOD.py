'''
Testing LOD
'''

import pathlib
import tempfile
import itertools
import shutil
import os
import pytest
import tabulate
import pandas as pd
from cleo import Application, CommandTester
from cleo.exceptions.exception import UsageException
from salmonella_typing.validation.limitOfDetection.LODExperimentWorkflow import LODCommand

TEST_DIR=os.getenv("TEST_LOD_DIR")
TEST_CLEAN_DIR=os.getenv('TEST_LOD_DIR_CLEAN', True)

@pytest.fixture(scope="class")
def input_test_file(tmpdir_factory, request):
    datapath = pathlib.Path(__file__).parent
    workdir = tempfile.TemporaryDirectory(dir=TEST_DIR)
    workpath = pathlib.Path(workdir.name)
    testfile = workpath.joinpath('test_input_lod.csv')
    datadir = workpath.joinpath("data")
    ids = ["SRR7284860","SRR7284877"]
    reads = ['R1', 'R2']
    df = {'ID': ids,
         'R1': [],
         'R2': []}
    for i,r in itertools.product(ids, reads):
        tmp = datadir.joinpath(i, f"{r}.fastq.gz")
        tmp.parent.mkdir(exist_ok=True, parents=True)
        shutil.copyfile(datapath / i / f"{i}_{r}.fastq.gz", tmp)
        df[r].append(tmp)
    tab = pd.DataFrame(df)
    tab.to_csv(testfile, index=False)
    assert testfile.exists()
    request.cls.infile = str(testfile)
    request.cls.wd = str(workpath)
    yield
    if TEST_CLEAN_DIR:
        print("Cleaning up...")
        workdir.cleanup()

def pytest_generate_tests(metafunc):
    # called once per each test function
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(argnames, [[funcargs[name] for name in argnames]
            for funcargs in funcarglist])

@pytest.mark.usefixtures('input_test_file')
class TestLODCommand(object):
    params = {
        'test_basic': [dict(params=[
         ('command', 'lod_generator'),
         ('--depth', '10,20')]
        )],
        'test_depth_none': [dict(params=[
         ('command', 'lod_generator')]
        )]  
    }

    def _gen_cmd(self, params):
        app = Application()
        app.add(LODCommand())
        command = app.find("lod_generator")
        runner = CommandTester(command)
        runner.execute(params)
        print(runner.get_display())
        return command

    def test_basic(self, params):
        '''
        Basic test of functionality
        '''
        params.append(('input_file', self.infile))
        params.append(('--workdir', self.wd))
        lod_command = self._gen_cmd(params)
        wd = pathlib.Path(self.wd)
        assert lod_command.infile.name == 'test_input_lod.csv'
        assert lod_command.reps == [1,2]
        assert lod_command.depth == ['10','20']
        assert lod_command.threads == 2
        assert lod_command.seed == 42
        assert lod_command.min_seed == 10
        assert lod_command.max_seed == 10**8
        assert lod_command.tab.ID.tolist() == ['id1', 'id2']
        print(tabulate.tabulate(lod_command.tab_lod, headers='keys', tablefmt='md'))
        assert wd.joinpath("lod_experiment_input.csv").exists()
        assert wd.joinpath("Snakefile").exists()
        assert wd.joinpath('config.yaml').exists()

    
    def test_depth_none(self, params):
        params.append(('input_file', self.infile))
        with pytest.raises(UsageException, message="Expecting UsageException"):
            self._gen_cmd(params)


