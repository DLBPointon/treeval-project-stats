import seaborn as sns
import matplotlib.pyplot as plt
import polars as pl
import polars.selectors as cs
import numpy as np


def graph_cpu_vs_process(data_df: pl.DataFrame):
    print("Generating CPU usage vs process", end="\r", flush=True)
    sns.set(rc={"figure.figsize": (25, 25)})
    fig = sns.lineplot(data_df, x="names", y="cpus_requested")
    fig.set(title="Process vs. CPUs requested")

    ax2 = plt.twinx()

    sns.scatterplot(data_df["cpu_used"], color="red", ax=ax2, legend=False)

    box = fig.get_figure()

    fig.set_xticks(data_df["names"].to_list())
    fig.set_xticklabels(data_df["names"].to_list(), rotation=90, fontsize=6)

    box.savefig("test.png")
    plt.clf()


def graph_process_vs_peak_log(data_df: pl.DataFrame):
    print("Generating Process VS Peak memory (LOG scale)", end="\r", flush=True)
    sns.set(rc={"figure.figsize": (25, 25)})
    new_data = data_df.with_columns(
        (pl.col("memory_requested_mb").log(base=2)).alias("mem_req_mb_log")
    )

    fig = sns.lineplot(new_data, x="names", y="mem_req_mb_log")
    fig.set(title="Process vs. Memory")

    fig.set_xticks(data_df["names"])

    fig.set_xticklabels(data_df["names"].to_list(), rotation=90, fontsize=6)
    fig.set_ylim(0, new_data["mem_req_mb_log"].max() + 1)

    ax2 = plt.twinx()
    ax2.set_ylim(0, new_data["mem_req_mb_log"].max() + 1)

    sns.scatterplot(
        new_data["peak_memory_mb"].log(base=2), color="red", ax=ax2, legend=False
    )

    box = fig.get_figure()

    box.savefig("test2_log.png")
    plt.clf()


def graph_process_vs_peak(data_df: pl.DataFrame):
    print("Generating Process VS Peak memory graph", end="\r", flush=True)
    sns.set(rc={"figure.figsize": (25, 25)})
    fig = sns.lineplot(data_df, x="names", y="memory_requested_mb")
    fig.set(title="Process vs. Memory")

    fig.set_xticks(data_df["names"])

    fig.set_xticklabels(data_df["names"].to_list(), rotation=90, fontsize=6)
    fig.set_ylim(0, data_df["memory_requested_mb"].max() + 1000)

    ax2 = plt.twinx()
    ax2.set_ylim(0, data_df["memory_requested_mb"].max() + 1000)

    sns.scatterplot(data_df["peak_memory_mb"], color="red", ax=ax2, legend=False)

    box = fig.get_figure()

    box.savefig("test2.png")
    plt.clf()


def graph_peak_vs_clade(data_df: pl.DataFrame):
    print("Generating Peak Mem VS Clade graph", end="\r", flush=True)
    print(data_df.columns)

    data2 = data_df.with_columns(
        [
            pl.col("names")
            .str.split_exact(":", 1)
            .struct.rename_fields(["major_subworkflow", "other"])
            .alias("fields"),
        ]
    ).unnest("fields")

    unique_subwf = set(data2.get_column("major_subworkflow"))

    for i in unique_subwf:
        if i != "CUSTOM_DUMPSOFTWAREVERSIONS":
            fig, axes = plt.subplots(1, 2, figsize=(24, 12))

            data3 = data2.filter((pl.col("major_subworkflow") == i))
            print(i)

            sns.set(rc={"figure.figsize": (25, 25)})
            sns.boxplot(
                ax=axes[0],
                data=data3,
                x="other",
                y="peak_memory_mb",
            )

            data4 = data3.unique(
                [
                    "clade",
                    "unique_name",
                    "genome_size",
                    "entry_point",
                    "pipeline_time",
                    "pacbio_total",
                    "pacbio_file_no",
                    "cram_total",
                    "cram_file_no",
                    "cram_containers",
                ]
            )

            sns.scatterplot(ax=axes[1], data=data4, x="unique_name", y="genome_size")

            box = fig.get_figure()

            box.savefig(f"{i}-test-peak-clade.png")
            plt.clf()


def graph_per_workflow(data_df: pl.DataFrame, names: list, save_name: str):
    # Dataframe containing max
    df_avg_peak = (
        data_df.select(["names", "peak_memory_as_percentage"]).group_by("names").max()
    )

    df_with_workflow = (
        # Adapted from https://stackoverflow.com/questions/73699500/python-polars-split-string-column-into-many-columns-by-delimiter
        # Splits name by ':' to get major subworkflow id (split[0]) to group the dataframe by
        data_df.with_row_count("id")
        .with_columns(pl.col("names").str.split(":").alias("workflow_id"))
        .explode("workflow_id")
        .with_columns(
            ("workflow_id_" + pl.arange(0, pl.count()).cast(pl.Utf8).str.zfill(2))
            .over("id")
            .alias("placeholder")
        )
        .pivot(index=["id", "names"], values="workflow_id", columns="placeholder")
        .with_columns(pl.col("^workflow_id_.*$").fill_null(""))
        .join(data_df, on="names", how="left")
    )
    # Grab the columns containing the workflow name information
    workflow_cols = [
        i for i in df_with_workflow.columns if i.startswith("workflow_id_")
    ]

    # Generate corrected names in each subworkflow upto Workflow - sub - sub - process
    # This should be generated by the class
    for i in names:
        df_by_process = df_with_workflow.filter(
            pl.col("workflow_id_00") == i
        ).with_columns(
            # Workflows shouldn't get more fractal than this...
            pl.when(pl.col("desc") == "WSSP")
            .then(
                pl.concat_str(
                    [
                        pl.col(workflow_cols[-3]),
                        pl.col(workflow_cols[-2]),
                        pl.col(workflow_cols[-1]),
                    ],
                    separator=":",
                )
            )
            .when(pl.col("desc") == "WSP")
            .then(
                pl.concat_str(
                    [pl.col(workflow_cols[-3]), pl.col(workflow_cols[-2])],
                    separator=":",
                )
            )
            .when(pl.col("desc") == "WP")
            .then(pl.col(workflow_cols[-3]))
            .otherwise(pl.col(workflow_cols[-1]))
            .alias("corrected_final")
        )

        # merge peak
        df_peak_names = df_by_process.select(["names", "corrected_final"]).join(
            other=df_avg_peak, on="names", how="left"
        )

        # now for the actual box plt
        fig = sns.boxplot(
            data=df_by_process,
            x="corrected_final",
            y="average_memory_used_as_percentage",
            log_scale=False,
        )
        fig.set(ylim=[-1, df_peak_names["peak_memory_as_percentage"].max()])

        ax2 = plt.twinx()
        ax2.set(ylim=[-1, df_peak_names["peak_memory_as_percentage"].max()])
        sns.scatterplot(
            data=df_peak_names,
            x="corrected_final",
            y="peak_memory_as_percentage",
            ax=ax2,
        )

        plt.savefig(f"{save_name}_{i}.png")
        plt.clf()


def graph_keys_against_genome(
    data_df: pl.DataFrame, workflow_names: list, key_processes: list
):
    graph_params = {
        0: ["realtime_seconds", "pacbio_total", "pacbioVStime"],
        1: ["genome_size", "pacbio_total", "pacbioVSgenome"],
        2: ["realtime_seconds", "cram_containers", "cramVSgenome"],
        3: ["genome_size", "cram_containers", "cramcVStime"],
        4: ["realtime_seconds", "genome_size", "timeVSgenome"],
    }

    for i in key_processes:
        subset_df = data_df.filter(pl.col("names").str.contains(i)).select(
            pl.col(
                [
                    "names",
                    "clade",
                    "pacbio_total",
                    "cram_containers",
                    "realtime_seconds",
                    "genome_size",
                ]
            )
        )
        for item, params in graph_params.items():
            print(
                f"Generating graph for:\t {i} | Params == {params}",
                end="\r",
                flush=True,
            )
            sns.lmplot(
                data=subset_df,
                x=params[0],
                y=params[1],
                x_estimator=np.mean,
                hue="clade",
                line_kws={"color": "red"},
            )
            # fig.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1)
            plt.savefig(f"S_{params[-1]}_{i}.png")
            plt.clf()
