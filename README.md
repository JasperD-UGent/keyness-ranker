# keyness-ranker
This module allows you to rank items in a study corpus according to their keyness (compared to a reference corpus). The keyness ranker takes 3-tuples consisting of a token, part-of-speech tag and lemma as input, meaning that you need to have your corpora tokenised, part-of-speech tagged an lemmatised beforehand. The tuples can be introduced into the keyness ranker as CSV or TSV files (one line per tuple; one file = one corpus document; one folder of files = one subcorpus). The study and reference corpora are assembled based on the subcorpora (if your study/reference corpus consists of just a single subcorpus, you can just assign it this one subcorpus). Below you can find a concrete usage example and an overview of the main steps performed by the underlying script.


**NOTE**: the example corpus used for the CSV/TSV input type is included in the <code>exampleCorpora</code> folder of this GitHub repository. This dummy corpus was created based on the [UD Spanish AnCora treebank](https://universaldependencies.org/treebanks/es_ancora/index.html). The treebank sentences were randomly divided over six documents, which were, at their turn, equally divided over three subcorpora (one subcorpora for the study corpus, and two for the reference corpus). The corpus adheres to the required folder structure: <code>corpus_folder/subcorpus_folders/document_files</code>.

## Usage example
### Input
The usage example is presented in the <code>keynessRanker_example.py</code> file. It contains a usage example for CSV/TSV files as input type. The <code>init_keyness_ranker</code> function used to perform the keyness ranking only requires three arguments, namely the path to the folder containing the corpora (passed to the first-position <code>path_to_direc_corpora</code> argument), a tuple containing the names of the subcorpora which constitute the study corpus (passed to the second-position <code>subcorpora_sc</code> argument) and a tuple containing the names of the subcorpora which constitute the reference corpus (passed to the third-position <code>subcorpora_rc</code> argument). To learn more about all the possible other arguments which can be passed to the <code>init_keyness_ranker</code> function, have a look at the [source code](https://github.com/JasperD-UGent/keyness-ranker/blob/main/keynessRanker_example_defs.py).
```python
def main():
    path_to_direc_corpora = os.path.join("exampleCorpora")
    subcorpora_sc = ("subcorpus1",)
    subcorpora_rc = ("subcorpus2", "subcorpus3")

    init_keyness_ranker(
        path_to_direc_corpora,
        subcorpora_sc,
        subcorpora_rc
    )
```

### Output
The output of intermediary steps (frequency dictionaries \[per item and totals] and dispersion values) are saved per corpus into an automatically created <code>prep</code> folder. The final results are stored in the automatically created <code>output</code> folder, in a subdirectory named <code>[study_corpus]\_VS_[reference_corpus]</code>. The following output files are created:
- Per "study corpus subcorpus - reference corpus" combination, an Excel file containing the keyness ranking results. Ranking scores have a theoretical range from 100 (highest possible ranking) to approximately 0 (lowest possible ranking) and are averaged out across the subcorpora of the reference corpus.
- An Excel file containing the final overview of the results for the study corpus. If the study corpus contains more than one subcorpus, the final ranking scores correspond to the averages of the "study corpus as a whole - reference corpus" comparison and each individual "study corpus subcorpus - reference corpus" comparison (which can all be consulted in the corresponding Excel files, as explained above).

## Method
### Step_1
Perform keyness calculation (see [keyness-calculator](https://github.com/JasperD-UGent/keyness-calculator)).

### Step_2
Make a normalised keyness ranking. Only statistically significant keyness values are taken into consideration, and the final ranking is an average of all possible study corpus (both as a whole and for each individual subcorpus) - reference corpus comparisons (both as a whole and for each individual subcorpus).

## Required Python modules
The keyness ranker uses the Python modules mentioned below, so you need to have them installed for the script to work.
- [numpy](https://pypi.org/project/numpy/) (~=1.18.2)
- [Xlsxwriter](https://pypi.org/project/XlsxWriter/) (~=1.2.8)
