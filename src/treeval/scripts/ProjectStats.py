# Python imports
import os
import plotly as px
import pandas as pd
from itertools import count
from sys import stdout

# TreeVal imports
from fileparsing import ProjectStats

class Colours:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'




def subset_dataframe(data_df: pd.DataFrame, ticket: list):
    if len(ticket) > 0:
        df = data_df[data_df["Ticket"].isin(ticket)]
    else:
        df = data_df
    return df

def generate_genome_vs_runtime(data_df: pd.DataFrame):
    fig = px.scatter(data_df, x='Hours', y='fasta_in_mb',
                    color='Assembly_clade', hover_data=['Sample_ID'], trendline="ols",
                    trendline_options=dict(log_x=True), #trendline_scope="overall", #trendline_color_override="black",
                    title = 'Size of Genome (MB) against runtime (Hours) - RAPID',
                    labels = { 'fasta_in_mb' : 'Fasta Size (MB)',
                                'Hours' : 'Runtime (Hours)',
                                'Assembly_clade' : 'Clade'})
    fig.update_layout(height=400)

    fig.show()

    fig = px.scatter(FULL_data, x='Hours', y='fasta_in_mb',
                    color='Assembly_clade', hover_data=['Sample_ID'], trendline="ols",
                    trendline_options=dict(log_x=True), #trendline_scope="overall", #trendline_color_override="black",
                    title = 'Size of Genome (MB) against runtime (Hours) - FULL',
                    labels = { 'fasta_in_mb' : 'Fasta Size (MB)',
                                'Hours' : 'Runtime (Hours)',
                                'Assembly_clade' : 'Clade'})
    fig.update_layout(height=400)

    fig.show()


def print_report(data_df: pd.DataFrame, empties: list):
    stdout.write(f"{Colours.HEADER}-"*50 + f'\n {Colours.END}')
    stdout.write(f"{Colours.BLUE}TreeVal{Colours.END}{Colours.RED}Project{Colours.END}.{Colours.GREEN}Summary{Colours.END} {Colours.YELLOW}Stats{Colours.END}!\n")
    stdout.write(f"{Colours.HEADER}-"*50 + f'\n {Colours.END}')
    stdout.write(f"Total data points: {len(data_df)} \n")
    stdout.write(f"{Colours.HEADER}-"*50 + f'\n {Colours.END}')
    stdout.write(f"Unique CLADE count:\n{data_df['Clade'].value_counts()}\n")
    stdout.write(f"{Colours.HEADER}-"*50 + f'\n {Colours.END}')
    stdout.write(f"Run Type Count:\n{data_df['Entry_Point'].value_counts()}\n")
    stdout.write(f"{Colours.HEADER}-"*50 + f'\n {Colours.END}')
    stdout.write(f"Ticket Type Count:\n{data_df['Ticket'].value_counts()}\n")
    stdout.write(f"{Colours.HEADER}-"*50 + f'\n {Colours.END}')
    if len(empties) >= 1:
        [stdout.write(f"Empty Files!:\n{i}\n") for i in empties]
        stdout.write(f"{Colours.HEADER}-"*50 + f'\n {Colours.END}')


def main():
    file_dir = '/lustre/scratch123/tol/resources/treeval/treeval_stats/release-1-0-0/'
    
    list_of_lists = []
    empty_files = []
    
    for file in os.listdir(file_dir):
        if os.stat(file_dir + file).st_size == 0:
            empty_files.append(file)
            pass
        else:
            data = ProjectStats(file_dir + file)
            list_of_lists.append(  [data.uniquename, data.header_block.entrypnt,
                                    data.header_block.version,data.header_block.duration.get('h'),
                                    data.header_block.genome_clade,data.id,
                                    data.fasta_mb,data.header_block.genome_ticket,
                                    data.pacbio_avg,data.cram_avg,
                                    data.header_block.pacbio_totaldata, data.header_block.cram_totaldata]
                                )

    header_df = pd.DataFrame(
                            list_of_lists,
                            columns = [ 'Unique_name', 'Entry_Point',
                                        'Pipeline_Version', 'Duration_(Hrs)',
                                        'Clade', 'Prefix',
                                        'Fasta_(mb)', 'Ticket',
                                        'Longread_(AVG_GB)', 'HiC__(AVG_GB)',
                                        'Longread_(TOTAL_GB)', 'HiC_(TOTAL_GB)' ]
                            )
    
    subset_df = subset_dataframe(header_df, ticket = [])
    
    generate_genome_vs_runtime(subset_df)
    
    #generate_longread_vs_runtime(header_df, ticket = [])
    
    #generate_hic_vs_runtime(header_df, ticket = [])
    
    #generate_clade_vs_runtime(header_df, ticket = [])
    
    print_report(header_df, empty_files)
        
if __name__ == "__main__":
    main()