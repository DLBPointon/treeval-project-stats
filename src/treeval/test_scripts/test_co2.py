from parse_co2 import Co2Parser

file = "/nfs/treeoflife-01/teams/tola/users/dp24/SummaryStats/treeval-summary-files/1-1-0-co2/bAnaBra1_1-co2footprint.txt"

data = Co2Parser(file)
print(data.max_data)
