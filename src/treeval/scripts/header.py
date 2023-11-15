import io

class Header:
    def __init__(self, block: list):
        self.block              = block
        self.name               = Header.get_name(self)
        self.runname            = self.block[1].strip().split(" ")[-1]
        self.uniquename         = f"{self.name}-{self.runname}"
        self.version            = self.block[0].strip().split(" ")[-1]
        self.session            = self.block[2].strip().split(" ")[-1]
        self.datestrt           = self.block[4].strip().split(" ")[-1]
        self.dateend            = self.block[5].strip().split(" ")[-1]
        self.entrypnt           = self.block[6].strip().split(" ")[-1]
        self.yamlfile           = self.block[9].strip().split(" ")[-1]
        self.duration           = Header.fix_time(self.block[3].strip().split("  ")[1].split(" "))
        
        genome_data             = Header.fix_fasta(self.block[10])
        self.genome_size        = genome_data[1]
        self.genome_clade       = genome_data[2]
        self.genome_ticket      = genome_data[3]

        pacbio_data             = Header.fix_data(self.block[11])
        self.pacbio_count       = len(pacbio_data)
        self.pacbio_totaldata   = sum(pacbio_data)

        cram_data               = Header.fix_data(self.block[12])
        self.cram_count         = len(cram_data)
        self.cram_totaldata     = sum(cram_data)
        self.collection         = Header.__iter__(self)

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value


    def __repr__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t\t {a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection']]
        txt.write("\t )")
        return txt.getvalue()


    def __str__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [txt.write(f"\t\t {a} = '{v}' \n") for a, v in self.collection if a not in ['block', 'collection']]
        txt.write("\t )")
        return txt.getvalue()


    def get_name(self) -> str:
        name = self.block[8].strip().split("      ")[1]

        if name.startswith('['):
            name = name.split('[')[1].split(']')[0]

        return name


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


    @staticmethod
    def fix_data(input_data: str) -> list:
        count_files = eval(input_data.split(':')[3].split('],')[0]) # split data into per list from collection of lists
        if not isinstance (count_files, list):  # catches not a list objects
            count_files = [count_files]
        return count_files


    @staticmethod
    def fix_fasta(fasta: str) -> list:
        split_field = fasta.split('  ')[1].split(':')
        output_list = [ split_field[1].split(',')[0],
                    int(split_field[2].split(',')[0]),
                    split_field[3].split(',')[0],
                    split_field[4].split(']')[0],
                    str(split_field[4].split(']')[1][2:])
                    ]
        return output_list