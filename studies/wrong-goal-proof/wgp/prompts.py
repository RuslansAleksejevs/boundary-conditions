"""Frozen role boundaries. No reference AST, label, or oracle witness is sent."""

from .logic import canonical, digest


AST_SCHEMA = (
    'Contract JSON has exactly {"variables":["p","q","r","s"],"C":node,"Q":node}. '
    'A node is exactly {"var":"p"}, {"const":true}, {"op":"not","arg":node}, '
    'or {"op":"and"|"or"|"implies","args":[node,node]}. '
    'Use only the listed variables in the listed order. No other keys. '
    'Return JSON only, without Markdown. Constants are booleans, not 0/1. '
    'Maximum depth 10 and 127 nodes per expression.'
)
TRANSLATOR = (
    "Translate the supplied controlled Boolean task faithfully into C and Q. "
    "Preserve the admissible domain, obligation, and fixed atom meanings separately. "
    "Do not strengthen assumptions, weaken requirements, rename atoms, or try to "
    "make the universal claim true. UNSAFE tasks are legitimate tasks. " + AST_SCHEMA
)
REVIEWER = (
    "Answer the ORIGINAL task, not merely the translated candidate. The original "
    "task, candidate AST, and a local certificate are provided. Check that the "
    "candidate matches the original; a correct proof of a different contract does "
    "not establish the original. You may reason directly about the original. "
    "Return exactly {\"verdict\":\"SAFE\"|\"UNSAFE\"|\"UNRESOLVED\",\"witness\":object|null}. "
    "SAFE means every original admissible assignment satisfies original Q. "
    "For UNSAFE provide all original variables with Boolean values witnessing "
    "original C=true and Q=false. For SAFE or UNRESOLVED witness must be null. "
    "UNRESOLVED is allowed but does not solve the task. Return JSON only, no Markdown."
)

# Similar character lengths, NOT a claim of matched token counts. Actual provider
# token usage is recorded if supplied; stdlib cannot predict a provider tokenizer.
HEADINGS = {
    "B": "PASS. The verification record is presented below. The record contains the checked contract, its hash, the local verdict, and the complete finite certificate.",
    "N": "Verification record. The record below contains a checked contract, its hash, the local verdict, and the complete finite certificate in structured data fields.",
    "S": "Scope: only candidate C'/Q' were checked; the original contract was not checked. The record contains its hash, local verdict, and complete finite certificate.",
}


def request(case_id, role, payload, condition=None):
    system = TRANSLATOR if role == "translator" else REVIEWER
    user = canonical(payload)
    content = {"system": system, "user": user}
    return {"id": f"{case_id}:{role}:{condition or '-'}", "role": role,
            "condition": condition, **content,
            "prompt_hash": digest(content, "wgp-prompt-v1")}


def translation_request(case):
    return request(case["id"], "translator", {"original_task": case["task"]})


def review_request(case, candidate, certificate, condition):
    if condition not in HEADINGS:
        raise ValueError("unknown presentation")
    payload = {"original_task": case["task"], "candidate": candidate,
               "certificate": certificate,
               "checker": {"local_valid": True, "method": "independent exhaustive finite check"},
               "presentation": HEADINGS[condition]}
    return request(case["id"], "reviewer", payload, condition)


def prompt_spec():
    return {"translator": TRANSLATOR, "reviewer": REVIEWER, "headings": HEADINGS,
            "heading_characters": {key: len(value) for key, value in HEADINGS.items()},
            "schema": AST_SCHEMA}
