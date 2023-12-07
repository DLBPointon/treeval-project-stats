import os

from parse_run import RunParser

folder = '/nfs/treeoflife-01/teams/tola/users/dp24/SummaryStats/tests/test_data/'

for file in os.listdir(folder):

    data = RunParser( f'{folder}{file}')
    print(data)