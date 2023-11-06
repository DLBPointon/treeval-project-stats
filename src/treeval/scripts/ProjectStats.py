# Python imports
import io
import re
import os
import pandas as pd
from itertools import count
from sys import stdout

# TreeVal imports
from header import Header
from execution import Execution

class Colours:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

class ProjectStats:
    
    _instance_counter = count(0)
    
    def __init__ (self, file: str):
        self.instance       = next(self._instance_counter)
        self.file           = str(file)
        self.contents       = ProjectStats.get_contents(self)
        self.header_block   = Header(self.contents[1:14])
        self.uniquename     = self.header_block.uniquename
        self.id             = re.search(r'^[a-z]*', self.uniquename).group() # returns initial lowercase characters (upto 2) important for DTOL and presumably EBP
        self.fasta_mb       = round(self.header_block.genome_size / 1000000, 2)
        self.cram_gb        = round(self.header_block.cram_totaldata / 1000000000, 2)
        self.pacbio_gb      = round(self.header_block.pacbio_totaldata / 1000000000, 2)
        self.cram_avg       = round(self.cram_gb / self.header_block.cram_count, 2)
        self.pacbio_avg     = round(self.pacbio_gb / self.header_block.pacbio_count, 2)
        
        self.main_block     = "IM THE EXECUTION PARSER THAT DOESN'T EXIST YET"

        self.collection         = Header.__iter__(self)

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t {a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents']]
        txt.write(")")
        return txt.getvalue()


    def __str__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t {a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents']]
        txt.write(")")
        return txt.getvalue()

    @staticmethod
    def get_contents(self) -> list:
        with open (self.file) as datafile:
            return datafile.readlines()

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
                            columns = ['Unique_name', 'Entry_Point', 'Pipeline_Version', 'Duration_(Hrs)', 'Clade', 'Prefix', 'Fasta_(mb)', 'Ticket', 'Longread_(AVG_GB)', 'HiC__(AVG_GB)', 'Longread_(TOTAL_GB)', 'HiC_(TOTAL_GB)']
                            )
    
    print_report(header_df, empty_files)
        
if __name__ == "__main__":
    main()