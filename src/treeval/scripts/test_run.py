import os
import polars as pl

from parse_run import RunParser
from condense_data import ExecutionCondenser

folder = '/nfs/treeoflife-01/teams/tola/users/dp24/SummaryStats/tests/test_data/'


base_df = []

for file in os.listdir(folder):

    data = RunParser( f'{folder}{file}')
    if 'TreeValProject.Summary' in data.data_type:
        print('Thanks for Choosing TreeValProject.Summary for your input context data')
        # I should add an IngestContext() which is also activated by flag
        # Adds the data I capture from the treevalproject.summary module
        # Would require a ESCondenser (which extended use of ExecutionCondenser to deal with the extra data.

    base_df.append(data.execution.data_frame)


pl.concat(base_df)

all = ExecutionCondenser(new_df)
print(all.condenser('total'))