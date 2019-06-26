Bootstrap: docker
From: continuumio/miniconda3:4.6.14

%help
A Singularity image for sistr

%labels
Maintainer Anders Goncalves da Silva
Build 1.0
sistr

%environment
VERSION=1.0.2
PYTHON_EGG_CACHE=/opt/salmonella_typing/.python_egg_cache
PYTHONNOUSERSITE=NO
PYTHONPATH=/opt/salmonella_typing
PATH=/opt/conda/bin:/opt/salmonella_typing:$PATH
export VERSION
export PYTHON_EGG_CACHE
export PYTHONNOUSERSITE
export PYTHONPATH
export PATH=/opt/conda/bin:/opt/salmonella_typing:$PATH

%setup
  cp -R salmonella_typing $SINGULARITY_ROOTFS/opt/salmonella_typing
  cp -R data $SINGULARITY_ROOTFS/opt/salmonella_typing/data
  mkdir -p $SINGULARITY_ROOTFS/opt/salmonella_typing/.python_egg_cache/sistr_cmd-1.0.2-py3.6.egg-tmp/sistr/data
  cp -R data/* $SINGULARITY_ROOTFS/opt/salmonella_typing/.python_egg_cache/sistr_cmd-1.0.2-py3.6.egg-tmp/sistr/data

%post
 # set versions of software to install
  VERSION=1.0.2

  apt-get update && apt-get install --yes subversion

  export PATH=/opt/conda/bin:/opt/salmonella_typing:$PATH
  export PYTHON_EGG_CACHE=/opt/salmonella_typing/.python_egg_cache
  export PYTHONNOUSERSITE=NO
  export PYTHONPATH=/opt/salmonella_typing

  conda config --add channels conda-forge
  conda config --add channels defaults
  conda config --add channels r
  conda config --add channels bioconda

  conda install sistr_cmd=$VERSION
  conda install snakemake
  conda install pip

  pip install -U pip
  pip install -U setuptools
  pip install cleo
  pip install pandas
  pip install XlsxWriter
  pip install sh
  pip install tabulate
  pip install pytest

  # installs to enable full LOD
  # conda install spades==3.12.0
  # conda install skesa==2.2
  # conda install shovill==1.0.1
  # conda install seqkit==0.9.0
  # conda install mash==2.0
 
 svn export https://github.com/phac-nml/sistr_cmd.git/branches/sistr_cmd_update_2018/sistr/data /opt/sistr_db 

  echo "Sorting some env variables..."
  echo "export DB_UPDATE=\"All DBs updated on $(stat -c %y /opt/sistr_db/sistr.msh)\"" >> $SINGULARITY_ENVIRONMENT
  chmod 755 /opt/salmonella_typing/stype_cli.py
  
  sistr /opt/salmonella_typing/data/SentericaLT2.fasta

  echo "Done"

%runscript
  echo "Welcome to MDU SALMONELLA TYPING WORKFLOW" >&2
  echo "Running sistr version $VERSION" >&2
  cat /etc/dbupdate >&2
  exec stype_cli.py "$@"

%test
  echo "Testing sistr"
  PATH=/opt/conda/bin:/opt/salmonella_typing:$PATH
  PYTHON_EGG_CACHE=/opt/salmonella_typing/.python_egg_cache
  PYTHONNOUSERSITE=NO
  PYTHONPATH=/opt/salmonella_typing
  sistr /opt/salmonella_typing/data/SentericaLT2.fasta

