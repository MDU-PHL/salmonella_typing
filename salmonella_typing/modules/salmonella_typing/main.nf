// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

module_dir = moduleDir + "/bin"

params.options = [:]
def options    = initOptions(params.options)

process SISTR {
    tag "$meta.id"
    label 'process_medium'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:meta.id, publish_id:meta.id) }
    cache 'lenient' 
    
    input:
    tuple val(meta), path(contigs)

    output:
    tuple val(meta), path('sistr.csv'), emit: sistr
    path '*.version.txt'                  , emit: version

    script:
    
    def software = getSoftwareName(task.process)
    def prefix   = options.suffix ? "${meta.id}${options.suffix}" : "${meta.id}"
    """
    tmp_dir=\$(mktemp -d -t sistr-XXXXXXXXXX)
    sistr -i contigs.fa ${prefix} -f csv -o sistr.csv --tmp-dir \$tmp_dir -m 
    echo \$(sistr --version 2>&1) | sed -e "s/sistr //g" > ${software}.version.txt
    rm -rf \$tmp_dir
    """
    
}


// common process to collate the sistr output
process COLLATE_SISTR {
    
    label 'process_medium'
    publishDir ".",
        mode: params.publish_dir_mode
        
    cache 'lenient'
    input:
    val(sistr_files) 

    output:
    path 'sistr.csv', emit: sistr_collated
    
    script:
    
    """
    ${module_dir}/collate_sistr.py $sistr_files
    """
    
}

process FILTER_SISTR {
    
    label 'process_medium'
    publishDir ".",
        mode: params.publish_dir_mode
        
    cache 'lenient'
    input:
    path 'sistr.csv' 

    output:
    path("${params.prefix}_filtered.csv"), emit: sistr_filtered
    path("${params.prefix}_sistr.xlsx") optional true
    

    script:
    
    """
    ${module_dir}/parse.py sistr.csv $params.prefix $params.mms136
    """
    
}

