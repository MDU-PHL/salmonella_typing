# _In silico_ _Salmonella enterica_ Serotyping

## Scope

The scripts presented in this repository are to be used to perform _in silico_ serotyping of _Salmonella enterica_ in accordance with MMS136. It takes as input a draft assembly and outputs a serotype inference. The draft assembly is obtained by performing a _de novo_ assembly on FASTQ data found to have passed MMS103 and to be identified as _Salmonella enterica_ by _kmer ID_ and by a wet laboratory method.

## Glossary

- Serotype: A form of classification of bacteria below the species level. Usually involves some sort of reactive between specific sera and antigens on the bacteria's wall.
- Serovar: In this case, a synonym of serotype.
- Serogroup: A group of serovars with common antigens.
- WGS: whole-genome sequence data. Usually, DNA sequence data comprised of short reads (between 35 and 300 bp in length) coded in the FASTQ format.

## A quick primer on _Salmonella_ serotypes

`sistr` will only call serotypes that are valid under the WHO Collaborating Centre for Reference and Research on _Salmonella_ table of antigenic formulas for _Salmonella_ serovars, which can be found [here](https://www.pasteur.fr/sites/default/files/veng_0.pdf). The table follows the _Kauffmann-White-Le Minor_ scheme (which is the _Kauffmann-White_ scheme, but for historical reasons the WHOCC-Salm added _Le Minor_'s name to the scheme's name). According to the document, about 30 serovars are expected to account for about 90% of the _Salmonella_ in a country. The scheme, as presented in the document, describes a total of 2,579 serovars of _Salmonella_, of which 2 557 are of the species _S. enterica_ and 22 are of the species _S. bongori_ (data on pg. 13).

The genus _Salmonella_ is now known to have two species: _S. enterica_ and _S. bongori_. The species _S. enterica_ has six subspecies: _enterica_, _salamae_, _arizonae_, _diarizonae_, _houtenae_, and _indica_. By far the most commonly found in human cases of Salmonellosis is _S. enterica_ subsp _enterica_.

Originally, the subspecies were believed to be subgenera named with roman numerals: I (now _S. enterica_ subsp _enterica_), II (_S. enterica_ subsp _salamae_), III (former genus _Arizona_: subdivided in to IIIa _S. enterica_ subsp _arizonae_ and IIIb _S. enterica_ subsp _diarizonae_), IV (_S. enterica_ subsp _houtenae_), V (_S. bongori_), and VI (_S. enterica_ subsp _indica_).

In the case of serotypes of _Salmonella enterica_ subsp. _enterica_ the serotype is typically reported by a single name (e.g., Enteritidis, Typhi, Typhimurium). This is kept for historical reasons. Serotypes of all other subspecies of _S. enterica_ and _S. bongori_ are typically reported with the antigenic formula.

## SISTR

To perform _Salmonella enterica_ serotyping we use the tool `sistr` [[1](#yoshida)] developed by Public Health Agency of Canada and held [here](https://github.com/peterk87/sistr_cmd). The tool has been extensively validated by others [[2](#yachison)].

`sistr` uses a combination of approaches to infer serotype from draft assemblies of WGS data. For the purposes of MDU work, we have validated the use of the combination of _antigen_ detection and _cgMLST_ typing:

1. It uses _BLAST_ to identify the presence of annotated O- and H- antigen sequences. As such, it comes with curated multiFASTA files for the _fliC_, _fliB_, and _wzx_ and _wzy_ genes.
2. It has a cgMLST scheme with 330 loci, and a database of 52 790 genomes (mostly comprising subspecies I) that have been typed at these loci and annotated with a serotype. It uses _BLAST_ to genotype the input assembly across as many of the 330 loci, and then calculates the pairwise distance of the input isolate to the database of curated genomes.

## References

[<a name='yoshida'>1</a>] Yoshida, C. E., Kruczkiewicz, P., Laing, C. R., Lingohr, E. J., Gannon, V. P. J., Nash, J. H. E., & Taboada, E. N. (2016). The Salmonella _In Silico_ Typing Resource (SISTR): An Open Web-Accessible Tool for Rapidly Typing and Subtyping Draft Salmonella Genome Assemblies. PloS One, 11(1), e0147101.

[<a name="yachison">2</a>] Yachison, C. A., Yoshida, C., Robertson, J., Nash, J. H. E., Kruczkiewicz, P., Taboada, E. N., … Nadon, C. (2017). The Validation and Implications of Using Whole Genome Sequencing as a Replacement for Traditional Serotyping for a National Salmonella Reference Laboratory. Frontiers in Microbiology, 8, 1044.
