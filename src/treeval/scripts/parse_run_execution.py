import io
import math
import sys

from master_list import master_list
from general_functions import normalise_values, fix_time


class TooManyProcesses(Exception):
    """
    Exception raised if the processes in the TreeVal execution log, exceed those expected.

    Attributes:
        process -- unexpected process
        message -- explanation of the error
    """

    def __init__(self, process, master):
        self._process = process
        self._master_list = master
        self._message = TooManyProcesses.message(self)
        super().__init__(self.message)

    def message(self):
        error_message = ''.join([i + '\n' for i in self._master_list])
        error = f"Process ({self._process}) not found in master process list. Have you modified the pipeline?\nMaster list:\n {error_message}"
        return error


class ParseRunExecution:
    def __init__(self, block,):

        self.condensed, self.efficiency     = ParseRunExecution.condense(self, block)
        self.list_of_list, self.headers     = ParseRunExecution.dict_to_list(self.condensed)
        self.collection                     = ParseRunExecution.__iter__(self)


    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value


    def __repr__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t\t {a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents', 'efficiency_dict']]

        return txt.getvalue()


    def __str__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t\t {a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents', 'efficiency_dict']]

        txt.write("\t )")
        return txt.getvalue()


    def dict_to_list(data_dict: dict) -> list:
        converted = []
        headers = []
        for k, v in data_dict.items():
            headers.append(k)
            converted.append(v)
        return converted, headers


    def efficiency_calculator(self, data: list) -> dict:
        """
        Get the pipeline total mem efficiency and cpu efficiency
        """
        mem_usage   = []
        mem_request = []
        cpu_usage   = []
        cpu_request = []
        for x, y in data.items():
            for sub_list in y:
                cpu_request.append(int(sub_list[0]))                                # cpu request by user
                mem_request.append(normalise_values(self, sub_list[1]))             # mem request by user
                cpu_usage.append(math.ceil(float(sub_list[4].split('%')[0]) / 100)) # number of cores used = roundup(CPU_percent  / 100)
                mem_usage.append(normalise_values(self, sub_list[-1].strip()))      # Using peak mem reported by process

        return { 'MEM_EFFICIENCY' : {
                                    'MEM_USAGE'     : sum(mem_usage),
                                    'MEM_REQUEST'   : sum(mem_request),
                                    'MEM_RUN_EFF'   : (sum(mem_request) / sum(mem_usage)) * 100
                                    },
                'CPU_EFFICIENCY' : {
                                    'CPU_USAGE'     : sum(cpu_usage),
                                    'CPU_REQUEST'   : sum(cpu_request),
                                    'CPU_RUN_EFF'   : (sum(cpu_request) / sum(cpu_usage)) * 100
                                    }
                }


    def condense(self, data: list):
        processes = ParseRunExecution.get_unique_processes(data)
        data_per_process = ParseRunExecution.collect_per_process(data, processes)
        efficiency_dict = ParseRunExecution.efficiency_calculator(self, data_per_process)
        condensed = ParseRunExecution.condense_data(self, data_per_process)
        process_correction = ParseRunExecution.compare_to_masterlist(self, condensed)
        condensed.update(process_correction)
        sorted_dict = dict(sorted(condensed.items())) # Alphabetically sort the keys, means all iterations should have same order
        return sorted_dict, efficiency_dict


    def get_unique_processes(data: list) -> list:
        """
        Return unique list of processes in execution lo
        """
        return list(set([i.split(' ')[0] for i in data]))


    def collect_per_process(data: list, processes: list) -> dict:
        """
        Collect completed processes per process, filtering out the incomplete or errored cases
        """
        collection = dict()
        counter = 0
        for i in processes:
            for ii in data:
                if ii.split(' ')[0] == i and str(ii.split('\t')[1]) == 'COMPLETED':
                    ii = ii.split('\t')[3:]
                    if i in collection:
                        collection[i].append(ii)
                    else:
                        collection[i] = [ii]

        return collection


    def condense_data(self, data: dict):
        """
        Condense data from the execution log into an easier averaged format
        So ten lines of data recorded by x process becomes one line of average(data) by x process
        """
        condensed_data = {}
        for process, data_lists in data.items():
            process_entry = str(process.split(':')[0])
            if process_entry in ['RAPID', 'FULL']:
                process = ':'.join(process.split(':')[3:])  # Gets subworkflows + process inside subworkflows
            elif 'SANGERTOL_TREEVAL' in process_entry:      # LEGACY ENTRY POINT
                process = ':'.join(process.split(':')[2:])  # Gets subworkflows + process
            else:
                print('Ooops, I\'m programmed to not recognise the given entry point here')
            if len(data_lists) <= 1:
                condensed_data[process] = [ int(data_lists[0][0]),
                                            normalise_values(self, data_lists[0][1]),
                                            normalise_values(self, data_lists[0][1]),
                                            ParseRunExecution.calculate_avg_time(fix_time(data_lists[0][3].split(' '))),
                                            int(float(data_lists[0][4].split('%')[0])),
                                            int(float(data_lists[0][5].split('%')[0])),
                                            round((normalise_values(self, data_lists[0][6].split('\\')[0]) / normalise_values(self, data_lists[0][1])) * 100, 0)]
            else:
                cpus = []
                memory = []
                realtime= []
                cpu_percent = []
                mem_percent = []
                peak_mem = []
                for i in data_lists:
                    cpus.append(int(i[0]))                                                      # '16'         - REQUESTED CPU
                    memory.append(normalise_values(self, i[1]))                     # '130 GB'     - REQUESTED MEM
                    realtime.append(
                        fix_time(i[3].split(' '))                             # '29m 33s'    - REALTIME EXECUTION TIME
                    )
                    cpu_percent.append(int(float(i[4].split('%')[0])))                          # '1441.5%'    - CPU UTILISATION PERCENTAGE
                    mem_percent.append(int(float(i[5].split('%')[0])))                          # '6.5%'       - MEM UTILISATION PERCENTAGE
                    peak_mem.append(normalise_values(self, i[6].split('\\')[0]))    # '25.8 GB\n'  - REPORTED PEAK MEMORY | NOW PERCENTAGE OF REQUESTED MEM
                avg_cpu = sum(cpus) / len(cpus)
                avg_mem = int(sum(memory) / len(memory))
                tot_mem = int(sum(memory))
                avg_realtime = ParseRunExecution.calculate_avg_time(realtime)
                avg_pcpu = sum(cpu_percent) / len(cpu_percent)
                avg_pmem = sum(mem_percent) / len(mem_percent)
                avg_peak = round((sum(peak_mem) / len(peak_mem)) / (int(sum(memory) / len(memory))) * 100, 0)
                tot_peak = sum(peak_mem)
                condensed_data[process] = [ avg_cpu,
                                            avg_mem,
                                            tot_mem,
                                            avg_realtime,
                                            avg_pcpu,
                                            avg_pmem,
                                            avg_peak,
                                            tot_peak
                                            ]
        return condensed_data


    def compare_to_masterlist(self, data_dict: dict) -> dict:
        """
        Compare created list of execution logs against a master list of processes

        This is ensure that the RAPID and FULL pipeline have data of the same width
        which is easier for df ingestion.
        """
        if len(master_list) == len(data_dict):
            # Indicates that this is a FULL treeval run in which all processes have fun
            return data_dict

        not_in_run = {}
        dict_list = [k for k, v in data_dict.items()]
        #print(f'{len(dict_list)} == {len(master_list)}')
        if set(dict_list) == set(master_list):
            pass # Because it needs no correction
        else:
            # Checks for missing processes (which is expected between full and rapid) and writes an NA list
            # This makes it MUCH easier to merge into the full dataframe later
            for i in master_list:
                if i not in dict_list:
                    not_in_run[i] = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']
                else:
                    pass

        # Double checks there's no extra processes, caused by modified pipeline
        for i in dict_list:
            if i not in master_list:
                # error out for some reason raise TooManyProcesses(self, i, master_list)
                print(f"error due to {i}")
                sys.exit()
            else:
                pass

        return not_in_run


    def calculate_avg_time(times: list) -> int:
        counter = 0
        total_time = 0
        if not isinstance(times, dict):
            for i in times:
                counter += 1
                total_time += i.get('s')
        else:
            total_time = times.get('s')
            counter = 1

        return total_time / counter