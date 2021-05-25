import pathlib, pandas, datetime, subprocess, os, logging,subprocess,collections
from styping.version import sistr_version
from styping.CustomLog import CustomFormatter


class SetupTyping(object):
    """
    A class for setting up salmonella typing
    """
    def __init__(self, args):
        

        self.logger =logging.getLogger(__name__) 
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(CustomFormatter())
        fh = logging.FileHandler('styping.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s:%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') 
        fh.setFormatter(formatter)
        self.logger.addHandler(ch) 
        self.logger.addHandler(fh)

        self.jobs = args.jobs 
        self.contigs = args.contigs
        self.prefix = args.prefix

        
    def file_present(self, name):
        """
        check file is present
        :name is the path of the file to check
        """
        
        if name == "":
            return False
        elif pathlib.Path(name).exists():
            self.logger.info(f"Checking if file {name} exists")
            return True
        else:
            return False

        

    def _check_prefix(self):
        """
        If running type is not batch, then check that prefix is present and a string
        """

        if self.prefix == '':
            self.logger.critical(f"You must supply a sample or sequence id.")
            raise SystemExit
        else:
            return True

            
    
    def _get_input_shape(self):
        """
        determine shape of file
        """
        run_type = 'assembly'
        with open(self.contigs, 'r') as c:
            data = c.read().strip().split('\n')
            firstline = data[0]
            if not firstline.startswith('>'):
                for line in data:
                    if len(line.split('\t')) != 2:
                        self.logger.critical("Your input file should either be a tab delimited file with two columns or the path to contigs. Please check your input and try again.")
                        raise SystemExit
                run_type = 'batch'
        self.logger.info(f"The input file seems to be in the correct format. Thank you.")
        return run_type
    

    def _input_files(self):
        """
        Ensure that the files (either contigs or amrfinder output) exist and return running type
        """
        
        running_type = self._get_input_shape()
        if running_type == 'batch':
            self.logger.info(f"Checking that the input data is present.")
            with open(self.contigs, 'r') as c:
                data = c.read().strip().split('\n')
                for line in data:
                    row = line.split('\t')
                    if not self.file_present(row[1]):
                        self.logger.critical(f"{row[1]} is not a valid file path. Please check your input and try again.")
                        raise SystemExit
        elif running_type == 'assembly' and self.file_present(self.contigs):
            self.logger.info(f"{self.contigs} is present. abritamr can proceed.")
        else:
            self.logger.critical(f"Something has gone wrong with your inputs. Please try again.")
            raise SystemExit
        
        return running_type
   

    def setup(self):
        # check that inputs are correct and files are present
        running_type = self._input_files()
        # check that prefix is present (if needed)
        if running_type == 'assembly':
            self._check_prefix()
        Data = collections.namedtuple('Data', ['run_type', 'input', 'prefix', 'jobs'])
        input_data = Data(running_type, self.contigs, self.prefix, self.jobs)
        
        return input_data


class SetupMDU(SetupTyping):
    """
    Setup MDUify of abritamr results
    """
    def __init__(self, args):
        

        self.logger =logging.getLogger(__name__) 
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(CustomFormatter())
        fh = logging.FileHandler('abritamr.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s:%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') 
        fh.setFormatter(formatter)
        self.logger.addHandler(ch) 
        self.logger.addHandler(fh)

        self.runid = args.runid
        self.input = args.sistr
        

    def _check_runid(self):
        if self.runid == '':
            self.logger.critical(f"Run ID can not be empty, please try again.")
            raise SystemExit
        else:
            return True

    def setup(self):
        """
        Check the inputs for MDU - ensure all files are present for collation.
        """
        self._check_runid()

        Data = collections.namedtuple('Data', ['input', 'runid'])

        if self.file_present(self.sistr) and self._check_runid():
            return Data(self.sistr, self.runid)
        else:
            self.logger.critical(f"Something has gone wrong with your inputs. Please try again!")
            raise SystemExit

class RunTyping:
    """
    A base class for setting up abritamr return a valid input object for subsequent steps
    """
    def __init__(self, args):
        # tmp_dir=\$(mktemp -d -t sistr-XXXXXXXXXX)
    # sistr -i contigs.fa ${prefix} -f csv -o sistr.csv --tmp-dir \$tmp_dir -m 

        self.logger =logging.getLogger(__name__) 
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(CustomFormatter())
        fh = logging.FileHandler('styping.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s:%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') 
        fh.setFormatter(formatter)
        self.logger.addHandler(ch) 
        self.logger.addHandler(fh)

        self.run_type = args.run_type
        self.input = args.input
        self.prefix = args.prefix
        self.jobs = args.jobs

    def _batch_cmd(self):
        """
        generate cmd with parallel
        """
        cmd = f"parallel -j {self.jobs} --colsep '\\t' '$(mktemp -d -t sistr-XXXXXXXXXX) && mkdir -p {{1}} && sistr -i {{2}} {{1}} -f csv -o {{1}}/sistr.csv --tmp-dir $tmp_dir -m' :::: {self.input}"

        return cmd
    
    def _single_cmd(self):
        """
        generate a single amrfinder command
        """
        cmd = f"$(mktemp -d -t sistr-XXXXXXXXXX) && mkdir -p {self.prefix} && sistr -i {self.input} {self.prefix} -f csv -o {self.prefix}/sistr.csv --tmp-dir $tmp_dir -m"
        
        return cmd
    
    def _generate_cmd(self):
        """
        Generate a command to run sistr
        """
        cmd = self._batch_cmd() if self.run_type == 'batch' else self._single_cmd()
        return cmd
        
    def _run_cmd(self, cmd):
        """
        Use subprocess to run the command for sisrs
        """

        p = subprocess.run(cmd, shell = True, capture_output = True, encoding = "utf-8")
        if p.returncode == 0:
            self.logger.info(f"sistr completed successfully. Will now move on to collation.")
            return True
        else:
            self.logger.critical(f"There appears to have been a problem with running sistr. The following error has been reported : \n {p.stderr}")

    def _check_output_file(self, path):
        """
        check that sistr outputs are present
        """
        if not pathlib.Path(path).exists():
            self.logger.critical(f"The sistr output : {path} is missing. Something has gone wrong with sistr. Please check all inputs and try again.")
            raise SystemExit
        else:
            return True

    def _check_outputs(self):
        """
        use inputs to check if files made
        """
        if self.run_type != 'batch':
            self._check_output_file(f"{self.prefix}/sistr.csv")
        else:
            tab = pandas.read_csv(self.input, sep = '\t', header = None)
            for row in tab.iterrows():
                self._check_output_file(f"{row[1][0]}/sistr.csv")
        return True

    def run(self):
        """
        run sistr
        """
    
        self.logger.info(f"All check complete now running sistr")
        cmd = self._generate_cmd()
        self.logger.info(f"You are running sistr in {self.run_type} mode. Now executing : {cmd}")
        self._run_cmd(cmd)
        self._check_outputs()

        Data = collections.namedtuple('Data', ['run_type', 'input', 'prefix'])
        sistr_data = Data(self.run_type, self.input, self.prefix)

        return sistr_data

