import os
import click
import argparse
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import date

from graphing import (
    graph_cpu_vs_process,
    graph_process_vs_peak,
    graph_process_vs_peak_log,
    graph_peak_vs_clade,
    graph_per_workflow,
    graph_keys_against_genome,
)
from parse_run import RunParser
from condense_data import ExecutionCondenser

TIME = date.today()
FOLDER = (
    "/home/runner/work/SummaryStats/SummaryStats/treeval-summary-files/1-1-0-runs-5/"
)
# FOLDER = "/nfs/treeoflife-01/teams/tola/users/dp24/SummaryStats/treeval-summary-files/readmapping modified/"

base_df = []


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="SummaryStats",
        description="""\
                    SummaryStats:
        A script for parsing nextflow execution logs
        into efficiency focused graphs.

        Works even better with TreeValProject.Summary
        context data.
        """,
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Path to directory containing all data files, e.g, /path/to/files/",
    )
    parser.add_argument(
        "-co2",
        "--co2directory",
        type=str,
        required=False,
        help="Path to directory containing the nf-co2footprint output",
    )
    parser.add_argument(
        "--graph_savename",
        required=False,
        type=str,
        default="SummaryGraphs",
        help="Do you want to name your graphs yourself?",
    )
    parser.add_argument("--debug", type=bool, default=False, help="For debugging!")
    parser.add_argument(
        "-s",
        "--specific-processes",
        type=list,
        default=[],
        help='A list of process for a process specific graph (will be more performant to specify! e.g ["REPEAT_DENSITY:GNU_SORT_C"])',
    )
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
            all_data.append(RunParser(f"{dir}{file}"))

    return all_data


def main(args):
    # all_data = [ i for i in RunParser( f"{folder}{file}") ]

    # Check if everything has context data
    # If yes, then inject into the dataframes
    # Else warn user and carry on with only the execution logs
    all_data = get_data(args.directory)

    tv_counter = 0
    tv_counter2 = (
        tv_counter + 1 for i in all_data if "TreeValProject.Summary" in i.data_type
    )
    for i in all_data:
        if "TreeValProject.Summary" in i.data_type:
            tv_counter += 1

    if args.debug:
        print(f"do they match? {tv_counter} -- {tv_counter2}")

        print(
            f"""
        TreeVal Context Data count: {tv_counter}
        vs.
        Total number of Data: {len(all_data)}

        """
        )

    if tv_counter == len(all_data):
        print("ALL DATA HAS TreeValPROJECT.SUMMARY CONTEXT DATA")
        print("means you can run more indepth analysis")
        tv_data = True
        new_data = [RunParser.inject_context(i) for i in all_data]
        condensed_data = [
            ExecutionCondenser(
                i.execution.data_frame.with_columns(
                    pl.col("pacbio_total").cast(pl.Int64),
                    pl.col("cram_total").cast(pl.Int64),
                )
            )
            for i in new_data
        ]

        #
        # Condenses per run to be used in other graphs
        # Generating box plots per process, across clades
        #
        for i in condensed_data:
            x = i.condenser(df="avg", extended=True)
            print(x.columns)
            print(x.dtypes)
        total_value_df = pl.concat(
            [i.condenser(df="avg", extended=True) for i in condensed_data]
        )
        unique_names = total_value_df.get_column("names").to_list()
        workflow_names = list(set([i.split(":")[0] for i in unique_names]))
        # graph_per_workflow(total_value_df, workflow_names, "TVC")
        #
        # Super condense allows us to generate the pipeline wide graphs like we do with non-contexted data
        #
        whole_condensed_data = ExecutionCondenser(
            pl.concat([i.execution.data_frame for i in new_data])
        )
        total_value_df = whole_condensed_data.condenser(df="avg", extended=True)

        if len(args.specific_processes) > 0:
            graph_keys_against_genome(
                total_value_df, workflow_names, args.specific_processes
            )

    else:
        print("NONE or NOT ENOUGH CONTEXT DATA - continuing with ALL DATA analysis")
        tv_data = False
        condensed_data = ExecutionCondenser(
            pl.concat([i.execution.data_frame for i in all_data])
        )
        total_value_df = condensed_data.condenser(df="total")

    """ with pl.Config() as cfg:
        cfg.set_tbl_cols(-1)
        print(total_value_df) """

    unique_names = total_value_df.get_column("names").to_list()
    workflow_names = list(set([i.split(":")[0] for i in unique_names]))

    # graph_process_vs_peak(total_value_df)
    # graph_per_workflow(total_value_df, workflow_names)
    # graph_process_vs_peak_log(total_value_df)


if __name__ == "__main__":
    args = parse_args()
    main(args)
