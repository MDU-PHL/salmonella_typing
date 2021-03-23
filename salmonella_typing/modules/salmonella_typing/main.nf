// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

module_dir = moduleDir + "/bin"
// println moduleDir
// println module_dir
params.options = [:]
def options    = initOptions(params.options)

process SISTR {
    tag "$meta.id"
    label 'process_medium'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:meta.id, publish_id:meta.id) }
    
       
    // conda (params.enable_conda ? 'bioconda::sistr_cmd=1.0.2' : null)
    // if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
    //     container 'https://depot.galaxyproject.org/singularity/fastp:0.20.1--h8b12597_0'
    // } else {
    //     container 'quay.io/biocontainers/fastp:0.20.1--h8b12597_0'
    // }

    input:
    tuple val(meta), path(contigs)

    output:
    tuple val(meta), path('sistr.csv'), emit: sistr
    path '*.version.txt'                  , emit: version

    script:
    // Added soft-links to original fastqs for consistent naming in MultiQC
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
    // tag "$meta.id"
    label 'process_medium'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:params.outdir, publish_id:'sistr_collate') }
    
       
    // conda (params.enable_conda ? 'bioconda::sistr_cmd=1.1.1' : null)
    // if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
    //     container 'https://depot.galaxyproject.org/singularity/fastp:0.20.1--h8b12597_0'
    // } else {
    //     container 'quay.io/biocontainers/fastp:0.20.1--h8b12597_0'
    // }

    input:
    val(sistr_files) 

    output:
    path 'sistr.csv', emit: sistr_collated
    // path '*.version.txt'                  , emit: version

    script:
    
    """
    ${module_dir}/collate_sistr.py $sistr_files
    """
    
}

process FILTER_SISTR {
     // tag "$meta.id"
    label 'process_medium'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:params.outdir, publish_id:'sistr_filtered') }
    
       
    // conda (params.enable_conda ? 'bioconda::sistr_cmd=1.1.1' : null)
    // if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
    //     container 'https://depot.galaxyproject.org/singularity/fastp:0.20.1--h8b12597_0'
    // } else {
    //     container 'quay.io/biocontainers/fastp:0.20.1--h8b12597_0'
    // }

    input:
    path 'sistr.csv' 

    output:
    path "${params.prefix}_sistr.xlsx", emit: sistr_filtered
    // path '*.version.txt'                  , emit: version

    script:
    
    """
    ${module_dir}/mms136.py sistr.csv $params.prefix
    """
    
}

