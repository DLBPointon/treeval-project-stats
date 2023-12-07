import io

from general_functions import get_contents, normalise_values, fix_time

class Co2Parser:

    def __init__ (self, file: str):
        self.file = file
        self._file_data         = get_contents(self)
        self._processed_data    = self.condense_data()
        self.original_headers   = self.get_co2_columns()
        self.max_data           = self.max_data_dict()
        self.total_data         = self.total_data_dict()
        self.average_data       = self.average_data_dict() # rename property to method name
        self.max_sworkflow      = self.max_subworkflow_dict()
        self.total_sworkflow    = self.total_subworkflow_dict()
        self.average_sworkflow  = self.average_subworkflow_dict()
        self.collection         = self.__iter__()


    def __iter__(self):
        for attr, value in self.__dict__.items():
            if not attr.startswith('_'):
                yield attr, value


    def __repr__(self) -> str:
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        for a, v in self.collection:
            if a not in ['block', 'collection', 'max_data', 'total_data', 'average_data', 'average_sworkflow', 'total_sworkflow', 'max_sworkflow']:
                txt.write(f"\t {a} = '{v}' \n")
            if a in ['max_data', 'total_data', 'average_data','average_sworkflow', 'total_sworkflow', 'max_sworkflow']:
                txt.write( f"\t {a} = \/ \n")
                for k, vv in v.items():
                    txt.write(f"\t\t{k} == {len(vv)} Data Points\n")
        txt.write(")")
        return txt.getvalue()


    def get_co2_columns(self) -> list:
        """
        Return the original headers of the co2 file.
        """
        raw_names = self._file_data[0].split('\t')
        return [ i if not i.endswith('\n') else i.split('\n')[0] for i in raw_names ]


    def process_co2_line(self, line: list) -> list:
        """
        Return a list formatted line for line in co2 file.
        Time is converted to dict of total h, total m, total s/
        CO2e and Energy usage are converted to mg and mWh
        """
        return [    ':'.join(line[1].split(' ')[0].split(':')[2:]), # PROCESS NAMES
                    normalise_values(self, line[3]),                # ENERGY USAGE
                    normalise_values(self, line[4]),                # CO2e
                    fix_time(line[5].split(" ")),                   # TIME TAKEN
                    line[6],                                        # CPUS
                    line[2]                                         # SUCCESS OR FAIL
                ]


    def condense_data(self) -> dict:
        """
        Collapse cases where a process is run multiple times, in cases of horizontal scaling.
        It creates a nested list containing the data from multiple process runs.
        """
        condensed_data = {}
        for line in self._file_data[1:]:
            line_list = line.split('\t')
            line_processed = self.process_co2_line(self, line_list)
            if line_processed[1] != None and line_processed[5] != 'FAILED':
                if not line_processed[0] in condensed_data.keys():
                    condensed_data[line_processed[0]] = {
                        "ENERGY": [line_processed[1]],
                        "CO2e"  : [line_processed[2]],
                        "TIME"  : [line_processed[3]],
                        "CPUS"  : [line_processed[4]],
                        "TYPE"  : [line_processed[5]]
                    }
                else:
                    condensed_data[line_processed[0]]["ENERGY"].append(line_processed[1]),
                    condensed_data[line_processed[0]]["CO2e"].append(line_processed[2]),
                    condensed_data[line_processed[0]]["TIME"].append(line_processed[3]),
                    condensed_data[line_processed[0]]["CPUS"].append(line_processed[4]),
                    condensed_data[line_processed[0]]["TYPE"].append(line_processed[5])
        return condensed_data


    def collapse_nested_lists(data: dict) -> dict:
        """
        Collapse the nested lists from condense_data
        """
        corrected = {}
        for x, y in data.items():
            corrected[x] = {
                'COLLECTS'      : y['COLLECTS'], # MUST REMAIN A LIST
                'SUB_ENERGY'    : [ii for i in y['SUB_ENERGY'] for ii in i],
                'SUB_CO2e'      : [ii for i in y['SUB_CO2e'] for ii in i],
                'SUB_TIME'      : [ii for i in y['SUB_TIME'] for ii in i],
                'SUB_CPUS'      : [int(ii) for i in y['SUB_CPUS'] for ii in i]
            }
        return corrected


    def condense_per_sworkflow (self) -> dict:
        """
        Collapse data down to the subworkflow level rather than module.
        """
        condensed_data = {}
        for x, y in self._processed_data.items():
            hierarchy = x.split(':')

            if len(hierarchy) < 2:
                subworkflow = x
            else:
                subworkflow = ':'.join(hierarchy[:-1])

            if not subworkflow in condensed_data.keys():
                condensed_data[subworkflow] = {
                    'COLLECTS'  : [hierarchy[-1]],
                    'SUB_ENERGY': [y['ENERGY']],
                    'SUB_CO2e'  : [y['CO2e']],
                    'SUB_TIME'  : [y['TIME']],
                    'SUB_CPUS'  : [y['CPUS']]
                }
                if not hierarchy[-1] in condensed_data[subworkflow]["COLLECTS"]:
                    condensed_data[subworkflow]["COLLECTS"].append(hierarchy[-1])
            else:
                condensed_data[subworkflow]["COLLECTS"].append(hierarchy[-1]),
                condensed_data[subworkflow]["SUB_ENERGY"].append(y['ENERGY']),
                condensed_data[subworkflow]["SUB_CO2e"].append(y['CO2e']),
                condensed_data[subworkflow]["SUB_TIME"].append(y['TIME']),
                condensed_data[subworkflow]["SUB_CPUS"].append(y['CPUS'])
        return self.collapse_nested_lists(condensed_data)


    def average_subworkflow_dict(self) -> dict:
        """
        Create a dictionary of averaged data per subworkflow
        """
        data = self.condense_per_sworkflow(self)
        average_dict = {}

        for x, y in data.items():
            time_list = [ x['s'] for x in y['SUB_TIME']]
            average_dict[x] = { "COLLECTS"  : y['COLLECTS'],
                                "AVG_ENERGY": self.calc_average(y['SUB_ENERGY']),
                                "AVG_CO2e"  : self.calc_average(y['SUB_CO2e']),
                                "AVG_CPUS"  : self.calc_average(y['SUB_CPUS']),
                                "AVG_TIME"  : fix_time([self.calc_average(time_list)])
                                }
        return average_dict


    def max_subworkflow_dict(self) -> dict:
        """
        Create a dictionary of the maximal value for each category
        """
        data = self.condense_per_sworkflow(self)
        max_dict = {}

        for x, y in data.items():
            time_list = [ x['s'] for x in y['SUB_TIME']]
            max_dict[x] = { "COLLECTS"  : y['COLLECTS'],
                            "MAX_ENERGY": max(y['SUB_ENERGY']),
                            "MAX_CO2e"  : max(y['SUB_CO2e']),
                            "MAX_CPUS"  : max(y['SUB_CPUS']),
                            "MAX_TIME"  : fix_time([max(time_list)])
                            }
        return max_dict


    def total_subworkflow_dict(self) -> dict:
        """
        Create a dictionary of the total value per category
        """
        data = self.condense_per_sworkflow(self)
        total_dict = {}

        for x, y in data.items():
            time_list = [ x['s'] for x in y['SUB_TIME']]
            total_dict[x] = { "COLLECTS"  : y['COLLECTS'],
                            "TOT_ENERGY": round(sum(y['SUB_ENERGY']), 2),
                            "TOT_CO2e"  : round(sum(y['SUB_CO2e']), 2),
                            "TOT_CPUS"  : round(sum(y['SUB_CPUS']), 2),
                            "TOT_TIME"  : fix_time([sum(time_list)])
                            }
        return total_dict


    # NEEDS CACHING OF SOME SORT AS IT WILL BE REFEREED TO THRICE!
    def all_data_dict(data: dict) -> dict:
        """
        Creates a dictionary of all raw data
        """
        the_all_dict = {}

        for x, y in data.items():
            cpu_list    = [ int(yyy) for xx, yy in y.items() if xx == 'CPUS' for yyy in yy]
            co2e_list   = [ yyy for xx, yy in y.items() if xx == 'CO2e' for yyy in yy ]
            time_list   = [ yyy['s'] for xx, yy in y.items() if xx == 'TIME' for yyy in yy ]
            energy_list = [ yyy for xx, yy in y.items() if xx == 'ENERGY' for yyy in yy ]

            the_all_dict[x] = { "ALL_ENERGY": energy_list,
                                "ALL_CO2e"  : co2e_list,
                                "ALL_CPUS"  : cpu_list,
                                "ALL_TIME"  : time_list
                                }

        return the_all_dict


    def calc_average(data: list) -> int:
        """
        Calculate the average value of the input list
        """
        return round(int(sum(data) / len(data)), 2)

    # THE BELOW 3 FUNCTIONS COULD BE SIMPLIFIED WITH
    # ONE OF THOSE WRAPPERS THAT TAKE A FUNC AS INPUT
    # GENERATE_DICTS( self, [self.calc_average, max, sum]) -> AVG, MAX, TOT

    def average_data_dict (self) -> dict:
        average_dict = {}

        for x, y in self.all_data_dict(self._processed_data).items():
            average_dict[x] = { "AVG_ENERGY": self.calc_average(y['ALL_ENERGY']),
                                "AVG_CO2e"  : self.calc_average(y['ALL_CO2e']),
                                "AVG_CPUS"  : self.calc_average(y['ALL_CPUS']),
                                "AVG_TIME"  : fix_time([self.calc_average(y['ALL_TIME'])])
                                }

        return average_dict


    def total_data_dict (self) -> dict:
        total_dict = {}

        for x, y in self.all_data_dict(self._processed_data).items():
            total_dict[x] = {   "TOT_ENERGY": sum(y['ALL_ENERGY']),
                                "TOT_CO2e"  : sum(y['ALL_CO2e']),
                                "TOT_CPUS"  : sum(y['ALL_CPUS']),
                                "TOT_TIME"  : fix_time([sum(y['ALL_TIME'])])
                                }

        return total_dict


    def max_data_dict (self) -> dict:
        max_dict = {}

        for x, y in self.all_data_dict(self._processed_data).items():
            max_dict[x] = {   "MAX_ENERGY"  : max(y['ALL_ENERGY']),
                                "MAX_CO2e"  : max(y['ALL_CO2e']),
                                "MAX_CPUS"  : max(y['ALL_CPUS']),
                                "MAX_TIME"  : fix_time([max(y['ALL_TIME'])])
                                }

        return max_dict