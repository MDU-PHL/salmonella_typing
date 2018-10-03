Bootstrap: docker
From: continuumio/miniconda3:4.5.4

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
  chmod -R 0444 $SINGULARITY_ROOTFS/opt/salmonella_typing
  chmod 0555 $SINGULARITY_ROOTFS/opt/salmonella_typing/scripts/*
  chmod 0555 $SINGULARITY_ROOTFS/opt/salmonella_typing/stype_cli.py
  find $SINGULARITY_ROOTFS/opt/salmonella_typing -type d -exec chmod 0555 {} \;

%post
 # set versions of software to install
  VERSION=1.0.2

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

  # installs to enable full LOD
  conda install spades==3.12.0
  conda install skeka==2.2
  conda install shovill==1.0.1
  conda install seqkit==0.9.0
  conda install mash==2.0
 
  echo "Sorting some env variables..."
  echo "All DBs updated on $(date "+%Y-%m-%d")" > /etc/dbupdate
  chmod 555 /etc/dbupdate

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

