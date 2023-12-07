import io
import polars as pl

class ParseExecution:

    def __init__(self, contents: list):
        self.headers            = contents[0].strip().split('\t')
        self.unique_processes   = self.generate_dataframe(contents)

        self.collection         = self.__iter__()


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

        txt.write(f"\t)")
        return txt.getvalue()


    def generate_dataframe(self, data: list) -> pl.DataFrame:
        split_data = [i.split('\t') for i in data]

        # column_0 would be retained as row_1 after transpose, so removed here
        df = pl.DataFrame(split_data).drop('column_0').transpose(include_header=False, column_names = self.headers)


        print(df)