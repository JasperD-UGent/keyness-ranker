# keyness-ranker
This module allows you to rank items in a study corpus (SC) according to their keyness compared to a reference corpus (RC). The keyness ranker takes 3-tuples consisting of a token, part-of-speech tag and lemma as input, meaning that you need to have your corpora tokenised, part-of-speech tagged and lemmatised beforehand. The tuples can be introduced into the keyness ranker as CSV or TSV files (one line per tuple; one file = one corpus document; one folder of files = one subcorpus). Below you can find a concrete usage example and an overview of the main steps performed by the underlying script.

The keyness ranker is an extension on the [keyness-calculator](https://github.com/JasperD-UGent/keyness-calculator), which determines one single keyness score for all words in an SC (which can but not has to contain multiple subcorpora) compared to an RC (which can but not has to contain multiple subcorpora). In the keyness calculator, the final calculations are based on one single (frequency) value for the SC and one single (frequency) value for the RC, even if the SC and/or RC consisted of multiple subcorpora (although it should be added that by using adjusted frequencies the distribution of words in the subcorpora can, to a certain extent, be taken into account).

The keyness ranker aims to address this limitation by offering an alternative way of comparing an SC (which can but not has to contain multiple subcorpora) to an RC (which should consist of multiple subcorpora for the keyness analysis to make sense). By considering each subcorpus (both in the SC and the RC) as an independent reference point and calculating a keyness ranking for each possible combination of reference points, a fine-grained keyness analysis can be performed. For example, the keyness ranker could be used to compare, say, an economic SC (consisting of a written and spoken subcorpus) to a series of other specialised corpora (on health, law, tourism, etc.). The output offered by the keyness ranker will then enable you to, among other things, identify the words which are ranked among the top key items in all different corpus comparisons, or identify the words which are key to only one of the SC subcorpora.

**NOTE**: the example corpora used for the CSV/TSV input type are included in the <code>exampleCorpora</code> folder of this GitHub repository. The corpora were created based on the [UD Spanish GSD treebank](https://universaldependencies.org/treebanks/es_gsd/index.html) and the [UD Spanish AnCora treebank](https://universaldependencies.org/treebanks/es_ancora/index.html). The treebank sentences were, per treebank, randomly divided over separate documents: the GSD treebank over four documents, the AnCora treebank over six. These documents were then used to create subcorpora: the four GSD documents were converted into two subcorpora (each containing two documents), the six AnCora documents into three subcorpora (each containing two documents). The corpora are stored according to the following folder structure: <code>corpus_folder/subcorpus_folders/document_files</code>. It should be noted, though, that these corpora have been created to allow trying out the script, not to yield results on which a meaningful keyness analysis can be carried out. In fact, although their contents are slightly different (the GSD treebank includes data from blogs, news, reviews, and Wikipedia; AnCora only includes news data), both treebanks mainly contain rather general language, a scenario which will unlikely lead to very meaningful keyness results.

## Usage example
### Input
The usage example is presented in the <code>keynessRanker_example.py</code> file. It contains a usage example for CSV/TSV files as input type. The <code>init_keyness_ranker</code> function used to perform the keyness ranking only requires two arguments, namely a dictionary containing the necessary information for the SC (name and list of paths to subcorpora; passed to the first-position `d_sc` argument) and a dictionary containing the exact same information for the RC (passed to the second-position `d_rc` argument). To learn more about all the possible other arguments which can be passed to the <code>init_keyness_ranker</code> function, have a look at the [source code](https://github.com/JasperD-UGent/keyness-ranker/blob/main/keynessRanker_example_defs.py).
```python
def main():
    # define support variables
    path_to_direc_corpora = os.path.join("exampleCorpora")
    name_sc = "UD_Spanish-GSD"
    name_rc = "UD_Spanish-AnCora"

    # define variables to be passed into function
    d_sc = {
        "name": name_sc,
        "subcorpora": [os.path.join(path_to_direc_corpora, name_sc, "GSD_subcorpus1"),
                       os.path.join(path_to_direc_corpora, name_sc, "GSD_subcorpus2")]
    }
    d_rc = {
        "name": name_rc,
        "subcorpora": [os.path.join(path_to_direc_corpora, name_rc, "AnCora_subcorpus1"),
                       os.path.join(path_to_direc_corpora, name_rc, "AnCora_subcorpus3")]
    }

    # call function
    init_keyness_ranker(
        d_sc,
        d_rc
    )
```

### Output
The output of intermediary steps (frequency dictionaries \[per item and totals] and dispersion values) are saved per corpus into an automatically created <code>prep</code> folder. The final results are stored in the automatically created <code>output</code> folder, in a subdirectory named <code>\[study_corpus]\_VS_\[reference_corpus]</code>. The following output files are created:
- Per "SC subcorpus - RC" combination, an Excel file containing the keyness ranking results. Ranking scores have a theoretical range from 100 (highest possible ranking) to approximately 0 (lowest possible ranking) and are averaged out across the subcorpora of the RC.
- An Excel file containing the final overview of the results for the SC. If the SC contains more than one subcorpus, the final ranking scores correspond to the averages of the "SC as a whole - RC" comparison and each individual "SC subcorpus - RC" comparison (which can all be consulted in the corresponding Excel files, as explained above).

## Method
### Step_1
Convert corpora into frequency dictionaries (see [keyness-calculator](https://github.com/JasperD-UGent/keyness-calculator)).

### Step_2
Apply dispersion metric, calculate adjusted frequencies and update frequency dictionaries (see [keyness-calculator](https://github.com/JasperD-UGent/keyness-calculator)).

### Step_3
Calculate the keyness values (see [keyness-calculator](https://github.com/JasperD-UGent/keyness-calculator)) and make a normalised keyness ranking. Only statistically significant keyness values are taken into consideration, and the final ranking is an average of all possible SC (both as a whole and for each individual subcorpus) - RC comparisons (both as a whole and for each individual subcorpus).

### Step_4
1. Construct meta file containing the information of the last query.
2. Save this meta file into the <code>prep</code> folder (when the keyness ranker is initialised, it first checks this meta file, and when the query criteria are identical, the ranker will immediately load the intermediate output for the corpus in question in the <code>prep</code> folder, instead of again calculating the frequencies from scratch).

## Required Python modules
The keyness ranker uses the Python modules mentioned below, so you need to have them installed for the script to work.
- [numpy](https://pypi.org/project/numpy/) (~=1.18.2)
- [Xlsxwriter](https://pypi.org/project/XlsxWriter/) (~=1.2.8)
