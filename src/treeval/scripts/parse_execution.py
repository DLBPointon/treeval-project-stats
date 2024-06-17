import io
import sys
import math
import numpy as np
import polars as pl

from general_functions import normalise_values, fix_time, reorder


class ParseExecution:
    """
    Parses and formats the execution log data into a usable format.
    """

    def __init__(self, contents: list, file: str):
        # DEBUG FOR ORIGINAL FILE HEADERS = contents[0].strip().split('\t')
        self.file = file
        data_frame = self.generate_dataframe(contents)
        self.classification, master_list = self.classify_data(data_frame)
        corrected_data_frame = self.correct_dataframe_names(data_frame, master_list)
        self.data_frame = self.add_column_description(corrected_data_frame)

        self.collection = self.__iter__()

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [
            txt.write(f"\t\t {a} = '{v}' \n")
            for a, v in self.collection
            if a not in ["block", "collection", "contents", "efficiency_dict"]
        ]

        return txt.getvalue()

    def __str__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [
            txt.write(f"\t\t {a} = '{v}' \n")
            for a, v in self.collection
            if a not in ["block", "collection", "contents", "efficiency_dict"]
        ]

        txt.write(f"\t)")
        return txt.getvalue()

    def correct_datatypes(self, data: list) -> list:
        """
        Currently the data in the frame is all string, this needs correcting so it is usable.
        """
        if data[0] == "name" and data[-1] == "peak_rss\n":
            data[3] = "cpus_requested"
            data[4] = "memory_requested_mb"
            data[6] = "realtime_seconds"
            data[7] = "percent_cpu"
            data[8] = "average_memory_used_as_percentage"
            data[-1] = "peak_memory_mb"
            data.append("cpu_used")
            data.append("average_memory_used_as_mb")
            data.append("peak_memory_as_percentage")

        else:
            data[3] = int(data[3])
            data[4] = normalise_values(self, data[4])
            data[5] = int(data[5])
            data[6] = fix_time(data[6].split(" "))
            data[7] = int(float(data[7].split("%")[0]))
            data[8] = int(float(data[8].split("%")[0]))
            data[9] = normalise_values(self, data[9])
            data.append(
                math.ceil(float(data[7]) / 100)
            )  # /\ Calculate number of core used (rounded up to whole number as you can't request a fraction of a core)
            data.append(
                (data[4] / 100) * data[8]
            )  # /\ Calculate the actual memory used by process in MB
            data.append((data[9] / data[4] * 100))  # Peak mem percentage of request

        return data

    def convert_list_to_dict(self, lol: list) -> dict:
        big_dict = {}
        for i in lol[0]:
            list_index = lol[0].index(i)
            big_dict[lol[0][list_index]] = [i[list_index] for i in lol[1:]]
        return big_dict

    def generate_dataframe(self, data: list) -> pl.DataFrame:
        """
        Generate Polars dataframe
        Process names have been cleaned to remove ()
        """

        split_data = [i.split("\t") for i in data]

        corrected_dtypes = [
            self.correct_datatypes(i) for i in split_data if not "FAILED" in i
        ]
        list_to_dict = self.convert_list_to_dict(corrected_dtypes)

        trans_df = pl.DataFrame(list_to_dict)
        cleaned_df = trans_df.drop("module")
        process_updates = cleaned_df.with_columns(
            extracted=pl.col("name")
            .str.split_exact(" ", 1)
            .struct.rename_fields(["name1", "unneeded"])
            .alias("process_list")
        )

        return reorder(
            process_updates.unnest("extracted").drop(["name", "unneeded"]), 0, "name1"
        )

    def remove_common_string(
        self, smallest_process: list, process_list: list, process_count: int
    ) -> list:
        """
        removes common str in each sublist if total number of str == total number of processes
        (this avoids cases of large numbers of repeat processes getting trunctated)

        THIS DOES KEEP ORDER WITH THE DATAFRAME
        """
        remove_list = []
        flat_list = [ii for i in process_list for ii in i]

        if process_count != 1:
            for i in set(flat_list):
                if flat_list.count(i) == process_count:
                    remove_list.append(i)

        return [
            ":".join([ii for ii in i if not ii in remove_list]) for i in process_list
        ]  # Nested list comprehension! Doge Wow!

    def classify_data(self, dataframe):
        """
        Collapse
        """
        split_processes = [i.split(":") for i in dataframe.get_column(name="name1")]
        process_count = len(dataframe.get_column(name="name1"))
        smallest_process = min(split_processes)

        base = smallest_process[0]

        if len(smallest_process) == 3 and "NFCORE" in base:
            classify = ["NFCORE", f'NO ENTRY POINTS="{base}"']
        elif len(smallest_process) == 4 and "NFCORE" in smallest_process[1]:
            classify = ["NFCORE", f'ENTRY POINTS="{base}"']
        elif len(smallest_process) == 3 and not "NFCORE" in base:
            classify = ["CUSTOM", f'NO ENTRY POINTS="{base}"']
        elif len(smallest_process) >= 4 and not "NFCORE" in smallest_process[1]:
            classify = ["CUSTOM", f'ENTRY POINTS="{base}"']
        else:
            sys.exit("WHAT DO?")

        return classify, self.remove_common_string(
            smallest_process, split_processes, process_count
        )

    def correct_dataframe_names(
        self, df: pl.DataFrame, new_names: list
    ) -> pl.DataFrame:
        """
        Create a mapping of old and new names for col_0
        """
        rename_dict = dict(
            zip(df.get_column(name="name1"), new_names)
        )  # Generate key:value mapping of row names that need replacing
        new_df = df.with_columns(
            pl.col("name1").replace(rename_dict).alias("updated_names")
        )  # Replaces values with a processed list that removed the common prefixes
        return reorder(new_df.drop("name1"), 0, "updated_names").rename(
            {"updated_names": "names"}
        )  # Reorder columns and rename col_0 back to names

    def add_column_description(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Add a new column including a simple description of col_0
        W = workflow
        S = subworkflow
        P = process
        """
        new_df = df.with_columns(
            pl.when(pl.col("names").str.split(":").list.len() == 1)
            .then(pl.lit("P"))
            .when(pl.col("names").str.split(":").list.len() == 2)
            .then(pl.lit("WP"))
            .when(pl.col("names").str.split(":").list.len() == 3)
            .then(pl.lit("WSP"))
            .when(pl.col("names").str.split(":").list.len() == 4)
            .then(pl.lit("WSSP"))
            .otherwise(pl.lit("TooManyNests"))
            .alias("description")
        )
        return reorder(new_df, 1, "description")
