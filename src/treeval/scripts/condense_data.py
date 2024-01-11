import io
import sys
import polars as pl
from general_functions import reorder

class ExecutionCondenser:

    def __init__(self, df: pl.DataFrame) -> pl.DataFrame:
        self.all_df             = df
        self.unique_processes   = set(self.all_df.get_column(name='names'))

        self.collection         = self.__iter__()


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


    def condense_subset_df(self, subsetter: str) -> pl.DataFrame:
        temp_df = self.all_df.filter((pl.col('names') == subsetter) & (pl.col('status') != 'FAILED'))
        return temp_df


    def get_all_run_average(self, lof:list, extended: bool) -> pl.DataFrame:
        """
        Input is a list of subset dataframes (per process)
        each dataframe is averaged and then all are glued together
        Creates a dataframe of averaged data per process
        """
        new_list = []
        for i in lof:
            data = i[0].row(0)[:3] # Grabs some data from the chunk(this is the same for all rows in chunk)
            data_rear = i[0].row(0)[13:]
            computed = (
                i.select(pl.mean(
                [
                    'cpus_requested', 'memory_requested_mb', 'attempt',
                    'realtime_seconds', 'percent_cpu', 'average_memory_used_as_percentage',
                    'peak_memory_mb', 'cpu_used', 'average_memory_used_as_mb', 'peak_memory_as_percentage'
                ]))
            )

            add_context = computed.with_columns(
                names = pl.lit(data[0]),
                desc = pl.lit(data[1]),
                status = pl.lit(data[2]),
                clade = pl.lit(data_rear[0]),
                unique_name = pl.lit(data_rear[1]),
                genome_size = pl.lit(data_rear[2]),
                entry_point = pl.lit(data_rear[3]),
                pipeline_time = pl.lit(data_rear[4]),
                pacbio_total = pl.lit(data_rear[5]),
                pacbio_file_no = pl.lit(data_rear[6]),
                cram_total = pl.lit(data_rear[7]),
                cram_file_no = pl.lit(data_rear[8]),
                cram_containers = pl.lit(data_rear[9]).cast(pl.Int32) # Otherwise 0 == NaN
            )
            new_df = reorder(add_context, 0, 'names')
            new_list.append(new_df)
        return pl.concat(new_list)


    def get_all_run_total(self, lof:list, extended: bool) -> pl.DataFrame:
        """
        Input is a list of subset dataframes (per process)
        each dataframe is averaged and then all are glued together
        Creates a dataframe of averaged data per process
        """
        new_list = []
        for i in lof:
            data = i[0].row(0)[:3] # Grabs some data from the chunk(this is the same for all rows in chunk)

            computed = (
                i.select(pl.sum(
                [
                    'cpus_requested', 'memory_requested_mb', 'attempt',
                    'realtime_seconds', 'percent_cpu', 'average_memory_used_as_percentage',
                    'peak_memory_mb', 'cpu_used', 'average_memory_used_as_mb'
                ]))
            )

            add_context = computed.with_columns(names = pl.lit(data[0]), desc=pl.lit(data[1]), status=pl.lit(data[2]) )
            new_df = reorder(add_context, 0, 'names')
            new_list.append(new_df)
        return pl.concat(new_list)


    def condenser(self, df: str = 'avg', extended: bool = False) -> pl.DataFrame:
        """
        These functions should be simplified to one of those
        pass a function as an argument, that way two methods become one.
        """

        list_of_frames = [self.condense_subset_df(i) for i in self.unique_processes]
        match df:
            case 'avg':
                return self.get_all_run_average(list_of_frames, extended)
            case 'total':
                return self.get_all_run_total(list_of_frames, extended)
            case 'minmax':
                sys.exit('Not implemented yet')
            case _:
                sys.exit("Don't know that one, only use [avg, total, minmax]")

