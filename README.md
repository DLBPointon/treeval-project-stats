# SummaryStats (v2)

For the TreeVal project, we have included a TreeValProject.summary function in groovy. This collects some specifically made channels into an output file merged with the execution logs.

The scripts contained in this repo `src/` aim to pull actionable data from these files.

## Requirements

Requirements can be seen in the requirements.txt file found in this folder.

These can be installed with:

```bash
python -m venv .env
source .env/bin/activate
python3 -m pip install -r requirements.txt
```

You can deactivate the environment with a simple

```bash
deactivate
```

and reactivate with the `source` command used above.

## Run the script

Run the script with:

```bash
python3 src/treeval/scripts/SummaryStats.py {PATH TO SUMMARY DIRECTORY}
```

Current Example:

```bash
python3 src/treeval/scripts/SummaryStats.py ./treeval-summary-files/1-1-0/

python3 src/treeval/scripts/SummaryStats.py /lustre/scratch123/tol/resources/treeval/treeval_stats/release-1-0-0/
```

## Repo Explainer

- output StatGraphsV2
  - Examples of the current output from SummaryStats V2
- src
  - accessory_scripts
    - A script used to convert the data in readmapping into that usable for SummaryStats, this is due to the different columns used in each team
  - legacy_scripts
    - files which have not yet been ported to V2, or contain code that is kept for posterity for now.
  - test_scripts
    - Scripts used to test individual classes and code
    - This should really be done by Unit tests
  - scripts
    - Contains the actual code for SummaryStats split into multiple classes for each input data type
- test-data
  - 1-0-0-runs
    - TV-enhanced runs of the TreeVal V1.0.0 pipeline
  - 1-1-0-runs
    - TV-enhanced runs of the TreeVal V1.0.0 pipeline
  - 1-1-0-co2
    - Respective co2 files of a subset of files in the above folder (script willl have to deal with this)
  - genomenote
    - output from another pipeline in ToL - plain trace files - may need re-headering
  - readmapping
    - output from another pipeline in ToL - plain trace files - re-headered in `readmapping modified`
  - readmapping modified
    - re-headered output from readmapping
  - mixed_data
    - a small folder of mixed data - should always kill the pipeline if there are mixed basic/enhanced data
    - SHOULD MAKE THIS A FLAG SO IF THERE IS A MIX THEN IGNORE ENHANCED DATA
  - efficiency_graphs
    - Graphs showing the relative efficiency of all runs
    - This needs porting to V2
  - requirements.txt
    - List of installable libraries for SummatyStats

## Example

```markdown
---

## TreeValProject.Summary Stats!

## Total data points: 235

Unique CLADE count:
Clade
insects 160
dicots 16
fungi 12
fish 11
nematode 9
mammals 8
bird 3
sponges 2
non-vascular-plants 2
mollusc 2
platyhelminths 2
other-animal-phyla 1
Annelida 1
jellyfish 1
protists 1
reptile 1
protist 1
other_arthropoda 1
chordates 1
Name: count, dtype: int64

---

Run Type Count:
Entry_Point
RAPID 198
FULL 37
Name: count, dtype: int64

---

Ticket Type Count:
Ticket
DTOL 197
VGP 25
ASG 7
TOL 6
Name: count, dtype: int64

---

Empty Files!:
TreeVal_run_ilMalNeus2_1_FULL_2023-10-25_18-58-23.txt

---
```

TODO:

- Make TreeValProject.Summary input data optional
- Output graphs summarising the stats. (Done for 80% of mem cases, issues with subworkflows inside subworkflows)

Full Dataframe will contain data on:

```markdown
['names', 'cpus_requested', 'memory_requested_mb', 'attempt', 'realtime_seconds', 'percent_cpu', 'average_memory_used_as_percentage', 'peak_memory_mb', 'cpu_used', 'average_memory_used_as_mb', 'peak_memory_as_percentage', 'desc', 'status', 'clade', 'unique_name', 'genome_size', 'entry_point', 'pipeline_time', 'pacbio_total', 'pacbio_file_no', 'cram_total', 'cram_file_no', 'cram_containers']
```
