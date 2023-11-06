import re
import io
import re
from itertools import count

from header import Header
from execution import Execution

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