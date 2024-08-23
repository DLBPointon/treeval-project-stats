# Major Imports
import os
import sys
import textwrap
import argparse
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import date

# Local Imports
from graphing import *
from parse_run import RunParser
from condense_data import ExecutionCondenser

# Constants
TIME = date.today()
VERSION = "2.1.0"
DESCRIPTION = f"""
    | ---
    | SummaryStats
    | Version: {VERSION}
    | ---
    | A Python3.10 script developed to parse NextflowDSL2 execution data into
    | actionable graphs and statistics.
    | ---
    | By Damon-Lee Pointon (DLBPointon, dp24)
    |
    | ---
    | This script aims to:
    | - Generate efficiency data
    | - Generate graphs evidencing memory and cpu efficiency
    | - Use nf-co2footprint data to, nominatively, add co2 footprint data to your data
    |     and ID your most polluting processes
    |
    | Get flags with:
    | SummaryStats.py -h
    """
base_df = []


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="SummaryStats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(DESCRIPTION),
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Path to directory containing all data files, e.g, /path/to/files/",
    )
    parser.add_argument(
        "-des",
        "--describe_data",
        action="store_true",
        help="Print a CLI report about the data (NOT YET IMPLEMENTED)",
    )
    parser.add_argument(
        "-co2",
        "--co2directory",
        type=str,
        required=False,
        help="Path to directory containing the nf-co2footprint output (NOT YET IMPLEMENTED)",
    )
    parser.add_argument(
        "--graph_savename",
        required=False,
        type=str,
        default="SummaryGraphs",
        help="Save name for the graphs",
    )
    parser.add_argument(
        "-a",
        "--output_halfway",
        type=bool,
        default=False,
        help="Output halfway data for ML",
    )
    parser.add_argument("--debug", type=bool, default=False, help="For debugging!")
    parser.add_argument(
        "-s",
        "--specific-processes",
        type=str,
        default="",
        help='A list of process for a process specific graph (will be more performant to specify! e.g "REPEAT_DENSITY:GNU_SORT_C,OTHER")',
    )
    parser.add_argument(
        "--graphs",
        action="store_true",
        help="Generate graphs for analysis",
    )
    parser.add_argument("-v", "--version", action="version", version=VERSION)
    return parser.parse_args(argv)


def get_data(dir: str):
    all_data = []
    # Check file is empty or not, it's happened...
    for file in os.listdir(dir):
        # pathlib?
        if os.stat(dir + file).st_size == 0:
            # empty_files.append(file)
            pass
        else:
            if args.debug:
                print(file)

            all_data.append(RunParser(f"{dir}{file}"))

    return all_data


def main(args):
    # Check if everything has context data
    # If yes, then inject into the dataframes
    # Else warn user and carry on with only the execution logs
    all_data = get_data(args.directory)

    # Count how much data has the extended context data
    tv_counter = 0
    for i in all_data:
        if "TreeValProject.Summary" in i.data_type:
            tv_counter += 1

    if args.debug:
        print(
            f"""
            TreeVal Context Data count: {tv_counter}
            vs.
            Total number of Data: {len(all_data)}

            """
        )

    specific_processes = args.specific_processes.split(",")

    #
    # If all files contain the context data, then we can perform extra analysis
    #
    if tv_counter == len(all_data):
        print("ALL DATA HAS CONTEXT DATA - means more analysis!")
        tv_data = True
        new_data = [RunParser.inject_context(i) for i in all_data]
        condensed_data = [ExecutionCondenser(i.execution.data_frame) for i in new_data]

        # Prints all datatypes for all dataframes in folder
        # Followed by print of the column headers
        if args.debug:
            # Add a summarising counter per column?
            [
                print(i.condenser(df="avg", extended=tv_data).dtypes)
                for i in condensed_data
            ]
            print(condensed_data[0].execution.data_frame.columns)

        all_total_values_df = pl.concat(
            [i.condenser(df="avg", extended=True) for i in condensed_data]
        )

        unique_names = all_total_values_df.get_column("names").to_list()
        workflow_names = list(set([i.split(":")[0] for i in unique_names]))

        if len(specific_processes) > 0 and args.output_halfway != True:
            graph_keys_against_genome(
                all_total_values_df, workflow_names, specific_processes
            )

        unique_names = all_total_values_df.get_column("names").to_list()
        workflow_names = list(set([i.split(":")[0] for i in unique_names]))
        # graph_per_workflow(total_value_df, workflow_names, "TVC")
        #
        # Super condense allows us to generate the pipeline wide graphs like we do with non-contexted data
        #
        whole_condensed_data = ExecutionCondenser(
            pl.concat([i.execution.data_frame for i in new_data])
        )
        total_value_df = whole_condensed_data.condenser(df="avg", extended=tv_data)

        """     if len(specific_processes) > 0:
        graph_keys_against_genome(
            total_value_df, workflow_names, specific_processes
        ) """

    else:
        print("NONE or MISSING CONTEXT DATA - continuing with MINIMAL analysis")
        tv_data = False
        condensed_data = ExecutionCondenser(
            pl.concat([i.execution.data_frame for i in all_data])
        )
        total_value_df = condensed_data.condenser(df="total")

    if args.output_halfway:
        all_total_values_df.write_csv("ML_data.csv", separator=",")
        sys.exit("Don't need to do anything else!")

    if tv_data:
        regression_args = {
            1: {
                "data": all_total_values_df,
                "all_data": True,
            },
            2: {"data": total_value_df, "all_data": False},
        }
    else:
        regression_args = {3: {"data": total_value_df, "all_data": False}}

    if args.graphs:
        for x, y in regression_args.items():
            print(f"GENERATE LINEAR GRAPHS WITH: {x} -- {y}")
            graph_linear_regressions(y, tv_data)
        
        print(f"GENERATE PROCESS VS PEAK")
        graph_process_vs_peak(total_value_df)

        print(f"GENERATE PROCESS VS PEAK - LOG")
        graph_process_vs_peak_log(total_value_df)

        print(f"GENERATE GRAPH PER WORKFLOW")
        graph_per_workflow(total_value_df, workflow_names, "./")
        
        print(f"GENERATE PEAK VS CLADE")
        graph_peak_vs_clade(total_value_df)
        
        print(f"GENERATE PROCESS VS CPU")
        graph_cpu_vs_process(total_value_df)


if __name__ == "__main__":
    args = parse_args()
    main(args)
