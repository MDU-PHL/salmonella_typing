#!/usr/bin/env nextflow
nextflow.preview.dsl=2
version = '1.0'

params.prefix = 'VERIFICATION'
params.path = ""
params.outdir = "."    
params.publish_dir_mode = 'copy'
params.filter = false
params.mms136 = true
if( params.filter ){
distribute_table = file("distribute_table.txt")
    if (distribute_table.exists()){
        distribution_reader =   distribute_table.newReader()
        // read the file
        distribution_reader.eachLine { line ->
            if( line.split('\t')[0] != 'MDUID') {
                job_types[line.split('\t')[0]] = line.split('\t')[3]
                species_exp[line.split('\t')[0]] = line.split('\t')[1]
                }
            }
        }
    contigs = Channel.fromPath(params.path + "*/contigs.fa")
                    .map { files -> tuple([id:files.parent.name, species_exp: species_exp[files.parent.name]], files)}
} else {
    contigs = Channel.fromPath(params.path + "*/contigs.fa")
                    .map { files -> tuple([id:files.parent.name], files)}
}
                                                 
// println contigs.view()
// include salmonella typing module
workflow {
include { SISTR; COLLATE_SISTR; FILTER_SISTR } from './modules/salmonella_typing/main' addParams( options: [args:"mdu" ,args2: 8] )

// // run sistr
    SISTR( contigs )
// collate sistr if filtering there must be a column that
    if( params.filter ){
                            COLLATE_SISTR( SISTR.out.sistr
                                                            .filter { cfg, sis -> cfg.species_exp =~ 'Salmonella' }
                                                            .map { cfg, sis -> sis}
                                                            .collect() )
                                    } else {
                                        COLLATE_SISTR( SISTR.out.sistr
                                                            .map { cfg, sis -> sis}
                                                            .collect() )
                                    }
    if( params.mms136 ){
        FILTER_SISTR( COLLATE_SISTR.out.sistr_collated )
    }
}