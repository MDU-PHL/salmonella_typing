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
export VERSION

%files
mkdir -p /opt/salmonella_typing
cp -R salmonella_typing /opt/salmonella_typing

%post
 # set versions of software to install
  VERSION=1.0.2

  export PATH=/opt/conda/bin:$PATH

  conda config --add channels conda-forge
  conda config --add channels defaults
  conda config --add channels r
  conda config --add channels bioconda

  conda install sistr_cmd=$VERSION
  conda install snakemake

  pip3 install cleo
  pip3 install pandas
 
  echo "Sorting some env variables..."
  echo "All DBs updated on $(date "+%Y-%m-%d")" > /etc/dbupdate
  sudo chmod 555 /etc/dbupdate
  
  echo "Done"

%runscript
  echo "Welcome to sistr $VERSION" >&2
  cat /etc/dbupdate >&2
  exec sistr "$@"

%test
  echo "Testing sistr"

