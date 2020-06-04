Bootstrap: docker
From: continuumio/miniconda3:4.6.14

%help
A Singularity image for sistr

%labels
Maintainer Anders Goncalves da Silva
Build 1.0
sistr

%environment
export SISTR_VERSION=1.0.2
export PYTHONNOUSERSITE=NO
export PYTHONPATH=/opt/salmonella_typing
export PATH=/opt/conda/bin:/opt/salmonella_typing:$PATH

%setup
  PY_VERSION=3.7
  SISTR_VERSION=1.0.2
  cp -R salmonella_typing $SINGULARITY_ROOTFS/opt/salmonella_typing

%files
sistrdb.tar.gz

%post
 # set versions of software to install
  SISTR_VERSION=1.0.2
  SISTR_BUILD=py37_3

  SNAKEMAKE_VERSION=5.9.1

  apt-get update && apt-get install --yes subversion

  export PATH=/opt/conda/bin:/opt/salmonella_typing:$PATH
  export PYTHONNOUSERSITE=NO
  export PYTHONPATH=/opt/salmonella_typing

  conda config --add channels conda-forge
  conda config --add channels defaults
  conda config --add channels r
  conda config --add channels bioconda

  conda install sistr_cmd=1.0.2 cleo=0.6.8 pandas=0.24.2 xlsxwriter=1.2.8 tabulate=0.8.7 sh=1.12.14 pytest=4.6.3 jinja2=2.11.1 snakemake-minimal=${SNAKEMAKE_VERSION}

  # conda install sistr_cmd=${SISTR_VERSION}=${SISTR_BUILD}
  # conda install datrie=0.7.1=py37h7b6447c_1

  # pip install -U pip
  # pip install -U setuptools
  # pip install cleo==0.6.8
  # pip install pandas
  # pip install XlsxWriter
  # pip install sh
  # pip install tabulate
  # pip install pytest
  # pip install jinja2
  # pip install snakemake==${SNAKEMAKE_VERSION}

  # installs to enable full LOD
  # conda install spades==3.12.0
  # conda install skesa==2.2
  # conda install shovill==1.0.1
  # conda install seqkit==0.9.0
  # conda install mash==2.0
 
 cd / && tar xvzf sistrdb.tar.gz && rm sistrdb.tar.gz

  echo "Sorting some env variables..."
  echo "export DB_UPDATE=\"All DBs updated on $(stat -c %y /opt/sistr_db/sistr.msh)\"" >> $SINGULARITY_ENVIRONMENT
  chmod 755 /opt/salmonella_typing/stype_cli.py

  echo "Done"

%runscript
  echo "Welcome to MDU SALMONELLA TYPING WORKFLOW" >&2
  echo "Running sistr version $VERSION" >&2
  echo $DB_UPDATE >&2
  exec stype_cli.py "$@"

%test
  export PYTHONNOUSERSITE=NO
  export PYTHONPATH=/opt/salmonella_typing
  export PATH=/opt/conda/bin:/opt/salmonella_typing:$PATH

  echo "Testing sistr"
  stype_cli.py test -vvv

