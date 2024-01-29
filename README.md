# SummaryStats (v2)

For the TreeVal project, we have included a TreeValProject.summary function in groovy. This collects some specifically made channels into an output file merged with the execution logs.

The scripts contained in this repo `src/` aim to pull actionable data from these files.

## Requirements

Requirements can be seen in the requirements.txt file found in this folder.

These can be installed with:

```
python -m venv .env
source .env/bin/activate
python3 -m pip install -r requirements.txt
```

You can deactivate the environment with a simple

```
deactivate
```

and reactivate with the `source` command used above.

## Run the script

Run the script with:

```
python3 src/treeval/scripts/SummaryStats.py {PATH TO SUMMARY DIRECTORY}
```

Current Example:

```
python3 src/treeval/scripts/SummaryStats.py ./treeval-summary-files/1-1-0/

python3 src/treeval/scripts/SummaryStats.py /lustre/scratch123/tol/resources/treeval/treeval_stats/release-1-0-0/
```

## Example

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

- Make TreeValProject.Summary input data optional
- Output graphs summarising the stats. (Done for 80% of mem cases, issues with subworkflows inside subworkflows)
