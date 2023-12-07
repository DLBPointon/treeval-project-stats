import io
from general_functions import fix_time

class ParseRunData:

    def __init__(self, contents: list):
        print(contents)
        self.pipeline_version   = self.pipeline_data([i for i in contents if i.startswith("Pipeline_version")])
        self.run_name           = self.pipeline_data([i for i in contents if i.startswith("Pipeline_runname")])
        self.run_id             = self.pipeline_data([i for i in contents if i.startswith("Pipeline_session")])
        self.pipeline_seconds   = fix_time(self.prep_time([i for i in contents if i.startswith("Pipeline_duration")]))
        self.pipeline_start     = self.prep_date([i for i in contents if i.startswith("Pipeline_datastrt")])
        self.pipeline_complete  = self.prep_date([i for i in contents if i.startswith("Pipeline_datecomp")])
        self.entry_point        = self.pipeline_data([i for i in contents if i.startswith("Pipeline_entrypnt")])

        self.collection         = self.__iter__()


    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value


    def __repr__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t\t{a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents']]
        txt.write(")")
        return txt.getvalue()


    def __str__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t\t{a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents']]
        txt.write(f"\t)")
        return txt.getvalue()


    def pipeline_data(self, line: list) -> str:
        return line[0].split(' ')[-1].strip()


    def prep_time(self, line: list) -> list:
        return line[0].split(':')[-1].strip().split(' ')


    def prep_date(self, line: list) -> str:
        return line[0].split(' ')[-1].strip()