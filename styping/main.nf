#!/usr/bin/env nextflow
nextflow.preview.dsl=2
version = '1.0'


// set default value for the contigs channel
contigs = Channel.fromPath(params.path + "/*/contigs.fa")
                    .map { files -> tuple([id:files.parent.name], files)}
// Hopefully you have a good reason to be doing this outside of a run folder
if( params.qc ){
    def job_types = [:]
    def species_exp = [:]
    distribute_table = file("distribute_table.txt")
        if (distribute_table.exists()){
            println 'Accessing distribute_table.txt'
            distribution_reader =   distribute_table.newReader()
            // read the file
            distribution_reader.eachLine { line ->
                if( line.split('\t')[0] != 'MDUID') {
                    // job_types[line.split('\t')[0]] = line.split('\t')[3]
                    species_exp[line.split('\t')[0]] = line.split('\t')[1]
                    }
                }
            contigs = Channel.fromPath(params.path + "*/contigs.fa")
                        .map { files -> tuple([id:files.parent.name, species_exp: species_exp[files.parent.name]], files)}
            }
} 
                                                 

// include salmonella typing module
workflow {
include { SISTR; COLLATE_SISTR; FILTER_SISTR } from './modules/salmonella_typing/main' addParams( options: [args:"mdu" ,args2: 8] )

// // run sistr
    SISTR( contigs )
// collate sistr if this is for qc, the distribute table must be present and has been used to generate a map so filtering can occur
    if( params.qc ){
                            COLLATE_SISTR( SISTR.out.sistr
                                                            .filter { cfg, sis -> cfg.species_exp =~ 'Salmonella' }
                                                            .map { cfg, sis -> sis}
                                                            .collect() )
                                    } else {
                                        COLLATE_SISTR( SISTR.out.sistr
                                                            .map { cfg, sis -> sis}
                                                            .collect() )
                                    }
    // filter and apply business logic to the sistr output - if this is for mms136 then a spreadsheet will be produced
    FILTER_SISTR( COLLATE_SISTR.out.sistr_collated )
    
}