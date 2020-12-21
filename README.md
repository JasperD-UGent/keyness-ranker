# keyness-ranker
This module allows you to rank items in a study corpus according to their keyness (compared to a reference corpus). The keyness ranker takes 3-tuples consisting of a token, part-of-speech tag and lemma as input, meaning that you need to have your corpora tokenised, part-of-speech tagged an lemmatised beforehand. The tuples can be introduced into the keyness calculator as CSV or TSV files (one line per tuple; one file = one corpus document; one folder of files = one subcorpus; one folder of subcorpora = one corpus). Below you can find a concrete usage example and an overview of the main steps performed by the underlying script.


**NOTE**: the example corpus used for the CSV/TSV input type is included in the <code>exampleCorpora</code> folder of this GitHub repository. This dummy corpus was created based on the [UD Spanish AnCora treebank](https://universaldependencies.org/treebanks/es_ancora/index.html). The treebank sentences were randomly divided over six documents, which were, at their turn, equally divided over three subcorpora (one subcorpora for the study corpus, and two for the reference corpus). The corpus adheres to the required folder structure: <code>corpus_folder/subcorpus_folders/document_files</code>.
## Usage example
### Input
The usage example is presented in the <code>keynessRanker_example.py</code> file. It contains a usage example for CSV/TSV files as input type. The <code>init_keyness_ranker</code> function used to perform the keyness ranking only requires three arguments, namely the path to the folder containing the corpora (passed to the first-position <code>path_to_direc_corpora</code> argument), a tuple containing the names of the subcorpora which constitute the study corpus (passed to the second-position <code>subcorpora_sc</code> argument) and a tuple containing the names of the subcorpora which constitute the reference corpus (passed to the third-position <code>subcorpora_rc</code> argument). To learn more about all the possible other arguments which can be passed to the <code>init_keyness_ranker</code> function, have a look at the [source code](https://github.com/JasperD-UGent/keyness-ranker/blob/main/utils.py).
## Required Python modules
The keyness calculator uses the Python modules mentioned below, so you need to have them installed for the script to work.
- [numpy](https://pypi.org/project/numpy/)
- [Xlsxwriter](https://pypi.org/project/XlsxWriter/)
## References
- Everitt, B.S. (2002). The Cambridge Dictionary of Statistics (2nd ed.). Cambridge University Press
- Gabrielatos, C. (2018). Keyness Analysis: nature, metrics and techniques. In C. Taylor & A. Marchi (Eds.), Corpus Approaches to Discourse: A Critical Review. Routledge.
- Gabrielatos, C., & Marchi, A. (2011). Keyness Matching metrics to definitions. November, 1–28.
- Gries, S. T. (2008). Dispersions and adjusted frequencies in corpora. International Journal of Corpus Linguistics, 13(4), 403–437. https://doi.org/10.1075/ijcl.13.4.02gri
- Hardie, A. (2014). Log Ratio - an informal introduction. http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/
- Hofland, K., & Johansson, S. (1982). Word Frequencies in British and American English. Longman.
- Kilgarriff, A. (2009). Simple maths for keywords. In M. Mahlberg, V. González-Díaz & C. Smith (Eds.), Proceedings of the Corpus Linguistics Conference, CL2009. University of Liverpool
- Lijffijt, J., & Gries, S. T. (2012). Review of ((2008)): International Journal of Corpus Linguistics. International Journal of Corpus Linguistics, 17(1), 147–149. https://doi.org/10.1075/ijcl.17.1.08lij
- Pojanapunya, P., & Watson Todd, R. (2016). Log-likelihood and odds ratio: Keyness statistics for different purposes of keyword analysis. Corpus Linguistics and Linguistic Theory.
- Wilson, A. (2013). Embracing Bayes factors for key item analysis in corpus linguistics. In M. Bieswanger & A. Koll-Stobbe (Eds.), New Approaches to the Study of Linguistic Variability (pp. 3–11). Peter Lang.
