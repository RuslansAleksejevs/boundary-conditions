"""Counts, paired contract bootstrap, and explicit incomplete-data uncertainty."""

import math
import random
from collections import Counter


def wilson(successes, total, z=1.959963984540054):
    if total == 0:
        return None
    p = successes / total
    d = 1 + z * z / total
    center = (p + z * z / (2 * total)) / d
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / d
    return [max(0.0, center - radius), min(1.0, center + radius)]


def rate(num, den):
    return {"numerator": num, "denominator": den,
            "estimate": num / den if den else None, "wilson95": wilson(num, den)}


def summarize(outcomes):
    n = len(outcomes)
    statuses = Counter(o["status"] for o in outcomes)
    assessed = sum(o["status"] == "completed" for o in outcomes)
    false = sum(o["false_safe"] for o in outcomes)
    accepted = sum(o["accepted"] for o in outcomes)
    safe_answers = sum(o["answer"] is not None and o["answer"]["verdict"] == "SAFE"
                       for o in outcomes)
    unsafe_answers = sum(o["answer"] is not None and o["answer"]["verdict"] == "UNSAFE"
                         for o in outcomes)
    result = {"scheduled": n, "assessed": assessed, "statuses": dict(statuses),
              "observed_false_safe_all_scheduled": rate(false, n),
              "false_safe_among_SAFE": rate(false, safe_answers),
              "error_among_accepted": rate(sum(o["error_accepted"] for o in outcomes), accepted),
              "correct_completion": rate(sum(o["correct"] for o in outcomes), n),
              "abstentions": rate(sum(o["abstained"] for o in outcomes), n),
              "valid_UNSAFE_witnesses": rate(sum(o["valid_witness"] is True for o in outcomes),
                                              unsafe_answers),
              "unassessed": n - assessed,
              "full_sample_false_safe_bounds": [false / n, (false + n - assessed) / n] if n else None}
    if assessed < n:
        result["observed_false_safe_all_scheduled"]["wilson95"] = None
        result["observed_false_safe_all_scheduled"]["note"] = "lower bound, not an imputed safe rate"
    result["zero_failure_one_sided95_upper"] = (
        1 - 0.05**(1 / n) if n and false == 0 and assessed == n else None)
    return result


def paired(outcomes, other, metric="false_safe", seed=606, samples=5000):
    by_case = {}
    for outcome in outcomes:
        by_case.setdefault(outcome["case_id"], {})[outcome["condition"]] = outcome
    differences, discordance = [], Counter()
    lower, upper = 0, 0
    for arms in by_case.values():
        a, b = arms.get("B"), arms.get(other)
        left = int(a[metric]) if a is not None and a["status"] == "completed" else None
        right = int(b[metric]) if b is not None and b["status"] == "completed" else None
        lower += (right if right is not None else 0) - (left if left is not None else 1)
        upper += (right if right is not None else 1) - (left if left is not None else 0)
        if left is None or right is None:
            continue
        differences.append(right - left)
        discordance[f"B={left},{other}={right}"] += 1
    n = len(differences)
    bounds = [lower / len(by_case), upper / len(by_case)] if by_case else None
    if not n:
        return {"contrast": other + "-B", "metric": metric, "complete_pairs": 0,
                "scheduled_pairs": len(by_case), "difference": None, "bootstrap95": None,
                "scheduled_difference_bounds": bounds}
    rng = random.Random(seed)
    boot = sorted(sum(rng.choices(differences, k=n)) / n for _ in range(samples))
    average = sum(differences) / n
    # Differences lie in [-1,1]. This conservative interval does not collapse to
    # [0,0] on zero discordance, unlike the empirical percentile bootstrap.
    radius = math.sqrt(2 * math.log(2 / 0.05) / n)
    return {"contrast": other + "-B", "metric": metric, "complete_pairs": n,
            "scheduled_pairs": len(by_case), "excluded_unassessed_pairs": len(by_case) - n,
            "sum_differences": sum(differences), "difference": average,
            "scheduled_difference_bounds": bounds,
            "discordance": dict(discordance),
            "bootstrap95": [boot[int(0.025 * (samples - 1))], boot[int(0.975 * (samples - 1))]],
            "bounded_iid_hoeffding95": [max(-1, average - radius), min(1, average + radius)],
            "bootstrap_samples": samples, "bootstrap_seed": seed,
            "note": "Contract-level paired resampling; template dependence limits inference. "
                    "Degenerate bootstrap intervals do not establish absence of an effect."}


def analyze(run):
    outcomes = run["outcomes"]
    groups = {}
    for group in ("natural", "fault", "equivalent"):
        groups[group] = {}
        for condition in (("B",) if group == "natural" else ("B", "N", "S")):
            subset = [o for o in outcomes if o["group"] == group and o["condition"] == condition]
            groups[group][condition] = summarize(subset)
    natural = [o for o in outcomes if o["group"] == "natural"]
    valid_translations = [o for o in natural if o["fidelity"] is not None]
    drift = sum(not o["fidelity"]["open_functions_equal"] for o in valid_translations)
    unique = {o["case_id"]: o for o in outcomes}
    oracle = {}
    for group in ("natural", "fault", "equivalent"):
        cases = [o for o in unique.values() if o["group"] == group]
        gates = [o["oracle_ceiling"] for o in cases if o["oracle_ceiling"] is not None]
        oracle[group] = {"scheduled_cases": len(cases), "assessed_cases": len(gates),
                         "correct_original_verdicts": sum(g["verdict"] == o["original_truth"]
                                                          for o in cases if (g := o["oracle_ceiling"]) is not None),
                         "certificates_bound_to_original": sum(g["certificate_bound_to_original"] for g in gates),
                         "textual_identity_acceptances": sum(g["textual_identity"] for g in gates),
                         "privileged_engineering_control_not_model_evidence": True}
    usage = {}
    for field in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_input_tokens", "cost_usd"):
        known = [c["usage"][field] for c in run["calls"]
                 if c["usage"] is not None and c["usage"][field] is not None]
        usage[field] = {"known_sum": sum(known), "known_calls": len(known),
                        "scheduled_calls": run["scheduled_calls"],
                        "total": sum(known) if len(known) == run["scheduled_calls"] else None}
    return {"mode": run["adapter"]["kind"], "split": run["split"],
            "new_model_calls": run["new_model_calls"], "scheduled_calls": run["scheduled_calls"],
            "call_statuses": dict(Counter(c["status"] for c in run["calls"])),
            "adapter_invocations": sum(c["adapter_invoked"] for c in run["calls"]),
            "groups": groups, "natural_drift_among_valid_translations": rate(drift, len(valid_translations)),
            "natural_unassessed_translations": len(natural) - len(valid_translations),
            "natural_fidelity_counts": {field: {"changed": sum(not o["fidelity"][field] for o in valid_translations),
                                                 "assessed": len(valid_translations)}
                                        for field in ("C_equal", "Q_equal", "closed_truth_equal")},
            "oracle_ceiling_and_textual_baseline": oracle,
            "equivalent_false_rejections": {
                arm: rate(sum(o["status"] == "completed" and o["answer"]["verdict"] != "SAFE"
                              for o in outcomes if o["group"] == "equivalent" and o["condition"] == arm),
                          sum(o["group"] == "equivalent" and o["condition"] == arm for o in outcomes))
                for arm in ("B", "N", "S")},
            "primary_fault_S_minus_B": paired([o for o in outcomes if o["group"] == "fault"], "S"),
            "secondary_fault_N_minus_B": paired([o for o in outcomes if o["group"] == "fault"], "N"),
            "equivalent_utility_S_minus_B": paired([o for o in outcomes if o["group"] == "equivalent"],
                                                   "S", "correct"),
            "fault_families_descriptive": {
                family: {arm: summarize([o for o in outcomes if o["group"] == "fault"
                                         and o["family"] == family and o["condition"] == arm])
                         for arm in ("B", "N", "S")}
                for family in sorted({o["family"] for o in outcomes if o["group"] == "fault"})},
            "usage": usage,
            "local_adapter_latency_seconds": sum(c["latency_seconds"] for c in run["calls"]),
            "latency_note": "Replay/double latency is not original provider latency.",
            "interpretation": ("SOFTWARE TEST ONLY; no empirical model effects measured."
                               if run["adapter"]["kind"] == "synthetic_test_double" else
                               "Offline replay; provenance and original acquisition require separate audit.")}
