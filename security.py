"""Signing-layer panel ("What guards the toll"). fetch() is called by collect.py, derive() by build.py.
Descriptive. Added 2026-11-14, after pre-registration. Not a tripwire."""
import datetime as dt

LABEL = "Descriptive. Added 2026-11-14, after pre-registration. Not a tripwire."
MPC_REPO, MPC_TAG, MPC_COMMIT = "near/mpc", "3.18.0", "e691bdb98d68dcf74653da58d043453a6318765f"
SRC = f"https://github.com/{MPC_REPO}/blob/{MPC_COMMIT}/"

# Result of reading the contract source at MPC_COMMIT (tag 3.18.0, the version `v1.signer.version()` returns).
# Re-check these if the deployed version changes; derive() flags a mismatch.
BOND_FINDING = {
    "finding": "none found in contract source",
    "checked": "participant join, vote and update paths, every #[payable] entry point, and a search of crates/contract/src for slash|bond|stake (0 hits)",
    "detail": [
        {"what": "Joining / new participant set: vote_new_parameters is not #[payable] and requires a valid TEE attestation; no deposit is taken",
         "where": SRC + "crates/contract/src/api/governance.rs#L31"},
        {"what": "Upgrade votes: vote_contract_update is not #[payable]; an update is approved once votes meet the threshold",
         "where": SRC + "crates/contract/src/api/update.rs#L82"},
        {"what": "update_config is #[private] (callable only by the contract account itself, which has no access keys)",
         "where": SRC + "crates/contract/src/api/update.rs#L152"},
        {"what": "prepay_attestation_storage is #[payable] but is a storage fee: exact multiple of the fee, 'no refunds, no withdrawal'; not slashable",
         "where": SRC + "crates/contract/src/api/attestation.rs#L51"},
        {"what": "Other deposits are 1 yoctoNEAR request/anti-spam deposits (sign, submit_contract_update, node management)",
         "where": SRC + "crates/near-mpc-contract-interface/src/deposits.rs#L4"},
    ],
}
UPGRADE_TXS_REASON = ("not collected: the FastNEAR tx API (tx.main.fastnear.com/v0/account) returns transaction hashes without method "
                      "names for v1.signer, whose traffic is dominated by signing requests; isolating upgrade votes would need every "
                      "transaction fetched, which did not fit the time box. Version changes below are taken from monthly state reads instead.")


def fetch(http):
    """Latest Intents TVL and DefiLlama's per-chain breakdown (the full history is ~3 MB, so only the latest values are kept)."""
    try:
        p = http("https://api.llama.fi/protocol/near-intents")
        return {"source": "https://api.llama.fi/protocol/near-intents", "latest": (p.get("tvl") or [None])[-1],
                "current_chain_tvls": p.get("currentChainTvls")}
    except Exception as e:  # no guessed value: record why it is missing
        return {"source": "https://api.llama.fi/protocol/near-intents", "latest": None, "error": str(e)}


def _runs(points):
    """Group consecutive points with the same margin: [(margin, first_date, last_date)]."""
    runs = []
    for p in points:
        if runs and runs[-1][0] == p["margin"]:
            runs[-1][2] = p["date"]
        else:
            runs.append([p["margin"], p["date"], p["date"]])
    return runs


def derive(head, hist, head_date, mpc, usd, raw_security):
    mon = lambda d: dt.date.fromisoformat(d).strftime("%b %Y")
    pts = sorted((p for p in hist if p["label"][0] != "-"), key=lambda p: p["label"])
    liveness = []
    for p, kind in [(p, "first-of-month") for p in pts] + [(head, "head")]:
        m = mpc(p["mpc_state"]) or {}
        tee = p.get("tee_accounts")
        liveness.append({"date": p["label"] if kind == "first-of-month" else head_date, "point": kind, "block": p["height"],
                         "participants_n": m.get("participants"), "threshold": m.get("threshold"),
                         "margin": m["participants"] - m["threshold"] if m.get("threshold") else None,
                         "tee_accounts_n": len(tee) if tee is not None else None,
                         "tee_reason": None if tee is not None else f"get_tee_accounts not available in contract version {p.get('mpc_version')} at this block",
                         "version": p.get("mpc_version")})
    parts = []
    for i, (mg, a, b) in enumerate(_runs(liveness)):
        span = mon(a) if mon(a) == mon(b) else f"{mon(a)} to {mon(b)}"
        parts.append(f"{mg} ({span})" if i else f"{mg} from {span}")
    liveness_text = ("Liveness margin (participants minus threshold, first-of-month points): " + ", then ".join(parts)
                     + f". Latest: {liveness[-1]['threshold']}-of-{liveness[-1]['participants_n']}, margin {liveness[-1]['margin']}.")

    changes, prev = [], None
    for p in liveness:
        if p["version"] != (prev or {}).get("version"):
            changes.append({"version": p["version"], "first_seen": p["date"], "first_seen_block": p["block"], "point": p["point"],
                            "changed_after": prev["date"] if prev else None})
        prev = p

    lat = (raw_security or {}).get("latest")
    value = lat["totalLiquidityUSD"] if lat else None
    cur = liveness[-1]
    bond = dict(BOND_FINDING, contract=f"{MPC_REPO}@{MPC_TAG} ({MPC_COMMIT})",
                version_match=head.get("mpc_version") == MPC_TAG,
                scope=f"Contract source at tag {MPC_TAG} only; the deployed code hash is not matched to a build of this tag.")
    if not bond["version_match"]:
        bond["finding"] = "unknown"
        bond["reason"] = f"deployed version {head.get('mpc_version')} differs from the version read ({MPC_TAG}); re-read the source"
    bond_text = "none found in contract" if bond["finding"] == "none found in contract source" else bond["finding"]
    sentence = (f"≈{usd(value)} held in Intents; {cur['threshold']} of {cur['participants_n']} signers must collude; "
                f"bond at risk per signer: {bond_text}. Security beyond that rests on TEE attestation "
                f"({cur['tee_accounts_n']} current entries) and operator identity.") if value else \
               f"Value held in Intents: null ({(raw_security or {}).get('error', 'not fetched')}); {cur['threshold']} of {cur['participants_n']} signers must collude."
    chains = (raw_security or {}).get("current_chain_tvls") or {}
    return {
        "label": LABEL,
        "liveness": {"points": liveness, "text": liveness_text},
        "governance": {
            "version_changes": changes, "current_version": head.get("mpc_version"),
            "pending_update_votes": head.get("contract_update_votes"), "access_keys_now": len(head.get("signer_access_keys") or []),
            "access_keys_block": head["height"],
            "rule": (f"Contract upgrades are approved once {cur['threshold']} participants (the threshold) vote for the same update; "
                     f"update_config is private; the account has {len(head.get('signer_access_keys') or [])} access keys (re-read at block {head['height']})."),
            "rule_sources": [BOND_FINDING["detail"][1]["where"], BOND_FINDING["detail"][2]["where"]],
            "upgrade_txs": None, "upgrade_txs_reason": UPGRADE_TXS_REASON,
        },
        "value_vs_corruption": {
            "value_in_intents_usd": value,
            "value_label": "value held in NEAR Intents. Part of it depends on MPC-controlled addresses; that share is not measured here. Context, not a precise exposure.",
            "value_source": (raw_security or {}).get("source"),
            "chain_breakdown_usd": {k: round(v) for k, v in sorted(chains.items(), key=lambda kv: -kv[1])},
            "chain_breakdown_note": "as reported by DefiLlama; which of these addresses are MPC-controlled is not measured",
            "signers_to_corrupt": cur["threshold"],
            "value_per_corruptible_signer_usd": value / cur["threshold"] if value else None,
            "tee_entries_now": cur["tee_accounts_n"],
            "sentence": sentence,
        },
        "participant_bond": bond,
    }
