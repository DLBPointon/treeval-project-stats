import io
import re
import ast
import numpy as np


class ParseInputData:
    def __init__(self, contents: list) -> None:
        sample = contents[0].split(" ")[-1].strip()
        self.sample = re.sub(
            "[^a-zA-Z0-9_]", "", sample
        )  # Remove the [ ] that occur in some cases
        self.get_tol_prefix
        self.genome_size = self.fix_data(
            [i for i in contents if i.startswith("InputAssemblyData")]
        )
        self.pacbio_data = self.fix_data(
            [i for i in contents if i.startswith("Input_PacBio_Files")]
        )
        self.cram_data = self.fix_data(
            [i for i in contents if i.startswith("Input_Cram_Files")]
        )

        self.collection = self.__iter__()

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [
            txt.write(f"\t\t{a} = '{v}' \n")
            for a, v in self.collection
            if a not in ["collection"]
        ]
        txt.write(f"\t)")
        return txt.getvalue()

    def __str__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [
            txt.write(f"\t\t{a} = '{v}' \n")
            for a, v in self.collection
            if a not in ["collection"]
        ]
        txt.write(f"\t)")
        return txt.getvalue()

    def fix_data(self, input_data: str) -> list:
        first_list = re.search(r"\[\[(.*)\],", input_data[0]).group()
        data_type = re.search(r"id:([a-zA-Z0-9]*)", str(first_list)).group(1)
        file_size_list_raw = re.search(r"sz:(([0-9].*|\[.*\])(\, [ln]..*\:|\, [cn]..*\:))|sz:([0-9]*)", str(first_list))
        cn_count = re.search(r"cn:([0-9]*)", first_list)
        if cn_count == None:
            cn_count = np.nan
        else:
            cn_count = float(cn_count.group(1))

        if file_size_list_raw.group(4):
            file_size_list = [file_size_list_raw.group(4)]
        elif file_size_list_raw.group(2):
            if '[' in file_size_list_raw.group(2):
                file_size_list = ast.literal_eval(file_size_list_raw.group(2))
                file_size_list = [int(i) for i in file_size_list]
            else:
                file_size_list = [ast.literal_eval(file_size_list_raw.group(2))]
        else:
            file_size_list = [0]

        file_size_list = [int(i) for i in file_size_list]

        return {
            "id": data_type,
            "file_size_list": file_size_list,
            "file_size_total": sum(file_size_list),
            "file_count": len(file_size_list),
            "containers": cn_count,
        }

    @property
    def get_tol_prefix(self) -> str:
        suffix = re.match(r"^[a-z]*", self.sample)
        if suffix:
            return suffix.group()
        else:
            return "unknown"
