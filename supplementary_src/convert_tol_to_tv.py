import os
import sys

folder = '/nfs/treeoflife-01/teams/tola/users/dp24/SummaryStats/treeval-summary-files/readmapping/'

counter = 0


for file in os.listdir(folder):
    data = []
    counter += 1

    print(file + str(counter))

    if os.stat(folder + file).st_size == 0:
        pass
    else:
        with open (f'{folder}{file}', 'r') as datafile:
            collection = [i.split('\t') for i in datafile.readlines()]
            for i in collection:

                if i[0] == 'task_id':
                    print(i)
                    head_line = ['name', i[5], "module", i[7], i[8], i[10], 'realtime', i[-5], i[-4], f'{i[-3]}\n']
                    data.append(head_line)
                else:
                    data_line = [f'{i[3]} ({i[4]})', i[5], '-', i[7], f'{i[8]}', i[10], i[-6], i[-5], i[-4], f'{i[-3]}\n']
                    data.append(data_line)

        with open(f'/nfs/treeoflife-01/teams/tola/users/dp24/SummaryStats/treeval-summary-files/readmapping modified/execution_log_coverted-{counter}.txt', 'w') as new_file:
            for i in data:
                new_file.write('\t'.join(i))

