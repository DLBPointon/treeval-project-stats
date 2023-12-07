# Public Libraries
import re
import io
import re
from itertools          import count

# Classes for Project
from parse_input_data   import ParseInputData
from parse_run_data     import ParseRunData
from parse_execution    import ParseExecution
from parse_co2_data     import ParseCo2Data
from general_functions  import get_contents

class RunParser:

    _instance_counter = count(0)

    def __init__ (self, file: str, co2: str = ''):
        self.counter        = next(self._instance_counter)
        self.file           = file

        file_contents       = get_contents(self)
        if file_contents[0].startswith('---RUN_DATA---\n'):
            run_index       = file_contents.index('---RUN_DATA---\n')
            input_index     = file_contents.index('---INPUT_DATA---\n')
            execution_index = file_contents.index('---RESOURCES---\n')

            self.data_type  = ['EXECUTION LONG', 'TreeValProject.Summary']
            self.run_data   = ParseRunData( file_contents[ run_index+1:input_index ] )
            self.input_data = ParseInputData( file_contents[ input_index+1 : execution_index ] )
            self.execution  = ParseExecution( file_contents[execution_index+1:] )
        else:
            self.data_type  = ['EXECUTION LOG ONLY']
            self.execution  = ParseExecution( file_contents )

        if co2 != '':
            self.data_type  = self.data_type.append('CO2 DATA')
            co2_contents    = get_contents( co2 )
            self.co2_data   = ParseCo2Data( co2_contents )

        self.data_type      = ' + '.join(self.data_type)
        self.collection     = self.__iter__()


    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value


    def __repr__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t{a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents']]
        txt.write(")")
        return txt.getvalue()


    def __str__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t{a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents']]
        txt.write(")")
        return txt.getvalue()