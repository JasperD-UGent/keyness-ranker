from utils.STEP_1 import corpora_to_d_freq
from utils.STEP_2 import dispersion
from utils.STEP_3 import keyness
from utils.STEP_4 import meta
from utils.keynessRanker_support import check_meta
from utils.process_JSONs import load_json, load_json_str_to_obj
from utils.write_output import results_to_xlsx_per_sc, results_to_xlsx_overview
from collections import OrderedDict
import os
import sys
from typing import Dict, Optional, Tuple


def init_keyness_ranker(
        path_to_direc_corpora: str,
        subcorpora_sc: Tuple,
        subcorpora_rc: Tuple,
        *,
        input_type_sc: str = "3-column_delimited",
        input_type_rc: str = "3-column_delimited",
        maintain_subcorpora_sc: bool = True,
        maintain_subcorpora_rc: bool = True,
        mapping_custom_to_ud: Optional[Dict] = None,
        mapping_ud_to_custom: Optional[Dict] = None,
        desired_pos: Tuple = ("NOUN", "ADJ", "VERB", "ADV"),
        lemma_or_token: str = "lemma",
        divide_number_docs_by: int = 10,
        number_iterations_merge_subcorpora: int = 1,
        approximation: float = 0.000000000000000001,
        statistical_significance_threshold_bic: int = 2,
        degrees_of_freedom: int = 1,
        frequency_type: str = "adj_freq_Lapl",
        keyness_metric: str = "LogRatio",
        ranking_threshold: float = 0.5,
) -> None:
    """Initialise the keyness ranker.
    :param path_to_direc_corpora: path to the folder where the subcorpora are located.
    :param subcorpora_sc: a tuple containing the (folder) names of the subcorpora which constitute the study corpus.
    :param subcorpora_rc: a tuple containing the (folder) names of the subcorpora which constitute the reference corpus.
    :param input_type_sc: data type of the study corpus documents. Defaults to "3-column_delimited" for CSV/TSV files
        (which is currently also the only recognised data type).
    :param input_type_rc: data type of the reference corpus documents. Defaults to "3-column_delimited" for CSV/TSV
        files (which is currently also the only recognised data type).
    :param maintain_subcorpora_sc: when working with adjusted frequencies, boolean value which defines whether
        dispersion is based on existing subcorpora of the study corpus, or whether all documents are merged and randomly
        split into new subcorpora. Defaults to True.
    :param maintain_subcorpora_rc: when working with adjusted frequencies, boolean value which defines whether
        dispersion is based on existing subcorpora of the reference corpus, or whether all documents are merged and
        randomly split into new subcorpora. Defaults to True.
    :param mapping_custom_to_ud: if you work with custom POS tags, dictionary which maps custom tags to UD counterparts.
    :param mapping_ud_to_custom: if you work with custom POS tags, dictionary which maps UD tags to custom counterparts.
    :param desired_pos: tuple of UD tags which should be taken into account in the keyness calculations.
        Defaults to ("NOUN", "ADJ", "VERB", "ADV").
    :param lemma_or_token: defines whether to calculate frequencies on token or lemma level. Choose between: "lemma",
        "token". Defaults to "lemma".
    :param divide_number_docs_by: when working with adjusted frequencies, number by which the total number of documents
        is divided to arrive at the number of new randomly generated subcorpora. Defaults to 10.
    :param number_iterations_merge_subcorpora: when working with adjusted frequencies, number of times the subcorpora
        are randomly shuffled to generate new subcorpora (and, thus, also new dispersion values). This will lead to
        (slightly) different keyness values (and rankings), which are averaged out in the end. Defaults to 1.
    :param approximation: float by which zero frequencies are approximated. Defaults to 0.000000000000000001.
    :param statistical_significance_threshold_bic: statistical significance threshold for BIC values. Defaults to 2
        (see also Gabrielatos [2018] and Wilson [2013]).
    :param degrees_of_freedom: degrees of freedom used to calculate log likelihood values. Defaults to 1 (which is
        the default number of degrees of freedom for keyness calculations).
    :param frequency_type: frequency type based on which keyness values are calculated. Choose between: "abs_freq"
        (absolute frequency), "adj_freq" (adjusted frequency), "abs_freq_Lapl" (absolute frequency + Laplace smoothing),
        "adj_freq_Lapl" (adjusted frequency + Laplace smoothing). Defaults to "adj_freq_Lapl".
    :param keyness_metric: keyness metric used to perform the keyness calculations. Choose between: "DIFF" (Gabrielatos
        & Marchi, 2011), "Ratio" (Kilgarriff, 2009), "OddsRatio" (Everitt, 2002; Pojanapunya & Watson Todd, 2016),
        "LogRatio" (Hardie, 2014), "DiffCoefficient" (Hofland & Johansson, 1982). Defaults to "LogRatio".
    :param ranking_threshold: value between 0 and 1 which indicates in how many percent of the study corpus subcorpora -
        reference corpus subcorpora combinations a statistically significant keyness value is required before the item
        can enter into the keyness ranking. Defaults to 0.5.
    :returns: `None`
    """
    l_pos_tags_ud = [
        "ADJ", "ADV", "INTJ", "NOUN", "PROPN", "VERB", "ADP", "AUX", "CCONJ", "DET", "NUM", "PART", "PRON", "SCONJ",
        "PUNCT", "SYM", "X"
    ]
    mapping_custom_to_ud = {pos: pos for pos in l_pos_tags_ud} if mapping_custom_to_ud is None else mapping_custom_to_ud
    mapping_ud_to_custom = {
        pos: [pos] for pos in l_pos_tags_ud
    } if mapping_ud_to_custom is None else mapping_ud_to_custom
    number_iterations_merge_subcorpora = 1 if maintain_subcorpora_sc and maintain_subcorpora_rc \
        else number_iterations_merge_subcorpora

    d_keyn_overview = OrderedDict()

    if len(subcorpora_sc) > 1:
        d_keyn_per_rc = OrderedDict()
        name_sc = "_".join(subcorpora_sc)
        input_sc = {corpus: os.path.join(path_to_direc_corpora, corpus) for corpus in subcorpora_sc}
        load_from_files_sc = check_meta(
            name_sc, desired_pos, lemma_or_token, maintain_subcorpora_sc, divide_number_docs_by,
            number_iterations_merge_subcorpora
        )

        if load_from_files_sc:
            d_freq_abs_adj_sc = load_json_str_to_obj(os.path.join("prep", name_sc, f"{name_sc}_d_freq_abs_adj.json"))
            l_d_sum_abs_adj_sc = load_json(
                os.path.join("prep", name_sc, f"{name_sc}_sum_words_desired_POS_abs_adj.json")
            )
        else:
            d_freq_sc, l_d_freq_sum_cps_sc = corpora_to_d_freq(
                name_sc, input_type_sc, input_sc, mapping_custom_to_ud, mapping_ud_to_custom, desired_pos,
                lemma_or_token, maintain_subcorpora_sc, divide_number_docs_by, number_iterations_merge_subcorpora
            )
            d_freq_abs_adj_sc, l_d_sum_abs_adj_sc = dispersion(
                name_sc, d_freq_sc, l_d_freq_sum_cps_sc, desired_pos, number_iterations_merge_subcorpora
            )
            meta(
                name_sc, desired_pos, lemma_or_token, maintain_subcorpora_sc, divide_number_docs_by,
                number_iterations_merge_subcorpora
            )

        if len(subcorpora_rc) > 1:
            name_rc = "_".join(subcorpora_rc)
            input_rc = {corpus: os.path.join(path_to_direc_corpora, corpus) for corpus in subcorpora_rc}
            load_from_files_rc = check_meta(
                name_rc, desired_pos, lemma_or_token, maintain_subcorpora_rc, divide_number_docs_by,
                number_iterations_merge_subcorpora
            )

            if load_from_files_rc:
                d_freq_abs_adj_rc = load_json_str_to_obj(
                    os.path.join("prep", name_rc, f"{name_rc}_d_freq_abs_adj.json")
                )
                l_d_sum_abs_adj_rc = load_json(
                    os.path.join("prep", name_rc, f"{name_rc}_sum_words_desired_POS_abs_adj.json")
                )
            else:
                d_freq_rc, l_d_freq_sum_cps_rc = corpora_to_d_freq(
                    name_rc, input_type_rc, input_rc, mapping_custom_to_ud, mapping_ud_to_custom, desired_pos,
                    lemma_or_token, maintain_subcorpora_rc, divide_number_docs_by, number_iterations_merge_subcorpora
                )
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc = dispersion(
                    name_rc, d_freq_rc, l_d_freq_sum_cps_rc, desired_pos, number_iterations_merge_subcorpora
                )
                meta(
                    name_rc, desired_pos, lemma_or_token, maintain_subcorpora_rc, divide_number_docs_by,
                    number_iterations_merge_subcorpora
                )

            l_d_keyn_corpus = keyness(
                approximation, statistical_significance_threshold_bic, degrees_of_freedom, frequency_type,
                keyness_metric, number_iterations_merge_subcorpora, d_freq_abs_adj_sc, l_d_sum_abs_adj_sc,
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc
            )
            d_keyn_per_rc[name_rc] = l_d_keyn_corpus

        for corpus in subcorpora_rc:
            name_rc = corpus
            input_rc = {corpus: os.path.join(path_to_direc_corpora, corpus)}
            load_from_files_rc = check_meta(
                name_rc, desired_pos, lemma_or_token, maintain_subcorpora_rc, divide_number_docs_by,
                number_iterations_merge_subcorpora
            )

            if load_from_files_rc:
                d_freq_abs_adj_rc = load_json_str_to_obj(
                    os.path.join("prep", name_rc, f"{name_rc}_d_freq_abs_adj.json")
                )
                l_d_sum_abs_adj_rc = load_json(
                    os.path.join("prep", name_rc, f"{name_rc}_sum_words_desired_POS_abs_adj.json")
                )
            else:
                d_freq_rc, l_d_freq_sum_cps_rc = corpora_to_d_freq(
                    name_rc, input_type_rc, input_rc, mapping_custom_to_ud, mapping_ud_to_custom, desired_pos,
                    lemma_or_token, maintain_subcorpora_rc, divide_number_docs_by, number_iterations_merge_subcorpora
                )
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc = dispersion(
                    name_rc, d_freq_rc, l_d_freq_sum_cps_rc, desired_pos, number_iterations_merge_subcorpora
                )
                meta(
                    name_rc, desired_pos, lemma_or_token, maintain_subcorpora_rc, divide_number_docs_by,
                    number_iterations_merge_subcorpora
                )

            l_d_keyn_corpus = keyness(
                approximation, statistical_significance_threshold_bic, degrees_of_freedom, frequency_type,
                keyness_metric, number_iterations_merge_subcorpora, d_freq_abs_adj_sc, l_d_sum_abs_adj_sc,
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc
            )
            d_keyn_per_rc[name_rc] = l_d_keyn_corpus

        d_keyn_sc = OrderedDict()

        for corpus in d_keyn_per_rc:

            for iteration in range(number_iterations_merge_subcorpora):

                for tup in d_keyn_per_rc[corpus][iteration]:

                    if tup not in d_keyn_sc:
                        d_keyn_sc[tup] = {}

                        for reference_corpus in d_keyn_per_rc:
                            d_keyn_sc[tup][reference_corpus] = \
                                ["NA" for iteration in range(number_iterations_merge_subcorpora)]

                    d_keyn_sc[tup][corpus][iteration] = d_keyn_per_rc[corpus][iteration][tup]

        l_d_keyn = []

        for tup in d_keyn_sc:
            d_keyn_iters = {}
            sum_ranking_scores = 0
            sum_keyn_scores = 0
            n_rankings = 0

            for corpus in d_keyn_sc[tup]:
                d_keyn_iters[corpus] = d_keyn_sc[tup][corpus]
                sum_ranking_scores_corpus = 0
                sum_keyn_scores_corpus = 0
                n_rankings_corpus = 0

                for item in d_keyn_sc[tup][corpus]:

                    if item != "NA":
                        sum_ranking_scores_corpus += item["ranking_score"]
                        sum_keyn_scores_corpus += item["keyn"]
                        n_rankings_corpus += 1

                if n_rankings_corpus != 0:
                    sum_ranking_scores += sum_ranking_scores_corpus / n_rankings_corpus
                    sum_keyn_scores += sum_keyn_scores_corpus / n_rankings_corpus
                    n_rankings += 1

            l_d_keyn.append({
                "item": tup,
                "d_keyn": d_keyn_iters,
                "ranking_score_avg": sum_ranking_scores / n_rankings,
                "keyness_score_avg": sum_keyn_scores / n_rankings,
                "n_rankings": n_rankings
            })

        sorted_l_d_keyn = sorted(sorted(
            l_d_keyn,
            key=lambda i: i["item"]),
            key=lambda i: i["ranking_score_avg"], reverse=True
        )  # sort key items by 1) ranking_score_avg (descending); 2) pos_lem_or_tok (ascending)
        results_to_xlsx_per_sc(
            subcorpora_sc, subcorpora_rc, name_sc, maintain_subcorpora_sc, maintain_subcorpora_rc, lemma_or_token,
            frequency_type, keyness_metric, ranking_threshold, sorted_l_d_keyn, d_keyn_per_rc
        )
        d_keyn_overview[name_sc] = sorted_l_d_keyn

    for study_corpus in subcorpora_sc:
        name_sc = study_corpus
        d_keyn_per_rc = OrderedDict()
        input_sc = {study_corpus: os.path.join(path_to_direc_corpora, study_corpus)}
        load_from_files_sc = check_meta(
            name_sc, desired_pos, lemma_or_token, maintain_subcorpora_sc, divide_number_docs_by,
            number_iterations_merge_subcorpora
        )

        if load_from_files_sc:
            d_freq_abs_adj_sc = load_json_str_to_obj(os.path.join("prep", name_sc, f"{name_sc}_d_freq_abs_adj.json"))
            l_d_sum_abs_adj_sc = load_json(
                os.path.join("prep", name_sc, f"{name_sc}_sum_words_desired_POS_abs_adj.json")
            )
        else:
            d_freq_sc, l_d_freq_sum_cps_sc = corpora_to_d_freq(
                name_sc, input_type_sc, input_sc, mapping_custom_to_ud, mapping_ud_to_custom, desired_pos,
                lemma_or_token, maintain_subcorpora_sc, divide_number_docs_by, number_iterations_merge_subcorpora
            )
            d_freq_abs_adj_sc, l_d_sum_abs_adj_sc = dispersion(
                name_sc, d_freq_sc, l_d_freq_sum_cps_sc, desired_pos, number_iterations_merge_subcorpora
            )
            meta(
                name_sc, desired_pos, lemma_or_token, maintain_subcorpora_sc, divide_number_docs_by,
                number_iterations_merge_subcorpora
            )

        if len(subcorpora_rc) > 1:
            name_rc = "_".join(subcorpora_rc)
            input_rc = {corpus: os.path.join(path_to_direc_corpora, corpus) for corpus in subcorpora_rc}
            load_from_files_rc = check_meta(
                name_rc, desired_pos, lemma_or_token, maintain_subcorpora_rc, divide_number_docs_by,
                number_iterations_merge_subcorpora
            )

            if load_from_files_rc:
                d_freq_abs_adj_rc = load_json_str_to_obj(
                    os.path.join("prep", name_rc, f"{name_rc}_d_freq_abs_adj.json")
                )
                l_d_sum_abs_adj_rc = load_json(
                    os.path.join("prep", name_rc, f"{name_rc}_sum_words_desired_POS_abs_adj.json")
                )
            else:
                d_freq_rc, l_d_freq_sum_cps_rc = corpora_to_d_freq(
                    name_rc, input_type_rc, input_rc, mapping_custom_to_ud, mapping_ud_to_custom, desired_pos,
                    lemma_or_token, maintain_subcorpora_rc, divide_number_docs_by, number_iterations_merge_subcorpora
                )
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc = dispersion(
                    name_rc, d_freq_rc, l_d_freq_sum_cps_rc, desired_pos, number_iterations_merge_subcorpora
                )
                meta(
                    name_rc, desired_pos, lemma_or_token, maintain_subcorpora_rc, divide_number_docs_by,
                    number_iterations_merge_subcorpora
                )

            l_d_keyn_corpus = keyness(
                approximation, statistical_significance_threshold_bic, degrees_of_freedom, frequency_type,
                keyness_metric, number_iterations_merge_subcorpora, d_freq_abs_adj_sc, l_d_sum_abs_adj_sc,
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc
            )
            d_keyn_per_rc[name_rc] = l_d_keyn_corpus

        for corpus in subcorpora_rc:
            name_rc = corpus
            input_rc = {corpus: os.path.join(path_to_direc_corpora, corpus)}
            load_from_files_rc = check_meta(
                name_rc, desired_pos, lemma_or_token, maintain_subcorpora_rc, divide_number_docs_by,
                number_iterations_merge_subcorpora
            )

            if load_from_files_rc:
                d_freq_abs_adj_rc = load_json_str_to_obj(
                    os.path.join("prep", name_rc, f"{name_rc}_d_freq_abs_adj.json")
                )
                l_d_sum_abs_adj_rc = load_json(
                    os.path.join("prep", name_rc, f"{name_rc}_sum_words_desired_POS_abs_adj.json")
                )
            else:
                d_freq_rc, l_d_freq_sum_cps_rc = corpora_to_d_freq(
                    name_rc, input_type_rc, input_rc, mapping_custom_to_ud, mapping_ud_to_custom, desired_pos,
                    lemma_or_token, maintain_subcorpora_rc, divide_number_docs_by, number_iterations_merge_subcorpora
                )
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc = dispersion(
                    name_rc, d_freq_rc, l_d_freq_sum_cps_rc, desired_pos, number_iterations_merge_subcorpora
                )
                meta(
                    name_rc, desired_pos, lemma_or_token, maintain_subcorpora_rc, divide_number_docs_by,
                    number_iterations_merge_subcorpora
                )

            l_d_keyn_corpus = keyness(
                approximation, statistical_significance_threshold_bic, degrees_of_freedom, frequency_type,
                keyness_metric, number_iterations_merge_subcorpora, d_freq_abs_adj_sc, l_d_sum_abs_adj_sc,
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc
            )
            d_keyn_per_rc[name_rc] = l_d_keyn_corpus

        d_keyn_sc = OrderedDict()

        for corpus in d_keyn_per_rc:

            for iteration in range(number_iterations_merge_subcorpora):

                for tup in d_keyn_per_rc[corpus][iteration]:

                    if tup not in d_keyn_sc:
                        d_keyn_sc[tup] = {}

                        for reference_corpus in d_keyn_per_rc:
                            d_keyn_sc[tup][reference_corpus] = \
                                ["NA" for iteration in range(number_iterations_merge_subcorpora)]

                    d_keyn_sc[tup][corpus][iteration] = d_keyn_per_rc[corpus][iteration][tup]

        l_d_keyn = []

        for tup in d_keyn_sc:
            d_keyn_iters = {}
            sum_ranking_scores = 0
            sum_keyn_scores = 0
            n_rankings = 0

            for corpus in d_keyn_sc[tup]:
                d_keyn_iters[corpus] = d_keyn_sc[tup][corpus]
                sum_ranking_scores_corpus = 0
                sum_keyn_scores_corpus = 0
                n_rankings_corpus = 0

                for item in d_keyn_sc[tup][corpus]:

                    if item != "NA":
                        sum_ranking_scores_corpus += item["ranking_score"]
                        sum_keyn_scores_corpus += item["keyn"]
                        n_rankings_corpus += 1

                if n_rankings_corpus != 0:
                    sum_ranking_scores += sum_ranking_scores_corpus / n_rankings_corpus
                    sum_keyn_scores += sum_keyn_scores_corpus / n_rankings_corpus
                    n_rankings += 1

            l_d_keyn.append({
                "item": tup,
                "d_keyn": d_keyn_iters,
                "ranking_score_avg": sum_ranking_scores / n_rankings,
                "keyness_score_avg": sum_keyn_scores / n_rankings,
                "n_rankings": n_rankings
            })

        sorted_l_d_keyn = sorted(sorted(
            l_d_keyn,
            key=lambda i: i["item"]),
            key=lambda i: i["ranking_score_avg"], reverse=True
        )  # sort key items by 1) ranking_score_avg (descending); 2) pos_lem_or_tok (ascending)
        results_to_xlsx_per_sc(
            subcorpora_sc, subcorpora_rc, name_sc, maintain_subcorpora_sc, maintain_subcorpora_rc, lemma_or_token,
            frequency_type, keyness_metric, ranking_threshold, sorted_l_d_keyn, d_keyn_per_rc
        )
        d_keyn_overview[name_sc] = sorted_l_d_keyn

    d_keyn_all_scs = OrderedDict()

    for corpus in d_keyn_overview:

        for dic in d_keyn_overview[corpus]:
            tup = dic["item"]

            if tup not in d_keyn_all_scs:
                d_keyn_all_scs[tup] = {}

                for study_corpus in d_keyn_overview:
                    d_keyn_all_scs[tup][study_corpus] = "NA"

            d_keyn_all_scs[tup][corpus] = dic

    l_d_keyn_all = []

    for tup in d_keyn_all_scs:
        sum_ranking_scores = 0
        sum_keyn_scores = 0
        n_rankings = 0

        for corpus in d_keyn_all_scs[tup]:

            if d_keyn_all_scs[tup][corpus] != "NA":
                sum_ranking_scores += d_keyn_all_scs[tup][corpus]["ranking_score_avg"]
                sum_keyn_scores += d_keyn_all_scs[tup][corpus]["keyness_score_avg"]
                n_rankings += 1

        l_d_keyn_all.append({
            "item": tup,
            "d_keyn": d_keyn_all_scs[tup],
            "ranking_score_avg_avg": sum_ranking_scores / n_rankings,
            "keyness_score_avg_avg": sum_keyn_scores / n_rankings,
            "n_rankings": n_rankings
        })

    sorted_l_d_keyn_all = sorted(sorted(
        l_d_keyn_all,
        key=lambda i: i["item"]),
        key=lambda i: i["ranking_score_avg_avg"], reverse=True
    )  # sort key items by 1) ranking_score_avg (descending); 2) pos_lem_or_tok (ascending)
    results_to_xlsx_overview(
        subcorpora_sc, subcorpora_rc, maintain_subcorpora_sc, maintain_subcorpora_rc, lemma_or_token, frequency_type,
        keyness_metric, ranking_threshold, sorted_l_d_keyn_all, d_keyn_overview
    )
