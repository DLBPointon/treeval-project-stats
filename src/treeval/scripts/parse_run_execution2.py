import io

from general_functions import get_contents

class RunExecution:

    def __init__(self, file):
        self.file               = str(file)
        self.all_processes      = RunExecution.get_all_processes(get_contents(self)[1:])
        self.collection         = RunExecution.__iter__(self)


    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value


    def __repr__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t {a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents', 'efficiency_dict']]

        return txt.getvalue()


    def get_all_processes(filedata: list) -> dict:
        process = filedata[-1].split(' ')[0] # last line should always be the DUMPSOFTWAREVERSIONS process
        if process.endswith('DUMPSOFTWAREVERSIONS'):
            print(process)
            if len(process.split(':')) == 3 and filedata[0].startswith('NFCORE'):
                print('An NFCORE pipeline with no entry points')
            elif len(process.split(':')) >= 3 and filedata[1].startswith('NFCORE'):
                print('An NFCORE pipeline, likely with some soft of entry point')
            elif len(process.split(':')) == 3 and not filedata[1].startswith('NFCORE'):
                print('A CUSTOM NFCORE pipeline with no entry points')
            elif len(process.split(':')) >= 3 and not filedata[1].startswith('NFCORE'):
                print('An CUSTOM NFCORE pipeline, likely with some soft of entry point')
            else:
                print('I dont know')