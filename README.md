# _In silico_ _Salmonella enterica_ Serotyping

## Scope

The scripts presented in this repository are to be used to perform _in silico_ serotyping of _Salmonella enterica_ in accordance with MMS136. It takes as input a draft assembly and outputs a serotype inference. The draft assembly is obtained by performing a _de novo_ assembly on FASTQ data found to have passed MMS103 and to be identified as _Salmonella enterica_ by _kmer ID_ and by a wet laboratory method.

## Glossary

- Serotype: A form of classification of bacteria below the species level. Usually involves some sort of reactive between specific sera and antigens on the bacteria's wall.
- Serovar: In this case, a synonym of serotype.
- Serogroup: A group of serovars with common antigens.
- WGS: whole-genome sequence data. Usually, DNA sequence data comprised of short reads (between 35 and 300 bp in length) coded in the FASTQ format.

## A quick primer on _Salmonella_ serotypes

`sistr` will only call serotypes that are valid under the WHO Collaborating Centre for Reference and Research on _Salmonella_ table of antigenic formulas for _Salmonella_ serovars, which can be found [here](https://www.pasteur.fr/sites/default/files/veng_0.pdf). The table follows the _Kauffmann-White-Le Minor_ scheme (which is the _Kauffmann-White_ scheme, but for historical reasons the WHOCC-Salm added _Le Minor_'s name to the scheme's name). According to the document, about 30 serovars are expected to account for about 90% of the _Salmonella_ in a country. The scheme, as presented in the document, describes a total of 2,579 serovars of _Salmonella_, of which 2,557 are of the species _S. enterica_ and 22 are of the species _S. bongori_ (data on pg. 13).

The genus _Salmonella_ is now known to have two species: _S. enterica_ and _S. bongori_. The species _S. enterica_ has six subspecies: _enterica_, _salamae_, _arizonae_, _diarizonae_, _houtenae_, and _indica_. By far the most commonly found in human cases of Salmonellosis is _S. enterica_ subsp _enterica_.

Originally, the subspecies were believed to be subgenera named with roman numerals: I (now _S. enterica_ subsp _enterica_), II (_S. enterica_ subsp _salamae_), III (former genus _Arizona_: subdivided in to IIIa _S. enterica_ subsp _arizonae_ and IIIb _S. enterica_ subsp _diarizonae_), IV (_S. enterica_ subsp _houtenae_), V (_S. bongori_), and VI (_S. enterica_ subsp _indica_).

In the case of serotypes of _Salmonella enterica_ subsp. _enterica_ the serotype is typically reported by a single name (e.g., Enteritidis, Typhi, Typhimurium). This is kept for historical reasons. Serotypes of all other subspecies of _S. enterica_ and _S. bongori_ are typically reported with the antigenic formula.

## SISTR

To perform _Salmonella enterica_ serotyping we use the tool `sistr` [[1](#yoshida)] developed by Public Health Agency of Canada and held [here](https://github.com/peterk87/sistr_cmd). The tool has been extensively validated by others [[2](#yachison)].

`sistr` uses a combination of approaches to infer serotype from draft assemblies of WGS data. For the purposes of MDU work, we have validated the use of the combination of _antigen_ detection and _cgMLST_ typing:

1. It uses _BLAST_ to identify the presence of annotated O- and H- antigen sequences. As such, it comes with curated multiFASTA files for the _fliC_, _fliB_, and _wzx_ and _wzy_ genes.
2. It has a cgMLST scheme with 330 loci, and a database of 52 790 genomes (mostly comprising subspecies I) that have been typed at these loci and annotated with a serotype. It uses _BLAST_ to genotype the input assembly across as many of the 330 loci, and then calculates the pairwise distance of the input isolate to the database of curated genomes.

## Running salmonella_serotyping

```
stype run --help
usage: stype run [-h] [--contigs CONTIGS] [--prefix PREFIX] [--jobs JOBS]

optional arguments:
  -h, --help            show this help message and exit
  --contigs CONTIGS, -c CONTIGS
                        Tab-delimited file with sample ID as column 1 and path to assemblies as column 2 OR path to a contig file (used if only doing a single sample - should provide value for -pfx). (default: )
  --prefix PREFIX, -px PREFIX
                        If running on a single sample, please provide a prefix for output directory (default: abritamr)
  --jobs JOBS, -j JOBS  Number of AMR finder jobs to run in parallel. (default: 16)
```

Salmonella_typing can be on a single sample run by

```
stype -c <path_to_contigs> -px <name_of_sample>
```

Or in batch mode

```
stype -c input.tab -j 16
```

Where `input.tab` is a tab-delimited file with column 1 being sample ID and column 2 is path to the assemblies.

### MDU Service

```
usage: stype mdu [-h] [--runid RUNID] [--sistr SISTR]

optional arguments:
  -h, --help            show this help message and exit
  --runid RUNID, -r RUNID
                        MDU RunID (default: Run ID)
  --sistr SISTR, -s SISTR
                        Path to concatentated output of sistr (default: sistr_concatenated.csv)
```

In order to generate a LIMS friendly spreadsheet, collate all `stype` results

```
csvtk concat sample_1/sistr_filtered.csv sample_2/sistr_filtered.csv ... > sistr_concatenated.csv
```

Then run `stype` in `mdu` mode

```
stype mdu -r RUNID -s sistr_concatenated.csv
```

## Output 

| File | Contents |
| :---: |:---:|
| `sample_directory/sistr.csv` | raw output of `sistr` |
| `sample_directory/sistr_filtered.csv` | `sistr` output that has been filtered based on MDU business logic per sample |
| `sistr_filtered.csv` | `sistr` output that has been collated and filtered based on MDU business logic for batch |
| `<RUNID>_sistr.xlsx` | a spreadsheet ready for upload into MDU LIMS only output if `mdu` used |

## References

[<a name='yoshida'>1</a>] Yoshida, C. E., Kruczkiewicz, P., Laing, C. R., Lingohr, E. J., Gannon, V. P. J., Nash, J. H. E., & Taboada, E. N. (2016). The Salmonella _In Silico_ Typing Resource (SISTR): An Open Web-Accessible Tool for Rapidly Typing and Subtyping Draft Salmonella Genome Assemblies. PloS One, 11(1), e0147101.

[<a name="yachison">2</a>] Yachison, C. A., Yoshida, C., Robertson, J., Nash, J. H. E., Kruczkiewicz, P., Taboada, E. N., … Nadon, C. (2017). The Validation and Implications of Using Whole Genome Sequencing as a Replacement for Traditional Serotyping for a National Salmonella Reference Laboratory. Frontiers in Microbiology, 8, 1044.
