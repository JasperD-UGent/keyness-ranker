import os
import statistics
import sys
from typing import Dict, List, Tuple
import xlsxwriter


def results_to_xlsx_per_sc(
        name_sc: str,
        name_rc: str,
        n_rc_prov: int,
        maintain_subcorpora_sc: bool,
        maintain_subcorpora_rc: bool,
        lem_or_tok: str,
        freq_type: str,
        keyn_metric: str,
        ranking_thresh: float,
        l_d_keyn: List,
        d_keyn_per_corpus: Dict,
) -> None:
    """Write results to XLSX (per study corpus).
    :param name_sc: name of the study corpus.
    :param name_rc: name of the reference corpus.
    :param n_rc_prov: number of subcorpora in the reference corpus.
    :param maintain_subcorpora_sc: when working with adjusted frequencies, boolean value which defines whether
        dispersion is based on existing subcorpora of the study corpus, or whether all documents are merged and randomly
        split into new subcorpora.
    :param maintain_subcorpora_rc: when working with adjusted frequencies, boolean value which defines whether
        dispersion is based on existing subcorpora of the reference corpus, or whether all documents are merged and
        randomly split into new subcorpora.
    :param lem_or_tok: defines whether to calculate frequencies on token or lemma level.
    :param freq_type: frequency type based on which keyness values are calculated.
    :param keyn_metric: keyness metric used to perform the keyness calculations.
    :param ranking_thresh: value between 0 and 1 which indicates in how many percent of the study corpus subcorpora -
        reference corpus subcorpora combinations a statistically significant keyness value is required before the item
        can enter into the keyness ranking.
    :param l_d_keyn: list of dictionaries containing the keyness analysis and ranking information.
    :param d_keyn_per_corpus: dictionary containing the lists of dictionaries containing the keyness analysis and
        ranking information per reference corpus.
    :return: `None`
    """
    output_direc = f"{name_sc}_VS_{name_rc}"
    fn_keyn = f"{name_sc}_VS_{name_rc}_keyness_ranked_{keyn_metric}_{freq_type}"

    if n_rc_prov == 1:
        n_rc = 1
    else:
        n_rc = n_rc_prov + 1

    n_rankings_thresh = n_rc * ranking_thresh

    # write final results into XLSX
    if not os.path.isdir(os.path.join("output", output_direc)):
        os.makedirs(os.path.join("output", output_direc))

    headers = [lem_or_tok, "POS", "number_values", "average_ranking_score", "average_keyness_score"]

    for corpus in d_keyn_per_corpus.keys():
        headers.append(corpus)

    wb = xlsxwriter.Workbook(os.path.join("output", output_direc, f"{fn_keyn}.xlsx"))
    ws1 = wb.add_worksheet("ranking_score_all")
    ws2 = wb.add_worksheet("keyness_all")
    ws3 = wb.add_worksheet("ranking_score_threshold")
    ws4 = wb.add_worksheet("keyness_threshold")
    ws5 = wb.add_worksheet("meta")

    column = 0

    for header in headers:
        ws1.write(0, column, header)
        ws2.write(0, column, header)
        ws3.write(0, column, header)
        ws4.write(0, column, header)
        column += 1

    row_ws_1_and_2 = 1

    for dic in l_d_keyn:
        ws1.write(row_ws_1_and_2, 0, str(dic["item"][0]))
        ws1.write(row_ws_1_and_2, 1, str(dic["item"][1]))
        ws1.write(row_ws_1_and_2, 2, dic["n_rankings"])
        ws1.write(row_ws_1_and_2, 3, dic["ranking_score_avg"])
        ws1.write(row_ws_1_and_2, 4, dic["keyness_score_avg"])

        ws2.write(row_ws_1_and_2, 0, str(dic["item"][0]))
        ws2.write(row_ws_1_and_2, 1, str(dic["item"][1]))
        ws2.write(row_ws_1_and_2, 2, dic["n_rankings"])
        ws2.write(row_ws_1_and_2, 3, dic["ranking_score_avg"])
        ws2.write(row_ws_1_and_2, 4, dic["keyness_score_avg"])

        column_ws = 5

        for corpus in dic["d_keyn"]:
            ranking_score = []
            keyn_score = []
            n_rankings = 0

            for item in dic["d_keyn"][corpus]:

                if item == "NA":
                    pass
                else:
                    ranking_score.append(item["ranking_score"])
                    keyn_score.append(item["keyn"])
                    n_rankings += 1

            if n_rankings == 0:
                ws1.write(row_ws_1_and_2, column_ws, "NA")
                ws2.write(row_ws_1_and_2, column_ws, "NA")
                column_ws += 1

            else:
                ws1.write(row_ws_1_and_2, column_ws, statistics.mean(ranking_score))
                ws2.write(row_ws_1_and_2, column_ws, statistics.mean(keyn_score))
                column_ws += 1

        row_ws_1_and_2 += 1

    row_ws_3_and_4 = 1

    for dic in l_d_keyn:

        if dic["n_rankings"] > n_rankings_thresh:
            ws3.write(row_ws_3_and_4, 0, str(dic["item"][0]))
            ws3.write(row_ws_3_and_4, 1, str(dic["item"][1]))
            ws3.write(row_ws_3_and_4, 2, dic["n_rankings"])
            ws3.write(row_ws_3_and_4, 3, dic["ranking_score_avg"])
            ws3.write(row_ws_3_and_4, 4, dic["keyness_score_avg"])

            ws4.write(row_ws_3_and_4, 0, str(dic["item"][0]))
            ws4.write(row_ws_3_and_4, 1, str(dic["item"][1]))
            ws4.write(row_ws_3_and_4, 2, dic["n_rankings"])
            ws4.write(row_ws_3_and_4, 3, dic["ranking_score_avg"])
            ws4.write(row_ws_3_and_4, 4, dic["keyness_score_avg"])

            column_ws = 5

            for corpus in dic["d_keyn"]:
                ranking_score = []
                keyn_score = []
                n_rankings = 0

                for item in dic["d_keyn"][corpus]:

                    if item == "NA":
                        pass
                    else:
                        ranking_score.append(item["ranking_score"])
                        keyn_score.append(item["keyn"])
                        n_rankings += 1

                if n_rankings == 0:
                    ws3.write(row_ws_3_and_4, column_ws, "NA")
                    ws4.write(row_ws_3_and_4, column_ws, "NA")
                    column_ws += 1

                else:
                    ws3.write(row_ws_3_and_4, column_ws, statistics.mean(ranking_score))
                    ws4.write(row_ws_3_and_4, column_ws, statistics.mean(keyn_score))
                    column_ws += 1

            row_ws_3_and_4 += 1

    ws5.write(0, 0, "name_sc")
    ws5.write(0, 1, name_sc)
    ws5.write(1, 0, "maintain_subcorpora_sc")
    ws5.write(1, 1, maintain_subcorpora_sc)
    ws5.write(2, 0, "name_rc")
    ws5.write(2, 1, name_rc)
    ws5.write(3, 0, "maintain_subcorpora_rc")
    ws5.write(3, 1, maintain_subcorpora_rc)

    wb.close()


def results_to_xlsx_overview(
        name_sc: str,
        name_rc: str,
        n_sc_prov: int,
        maintain_subcorpora_sc: bool,
        maintain_subcorpora_rc: bool,
        lem_or_tok: str,
        freq_type: str,
        keyn_metric: str,
        ranking_thresh: float,
        l_d_keyn: List,
        d_keyn_overview: Dict,
):
    """Write results to XLSX (overview).
    :param name_sc: name of the study corpus.
    :param name_rc: name of the reference corpus.
    :param n_sc_prov: number of subcorpora in the study corpus.
    :param maintain_subcorpora_sc: when working with adjusted frequencies, boolean value which defines whether
        dispersion is based on existing subcorpora of the study corpus, or whether all documents are merged and randomly
        split into new subcorpora.
    :param maintain_subcorpora_rc: when working with adjusted frequencies, boolean value which defines whether
        dispersion is based on existing subcorpora of the reference corpus, or whether all documents are merged and
        randomly split into new subcorpora.
    :param lem_or_tok: defines whether to calculate frequencies on token or lemma level.
    :param freq_type: frequency type based on which keyness values are calculated.
    :param keyn_metric: keyness metric used to perform the keyness calculations.
    :param ranking_thresh: value between 0 and 1 which indicates in how many percent of the study corpus subcorpora -
        reference corpus subcorpora combinations a statistically significant keyness value is required before the item
        can enter into the keyness ranking.
    :param l_d_keyn: list of dictionaries containing the keyness analysis and ranking information.
    :param d_keyn_overview: dictionary containing the overall results per study corpus.
    :return: `None`
    """
    output_direc = f"{name_sc}_VS_{name_rc}"
    fn_keyn = f"{name_sc}_VS_{name_rc}_keyness_ranked_overview_{keyn_metric}_{freq_type}"

    if n_sc_prov == 1:
        n_sc = 1
    else:
        n_sc = n_sc_prov + 1

    n_rankings_thresh = n_sc * ranking_thresh

    # write final results into XLSX
    headers = [lem_or_tok, "POS", "number_values", "average_ranking_score", "average_keyness_score"]

    for corpus in d_keyn_overview.keys():
        headers.append(corpus)

    wb = xlsxwriter.Workbook(os.path.join("output", output_direc, f"{fn_keyn}.xlsx"))
    ws1 = wb.add_worksheet("ranking_score_all")
    ws2 = wb.add_worksheet("ranking_score_threshold")
    ws3 = wb.add_worksheet("meta")

    column = 0

    for header in headers:
        ws1.write(0, column, header)
        ws2.write(0, column, header)
        column += 1

    row_ws1 = 1

    for dic in l_d_keyn:
        ws1.write(row_ws1, 0, str(dic["item"][0]))
        ws1.write(row_ws1, 1, str(dic["item"][1]))
        ws1.write(row_ws1, 2, dic["n_rankings"])
        ws1.write(row_ws1, 3, dic["ranking_score_avg_avg"])
        ws1.write(row_ws1, 4, dic["keyness_score_avg_avg"])

        column_ws = 5

        for corpus in dic["d_keyn"]:

            if dic["d_keyn"][corpus] == "NA":
                ws1.write(row_ws1, column_ws, "NA")
                column_ws += 1
            else:
                ws1.write(row_ws1, column_ws, dic["d_keyn"][corpus]["ranking_score_avg"])
                column_ws += 1

        row_ws1 += 1

    row_ws2 = 1

    for dic in l_d_keyn:

        if dic["n_rankings"] > n_rankings_thresh:
            ws2.write(row_ws2, 0, str(dic["item"][0]))
            ws2.write(row_ws2, 1, str(dic["item"][1]))
            ws2.write(row_ws2, 2, dic["n_rankings"])
            ws2.write(row_ws2, 3, dic["ranking_score_avg_avg"])
            ws2.write(row_ws2, 4, dic["keyness_score_avg_avg"])

            column_ws = 5

            for corpus in dic["d_keyn"]:

                if dic["d_keyn"][corpus] == "NA":
                    ws2.write(row_ws2, column_ws, "NA")
                    column_ws += 1
                else:
                    ws2.write(row_ws2, column_ws, dic["d_keyn"][corpus]["ranking_score_avg"])
                    column_ws += 1

            row_ws2 += 1

    ws3.write(0, 0, "name_SC")
    ws3.write(0, 1, name_sc)
    ws3.write(1, 0, "maintain_subcorpora_SC")
    ws3.write(1, 1, maintain_subcorpora_sc)
    ws3.write(2, 0, "name_RC")
    ws3.write(2, 1, name_rc)
    ws3.write(3, 0, "maintain_subcorpora_RC")
    ws3.write(3, 1, maintain_subcorpora_rc)

    wb.close()
