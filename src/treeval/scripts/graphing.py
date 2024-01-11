import seaborn as sns
import matplotlib.pyplot as plt
import polars as pl

def graph_cpu_vs_process( data_df: pl.DataFrame):
    print('Graph1')
    sns.set(rc = {'figure.figsize':(25,25)})
    fig = sns.lineplot(
        data_df,
        x='names',
        y='cpus_requested'
    )
    fig.set(
        title='Process vs. CPUs requested'
    )

    ax2 = plt.twinx()

    sns.scatterplot(data_df['cpu_used'], color='red', ax=ax2, legend=False)

    box = fig.get_figure()

    fig.set_xticks(data_df['names'].to_list())
    fig.set_xticklabels(data_df['names'].to_list(), rotation=90, fontsize=6)

    box.savefig('test.png')
    plt.clf()


def graph_process_vs_peak_log(data_df: pl.DataFrame):
    print('test2.png : log scale')
    sns.set(rc = {'figure.figsize':(25,25)})
    new_data = data_df.with_columns((pl.col('memory_requested_mb').log(base=2)).alias('mem_req_mb_log'))

    fig = sns.lineplot(
        new_data,
        x='names',
        y='mem_req_mb_log'
    )
    fig.set(
        title='Process vs. Memory'
    )

    fig.set_xticks(data_df['names'])

    fig.set_xticklabels(data_df['names'].to_list(), rotation=90, fontsize=6)
    fig.set_ylim(0, new_data['mem_req_mb_log'].max()+1)

    ax2 = plt.twinx()
    ax2.set_ylim(0, new_data['mem_req_mb_log'].max()+1)

    sns.scatterplot(new_data['peak_memory_mb'].log(base=2), color='red', ax=ax2, legend=False)

    box = fig.get_figure()

    box.savefig('test2_log.png')
    plt.clf()

def graph_process_vs_peak(data_df: pl.DataFrame):
    print('Graph2')
    sns.set(rc = {'figure.figsize':(25,25)})
    fig = sns.lineplot(
        data_df,
        x='names',
        y='memory_requested_mb'
    )
    fig.set(
        title='Process vs. Memory'
    )

    fig.set_xticks(data_df['names'])

    fig.set_xticklabels(data_df['names'].to_list(), rotation=90, fontsize=6)
    fig.set_ylim(0, data_df['memory_requested_mb'].max()+1000)

    ax2 = plt.twinx()
    ax2.set_ylim(0, data_df['memory_requested_mb'].max()+1000)

    sns.scatterplot(data_df['peak_memory_mb'], color='red', ax=ax2, legend=False)

    box = fig.get_figure()

    box.savefig('test2.png')
    plt.clf()

def graph_peak_vs_clade(data_df: pl.DataFrame):
    print('Graph3')
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
        if i != 'CUSTOM_DUMPSOFTWAREVERSIONS':
            fig, axes = plt.subplots(1, 2, figsize=(24, 12))

            data3 = data2.filter((pl.col('major_subworkflow') == i))
            print(i)

            sns.set(rc = {'figure.figsize':(25,25)})
            sns.boxplot(
                ax = axes[0],
                data = data3,
                x='other',
                y='peak_memory_mb',
            )

            data4 = data3.unique(['clade', 'unique_name', 'genome_size', 'entry_point', 'pipeline_time', 'pacbio_total', 'pacbio_file_no', 'cram_total', 'cram_file_no', 'cram_containers'])

            sns.scatterplot(
                ax=axes[1],
                data = data4,
                x='unique_name',
                y='genome_size'
            )


            box = fig.get_figure()

            box.savefig(f'{i}-test-peak-clade.png')
            plt.clf()

    """    unique_process = data2.get_column("other")"""


def graph_per_workflow( data_df: pl.DataFrame , unique_names: list):

    pass
