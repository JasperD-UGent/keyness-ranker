import numpy as np
import sys
from typing import Dict, List


def keyness(
        approx: float,
        stat_sign_thresh: int,
        degrs_of_freed: int,
        freq_type: str,
        keyn_metric: str,
        n_iters: int,
        d_abs_adj_sc: Dict,
        l_d_sum_abs_adj_sc: List,
        d_abs_adj_rc: Dict,
        l_d_sum_abs_adj_rc: List
) -> List:
    """STEP_3: calculate keyness (data stored in "[SC]_VS_[RC]" folder).
    :param approx: float by which zero frequencies are approximated.
    :param stat_sign_thresh: statistical significance threshold for BIC values.
    :param degrs_of_freed: degrees of freedom used to calculate log likelihood values.
    :param freq_type: frequency type based on which keyness values are calculated.
    :param keyn_metric: keyness metric used to perform the keyness calculations.
    :param n_iters: when working with adjusted frequencies, number of times the subcorpora are randomly shuffled to
        generate new subcorpora (and, thus, also new dispersion values). This will lead to (slightly) different keyness
        values (and rankings), which are averaged out in the end.
    :param d_abs_adj_sc: frequency dictionary enriched with adjusted frequency values (per item) for the study corpus.
    :param l_d_sum_abs_adj_sc: list of frequency dictionaries enriched with adjusted frequency values (totals) for the
        study corpus.
    :param d_abs_adj_rc: frequency dictionary enriched with adjusted frequency values (per item) for the reference
        corpus.
    :param l_d_sum_abs_adj_rc: list of frequency dictionaries enriched with adjusted frequency values (totals) for the
        reference corpus.
    :return: a list of dictionaries containing the keyness analysis and ranking information.
    """
    l_d_keyn_ranked = []

    for iteration in range(n_iters):
        l_d_keyn_ranked_prov = []

        sum_sc = l_d_sum_abs_adj_sc[iteration]["all"][freq_type]
        sum_rc = l_d_sum_abs_adj_rc[iteration]["all"][freq_type]

        for tup in d_abs_adj_sc:

            freq_sc = d_abs_adj_sc[tup][freq_type][iteration]

            if tup in d_abs_adj_rc:
                freq_rc = d_abs_adj_rc[tup][freq_type][iteration]

            else:

                if freq_type in ["abs_freq", "adj_freq"]:
                    freq_rc = approx
                elif freq_type in ["abs_freq_Lapl", "adj_freq_Lapl"]:
                    freq_rc = 1
                else:
                    raise ValueError("`frequency_type` is not correctly defined.")

            exp_freq_sc = sum_sc * (freq_sc + freq_rc) / (sum_sc + sum_rc)
            exp_freq_rc = sum_rc * (freq_sc + freq_rc) / (sum_sc + sum_rc)

            norm_freq_1000_sc = freq_sc / sum_sc * 1000
            norm_freq_1000_rc = freq_rc / sum_rc * 1000

            if keyn_metric == "DIFF":
                keyn_score_sc = ((norm_freq_1000_sc - norm_freq_1000_rc) * 100) / norm_freq_1000_rc
            elif keyn_metric == "Ratio":
                keyn_score_sc = norm_freq_1000_sc / norm_freq_1000_rc
            elif keyn_metric == "OddsRatio":
                keyn_score_sc = (freq_sc / (sum_sc - freq_sc)) / (freq_rc / (sum_rc - freq_rc))
            elif keyn_metric == "LogRatio":
                keyn_score_sc = np.log2(norm_freq_1000_sc / norm_freq_1000_rc)
            elif keyn_metric == "DiffCoefficient":
                keyn_score_sc = (norm_freq_1000_sc - norm_freq_1000_rc) / (norm_freq_1000_sc + norm_freq_1000_rc)
            else:
                raise ValueError("`keyness_metric` is not correctly defined.")

            if freq_sc == 0 or exp_freq_sc == 0:

                if freq_rc == 0 or exp_freq_rc == 0:
                    log_lik = 0
                else:
                    log_lik = 2 * (freq_rc * np.log(freq_rc / exp_freq_rc))

            else:

                if freq_rc == 0 or exp_freq_rc == 0:
                    log_lik = 2 * (freq_sc * np.log(freq_sc / exp_freq_sc))
                else:
                    log_lik = 2 * (
                                (freq_sc * np.log(freq_sc / exp_freq_sc)) + (freq_rc * np.log(freq_rc / exp_freq_rc)))

            bic = log_lik - (degrs_of_freed * np.log(sum_sc + sum_rc))

            d_keyn_ranked_prov = {}

            if bic >= stat_sign_thresh:
                d_keyn_ranked_prov["item"] = tup
                d_keyn_ranked_prov["keyn_SC"] = keyn_score_sc
                d_keyn_ranked_prov["freq_SC"] = freq_sc

                l_d_keyn_ranked_prov.append(d_keyn_ranked_prov)

        sorted_l_d_keyn_ranked = sorted(sorted(sorted(
            l_d_keyn_ranked_prov,
            key=lambda i: i["item"]),
            key=lambda i: i["freq_SC"], reverse=True),
            key=lambda i: i["keyn_SC"], reverse=True
        )  # sort key items by 1) keyness (descending); 2) freq_SC (descending); 3) pos_lem_or_tok (ascending)

        d_keyn_ranked = {}
        ranking_score_abs = len(sorted_l_d_keyn_ranked)

        for dic in sorted_l_d_keyn_ranked:
            tup = dic["item"]
            d_keyn_ranked[tup] = {
                "keyn": dic["keyn_SC"], "freq_SC": dic["freq_SC"],
                "ranking_score": ranking_score_abs / len(sorted_l_d_keyn_ranked) * 100
            }
            ranking_score_abs -= 1

        l_d_keyn_ranked.append(d_keyn_ranked)

    return l_d_keyn_ranked
