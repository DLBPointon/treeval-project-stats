import io
from master_list import master_list

class TooManyProcesses(Exception):
    """
    Exception raised if the processes in the TreeVal execution log, exceed those expected.

    Attributes:
        process -- unexpected process
        message -- explanation of the error
    """

    def __init__(self, process, master_list, verbose):
        self._process = process
        self._master_list = master_list
        self._message = TooManyProcesses.message(self)
        self._verbose = verbose
        super().__init__(self.message)

    def message(self):
        #if self._verbose:
        error_message = ''.join([i + '\n' for i in self.master_list])
        error = f"Process ({self.process}) not found in master process list. Have you modified the pipeline?\nMaster list:\n {error_message}"
        return error


class Execution():
    def __init__(self, block,):

        self.condensed                      = Execution.condense(block)
        self.list_of_list, self.headers     = Execution.dict_to_list(self.condensed)
        self.collection                     = Execution.__iter__(self)


    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value


    def __repr__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t\t {a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents']]

        return txt.getvalue()


    def __str__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t\t {a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection', 'contents']]

        txt.write("\t )")
        return txt.getvalue()


    def dict_to_list(data_dict: dict) -> list:
        converted = []
        headers = []
        for k, v in data_dict.items():
            headers.append(k)
            converted.append(v)
        return converted, headers


    def condense(data: list):
        processes = Execution.get_unique_processes(data)
        data_per_process = Execution.collect_per_process(data, processes)
        condensed = Execution.condense_data(data_per_process)
        process_correction = Execution.compare_to_masterlist(condensed)
        condensed.update(process_correction)
        sorted_dict = dict(sorted(condensed.items())) # Alphabetically sort the keys, means all iterations should have same order
        return sorted_dict


    def get_unique_processes(data: list) -> list:
        processes_list = [i.split(' ')[0] for i in data]
        unique_processes = set(processes_list)
        set_list = list(unique_processes)
        return set_list


    def collect_per_process(data: list, processes: list) -> dict:
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


    def condense_data(data: dict):
        condensed_data = {}
        for process, data_lists in data.items():
            process_entry = str(process.split(':')[0])
            if process_entry in ['RAPID', 'FULL']:
                process = ':'.join(process.split(':')[3:]) # Gets subworkflows + process inside subworkflows 
            elif 'SANGERTOL_TREEVAL' in process_entry: # FULL entry point
                process = ':'.join(process.split(':')[2:]) # Gets subworkflows + process
            else:
                print('Ooops, I dont recognise the entry point here')
            if len(data_lists) <= 1:
                condensed_data[process] = [ int(data_lists[0][0]),
                                            Execution.normalise_memory(data_lists[0][1]),
                                            Execution.calculate_avg_time(Execution.fix_time(data_lists[0][3].split(' '))),
                                            int(float(data_lists[0][4].split('%')[0])),
                                            int(float(data_lists[0][5].split('%')[0])),
                                            round((Execution.normalise_memory(data_lists[0][6].split('\\')[0]) / Execution.normalise_memory(data_lists[0][1])) * 100, 0)]
            else:
                cpus = []
                memory = []
                realtime= []
                cpu_percent = []
                mem_percent = []
                peak_mem = []
                for i in data_lists:
                    cpus.append(int(i[0]))                                           # '16'         - REQUESTED CPU
                    memory.append(Execution.normalise_memory(i[1]))                  # '130 GB'     - REQUESTED MEM
                    realtime.append(
                        Execution.fix_time(i[3].split(' '))                          # '29m 33s'    - REALTIME EXECUTION TIME
                    )
                    cpu_percent.append(int(float(i[4].split('%')[0])))               # '1441.5%'    - CPU UTILISATION PERCENTAGE
                    mem_percent.append(int(float(i[5].split('%')[0])))               # '6.5%'       - MEM UTILISATION PERCENTAGE
                    peak_mem.append(Execution.normalise_memory(i[6].split('\\')[0])) # '25.8 GB\n'  - REPORTED PEAK MEMORY | NOW PERCENTAGE OF REQUESTED MEM
                avg_cpu = sum(cpus) / len(cpus)
                avg_mem = int(sum(memory) / len(memory))
                avg_realtime = Execution.calculate_avg_time(realtime)
                avg_pcpu = sum(cpu_percent) / len(cpu_percent)
                avg_pmem = sum(mem_percent) / len(mem_percent)
                avg_peak = round((sum(peak_mem) / len(peak_mem)) / (int(sum(memory) / len(memory))) * 100, 0)
                condensed_data[process] = [ avg_cpu,
                                            avg_mem,
                                            avg_realtime,
                                            avg_pcpu,
                                            avg_pmem,
                                            avg_peak ]
        return condensed_data


    def compare_to_masterlist(data_dict: dict) -> dict:
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
            # Checks for missing processes (which is expected between full and rapid) and writes an NA dict
            for i in master_list:
                if i not in dict_list:
                    not_in_run[i] = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA']
                else:
                    pass

        # Double checks there's no extra processes, caused by modified pipeline
        for i in dict_list:
            if i not in master_list:
                raise TooManyProcesses(i, master_list)
            else:
                pass
        
        return not_in_run


    def normalise_memory(memory_value: str) -> int:
        """
        Convert everything to MegaBytes!
        """
        value = memory_value.split(' ')
        if memory_value == 0 or len(value) < 2:
            return 0
        
        suffix = value[1].strip()
        if suffix == 'TB':
            output = int(float(value[0])) * 1000000
        elif suffix == 'GB':
            output = int(float(value[0])) * 1000
        elif suffix == 'MB':
            output = int(float(value[0]))
        elif suffix == 'KB':
            output = round((int(float(value[0])) / 1000), 2)
        else:
            output = 999999999999999 # 999 TB of memory should start alarm bells
        return output


    def fix_time(time_list: list) -> dict:
        total = 0
        time_dict = {}
        if time_list[0] == "CANNOT":
            total = -1
        else:
            for i in time_list:
                if i.endswith('d'):
                    total += int(i.split('d')[0]) * 86400        # number of days * seconds in day
                elif i.endswith('h'):
                    total += (int(i.split('h')[0]) * 60) * 60    # number of hours * minutes in hour * seconds in minute
                elif i.endswith('ms'):
                    total += int(float(i.split('ms')[0])) * 1000 # number of miliseconds in seconds
                elif i.endswith('m'):
                    total += int(i.split('m')[0]) * 60           # number of minutes * seconds in minute
                elif i.endswith('s'):
                    total += int(float(i.split('s')[0]))         # nothing.. it's already in seconds
                else:
                    total = int(float(i))                        # nothing.. means its the newer formats which are already converted
            time_dict['s'] = total
            time_dict['m'] = round(total / 60, 2)
            time_dict['h'] = round(( total / 60 ) / 60, 2)
        return time_dict


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