import os

from parse_run_execution2 import RunExecution

folder = '/nfs/treeoflife-01/teams/tola/users/dp24/SummaryStats/tests/test_data/'

for file in os.listdir(folder):

    data = RunExecution(f'{folder}{file}')
    print(data)