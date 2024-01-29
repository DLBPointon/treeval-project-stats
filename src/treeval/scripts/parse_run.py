# Public Libraries
import re
import io
import re
import polars as pl
from itertools import count

# Classes for Project
from parse_input_data import ParseInputData
from parse_run_data import ParseRunData
from parse_execution import ParseExecution
from parse_co2_data import ParseCo2Data
from general_functions import get_contents


class RunParser:
    _instance_counter = count(0)

    def __init__(self, file: str, co2: str = ""):
        self.counter = next(self._instance_counter)
        self.file = file

        file_contents = get_contents(self)
        if file_contents[0].startswith("---RUN_DATA---\n"):
            run_index = file_contents.index("---RUN_DATA---\n")
            input_index = file_contents.index("---INPUT_DATA---\n")
            execution_index = file_contents.index("---RESOURCES---\n")

            data_type = ["EXECUTION LONG", "TreeValProject.Summary"]
            self.run_data = ParseRunData(file_contents[run_index + 1 : input_index])
            self.input_data = ParseInputData(
                file_contents[input_index + 1 : execution_index]
            )
            self.execution = ParseExecution(file_contents[execution_index + 1 :], file)
        else:
            data_type = ["EXECUTION LOG ONLY"]
            self.execution = ParseExecution(file_contents, file)

        if co2 != "":
            data_type = self.data_type.append("CO2 DATA")
            co2_contents = get_contents(co2)
            self.co2_data = ParseCo2Data(co2_contents)

        self.data_type = " + ".join(data_type + self.execution.classification)
        self.collection = self.__iter__()

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [
            txt.write(f"\t{a} = '{v}' \n")
            for a, v in self.collection
            if a not in ["block", "collection", "contents"]
        ]
        txt.write(")")
        return txt.getvalue()

    def __str__(self):
        txt = io.StringIO()
        txt.write(f"{self.__class__.__name__}(\n")
        [
            txt.write(f"\t{a} = '{v}' \n")
            for a, v in self.collection
            if a not in ["block", "collection", "contents"]
        ]
        txt.write(")")
        return txt.getvalue()

    def correct_data_casts(self) -> pl.DataFrame:
        """
        Due to the amount of data now being taken in,
        there are times where the casting (data type of the column) not being correct
        This causes significant issues with Merging multiple frames as
        Example: polars.exceptions.SchemaError: cannot extend/append Int64 with Int32

        For now this deals with the usually buggy ones.
        """
        self.execution.data_frame = self.execution.data_frame.with_columns(
            [
                pl.col("input_genome").cast(pl.Int64),
                pl.col("cram_containers").cast(pl.Float64),
                pl.col("cram_file_no").cast(pl.Int32),
                pl.col("cram_total").cast(pl.Int64),
                pl.col("pacbio_file_no").cast(pl.Int32),
                pl.col("pipeline_time").cast(pl.Int64),
                pl.col("pacbio_total").cast(pl.Int64),
            ]
        )
        #print(self.execution.data_frame.dtypes)
        return self

    def inject_context(self):
        """
        If there is valid treevalproject.summary data then inject it into the dataframe so that
        we can run more analysis! Also casts to a particular datatype.
        More Analysis == More Graphs!
        """
        self.execution.data_frame = self.execution.data_frame.with_columns(
            clade=pl.lit(self.input_data.get_tol_prefix),
            unique_name=pl.lit(f"{self.run_data.run_name}-{self.run_data.run_id}"),
            input_genome=pl.lit(self.input_data.genome_size.get("file_size_total")),
            entry_point=pl.lit(self.run_data.entry_point),
            pipeline_time=pl.lit(self.run_data.pipeline_seconds),
            pacbio_total=pl.lit(
                self.input_data.pacbio_data.get("file_size_total")),
            pacbio_file_no=pl.lit(self.input_data.pacbio_data.get("file_count")),
            cram_total=pl.lit(self.input_data.cram_data.get("file_size_total")),
            cram_file_no=pl.lit(self.input_data.cram_data.get("file_count")),
            cram_containers=pl.lit(self.input_data.cram_data.get("containers"))
        )

        return self.correct_data_casts()

    def inject_co2(self):
        pass
