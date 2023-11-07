# SummaryStats

For the TreeVal project, we have included a TreeValProject.summary function in groovy. This collects some specifically made channels into an output file merged with the execution logs.

The scripts contained in this repo `src/` aim to pull actionable data from these files.

Requirements:
Python >= 3.10
pandas
plotly
statsmodels


Run the script with:
```
python3 src/treeval/scripts/ProjectStats.py {PATH TO SUMMARY DIRECTORY}
```

Current Example:
```
python3 src/treeval/scripts/ProjectStats.py ./treeval-summary-files/1-1-0/
```

Current Example Output:
```
--------------------------------------------------
 TreeValProject.Summary Stats!
--------------------------------------------------
 Total data points: 235 
--------------------------------------------------
 Unique CLADE count:
Clade
insects                160
dicots                  16
fungi                   12
fish                    11
nematode                 9
mammals                  8
bird                     3
sponges                  2
non-vascular-plants      2
mollusc                  2
platyhelminths           2
other-animal-phyla       1
Annelida                 1
jellyfish                1
protists                 1
reptile                  1
protist                  1
other_arthropoda         1
chordates                1
Name: count, dtype: int64
--------------------------------------------------
 Run Type Count:
Entry_Point
RAPID    198
FULL      37
Name: count, dtype: int64
--------------------------------------------------
 Ticket Type Count:
Ticket
DTOL    197
VGP      25
ASG       7
TOL       6
Name: count, dtype: int64
--------------------------------------------------
 Empty Files!:
TreeVal_run_ilMalNeus2_1_FULL_2023-10-25_18-58-23.txt
--------------------------------------------------
```

TODO:
- Include options to add the co2footprint data to the information. Must be optional as not everyone will run it.
- Write the execution class for execution log data.
- Output graphs summarising the stats.