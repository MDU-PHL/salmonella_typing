FROM continuumio/miniconda3:4.5.4 as build

# export SISTR_VERSION=1.0.2
# export PYTHONNOUSERSITE=NO
# export PYTHONPATH=/opt/salmonella_typing
# export PATH=/opt/conda/bin:/opt/salmonella_typing:$PATH

ARG SISTR_BUILD=py37_3
ARG SNAKEMAKE_VERSION=5.5.1
ARG VERSION=1.0.2

RUN apt-get update && apt-get install --yes subversion
RUN conda update conda
RUN conda config --add channels conda-forge
RUN conda config --add channels defaults
RUN conda config --add channels r
RUN conda config --add channels bioconda
# RUN conda install sistr_cmd=1.0.2 cleo=0.6.8 pandas=0.24.2 xlsxwriter=1.2.8 tabulate=0.8.7 sh=1.12.14 pytest=4.6.3 jinja2=2.11.1 snakemake-minimal=${SNAKEMAKE_VERSION} 


RUN conda install sistr_cmd=${VERSION}
RUN conda install snakemake-minimal=${SNAKEMAKE_VERSION}
RUN conda install pip=19.1.1

RUN pip install -U pip
RUN pip install -U setuptools
RUN pip install cleo==0.6.8
RUN pip install pandas==0.24.2
RUN pip install XlsxWriter==1.1.8
RUN pip install jinja2==2.10.1
RUN pip install sh
COPY . /opt/
RUN ls /opt/salmonella_typing
RUN echo "Sorting some env variables..."
RUN echo "All DBs updated on $(date "+%Y-%m-%d")" > /etc/dbupdate
RUN chmod 555 /etc/dbupdate
RUN sistr /opt/salmonella_typing/data/SentericaLT2.fasta
RUN echo "Done"
RUN ls /opt/salmonella_typing/ -lathr

ENV PATH=/opt/conda/bin:/opt/salmonella_typing:$PATH
ENV PYTHONNOUSERSITE=NO
ENV PYTHONPATH=/opt/salmonella_typing

RUN chmod 755 /opt/salmonella_typing/stype_cli.py
RUN stype_cli.py -h
RUN chmod 555 /etc/dbupdate
# RUN sistr /opt/salmonella_typing/data/SentericaLT2.fasta
# CMD [ "echo Welcome to MDU SALMONELLA TYPING WORKFLOW \nRunning sistr version $SISTR_VERSION\n $DB_UPDATE  >&2"]
RUN pip list |wc -l
ENTRYPOINT [ "stype_cli.py" ] 

CMD ["$@"]
