'''
Testing LOD
'''

import pathlib
import pytest
import tabulate
import pandas as pd
from cleo import Application, CommandTester
from cleo.exceptions.exception import UsageException
from salmonella_typing.validation.limitOfDetection.gen_lod_experiment import LODCommand

@pytest.fixture(scope="class")
def input_test_file(tmpdir_factory, request):
    workdir = tmpdir_factory.mktemp("salmoLOD")
    testfile = workdir.join('test_input_lod.csv')
    tab = pd.DataFrame({
        'ID': ['id1', 'id2'],
        'R1': [workdir.join('id1').join('R1.fastq.gz'),
               workdir.join('id2').join('R1.fastq.gz')],
        'R2': [workdir.join('id1').join('R2.fastq.gz'),
               workdir.join('id2').join('R2.fastq.gz')]
    })
    print(tab)
    assert 0
    request.cls.wd = str(workdir)
    yield 

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
        params.append(('input_file', self.wd))
        print(params)
        lod_command = self._gen_cmd(params)
        assert lod_command.infile.name == 'test_input_lod.csv'
        assert lod_command.reps == [1,2]
        assert lod_command.depth == ['10','20']
        assert lod_command.threads == 2
        assert lod_command.seed == 42
        assert lod_command.min_seed == 10
        assert lod_command.max_seed == 10**8
        assert lod_command.tab.ID.tolist() == ['id1', 'id2']
        assert lod_command.tab.R1.tolist() == ['/path/id1/read1_R1.fastq.gz', '/path/id2/read1_R1.fastq.gz']
        assert lod_command.tab.R2.tolist() == ['/path/id1/read2_R2.fastq.gz', '/path/id2/read2_R2.fastq.gz']
        print(tabulate.tabulate(lod_command.tab_lod, headers='keys', tablefmt='md'))
        assert 0

    
    def test_depth_none(self, params):
        params.append(('input_file', self.wd))
        with pytest.raises(UsageException, message="Expecting UsageException"):
            self._gen_cmd(params)


