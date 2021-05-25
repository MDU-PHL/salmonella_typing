import pathlib, argparse, sys, os, logging

from styping.Typing import SetupTyping, RunTyping
# from abritamr.RunFinder import RunFinder
# from abritamr.Collate import Collate, MduCollate
from styping.version import __version__

"""
abritamr is designed to implement AMRFinder and parse the results compatible for MDU use. It may also be used for other purposes where the format of output is compatible

"""

def run_pipeline(args):
    P = SetupTyping(args)
    input_data = P.setup()
    T = RunFinder(input_data)
    sistr_data = T.run()
    # C = Collate(amr_data)
    # collated_data = C.run()
    

# def mdu(args):
#     M = SetupMDU(args)
#     input_data = M.setup()
#     C = MduCollate(input_data)
#     collated_data = C.run()


def set_parsers():
    parser = argparse.ArgumentParser(
        description="Salmonella typing using sistr", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    
    subparsers = parser.add_subparsers(help="Task to perform")
    parser_sub_run = subparsers.add_parser('run', help='Run salmonella typing', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_sub_run.add_argument(
        "--contigs",
        "-c",
        default="",
        help="Tab-delimited file with sample ID as column 1 and path to assemblies as column 2 OR path to a contig file (used if only doing a single sample - should provide value for -pfx). ",
    )
    parser_sub_run.add_argument(
        "--prefix",
        "-px",
        default="abritamr",
        help="If running on a single sample, please provide a prefix for output directory",
    )
    
    parser_sub_run.add_argument(
        "--jobs", "-j", default=16, help="Number of AMR finder jobs to run in parallel."
    )
    
    # parser_mdu = subparsers.add_parser('mdu', help='Finalise abritamr results for MDU service', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # parser_mdu.add_argument(
    #     "--qc",
    #     "-q",
    #     default="",
    #     help="Name of checked MDU QC file."
    # )
    # parser_mdu.add_argument(
    #     "--runid",
    #     "-r",
    #     default=f"Run ID",
    #     help="MDU RunID",
    # )
    # parser_mdu.add_argument(
    #     "--matches",
    #     "-m",
    #     default=f"summary_matches.txt",
    #     help="Path to matches, concatentated output of abritamr",
    # )
    # parser_mdu.add_argument(
    #     "--partials",
    #     "-p",
    #     default=f"summary_partials.txt",
    #     help="Path to partial matches, concatentated output of abritamr",
    # )

    
    
    parser_sub_run.set_defaults(func=run_pipeline)
    parser_mdu.set_defaults(func = mdu)
    args = parser.parse_args()
    return args


def main():
    """
    run pipeline
    """

    args = set_parsers()
    if vars(args) == {}:
        parser.print_help(sys.stderr)
    else:
        args.func(args)
    

if __name__ == "__main__":
    main()
