"""Fetch raw data into data/raw/<UTC date of head block>/. Standard library only, no keys."""
import base64, datetime as dt, json, os, ssl, sys, time, urllib.request

RPC = "https://rpc.mainnet.near.org"
ARCHIVAL = "https://archival-rpc.mainnet.fastnear.com"
LLAMA = "https://api.llama.fi"
BLOCKS_PER_DAY = 149_421
SIGNER, BUYBACK = "v1.signer", "buybacks.multisignature.near"
OFFSETS_DAYS = [30, 31, 90, 180, 365, 384]   # history points relative to head
FIRST_MONTH = dt.date(2025, 10, 1)           # monthly history points start here


def tls_context():
    ctx = ssl.create_default_context()
    if sys.platform == "win32":
        # Windows' intermediate (CA) store can hold an expired ISRG cross-sign that OpenSSL
        # prefers over the valid chain FastNEAR serves. Trust the ROOT store only; still verified.
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        for der, enc, _ in ssl.enum_certificates("ROOT"):
            if enc == "x509_asn":
                try:
                    ctx.load_verify_locations(cadata=der)
                except ssl.SSLError:
                    pass
    return ctx


TLS = tls_context()


def http(url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "near-thesis/1.0"})
    time.sleep(0.25)  # pace requests: public nodes answer 429 to fast clients (seen on GitHub Actions)
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60, context=TLS) as r:
                return json.load(r)
        except Exception as e:
            if attempt == 5:
                raise RuntimeError(f"{url}: {e}") from e
            wait = 2
            if getattr(e, "code", None) == 429:  # rate limited: honour Retry-After, else back off 5, 10, 20, 40 s
                ra = e.headers.get("Retry-After", "")
                wait = min(60, float(ra) if ra.isdigit() else 5 * 2 ** attempt)
            time.sleep(wait)


def rpc(method, params, url=RPC):
    """Result of a JSON-RPC call, or None if the node returns an error (e.g. missing block, no contract)."""
    return http(url, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).get("result")


def ref(height):
    return {"block_id": height} if height else {"finality": "final"}


def view(method, height=None, url=RPC):
    r = rpc("query", {"request_type": "call_function", "account_id": SIGNER, "method_name": method,
                      "args_base64": base64.b64encode(b"{}").decode(), **ref(height)}, url)
    return json.loads(bytes(r["result"])) if r and "result" in r else None  # method absent in older contract versions


def account(account_id, height=None, url=RPC):
    return rpc("query", {"request_type": "view_account", "account_id": account_id, **ref(height)}, url)


def header(block):
    h = block["header"]
    return {"height": h["height"], "timestamp_ns": h["timestamp"], "total_supply": h["total_supply"]}


def trim_state(state):
    # keep parameters and domains; drop public keys and votes to keep raw files small
    if not state:
        return None
    return {k: {f: v.get(f) for f in ("parameters", "domains", "previous_running_state", "resharing_key")
                if isinstance(v, dict) and f in v} for k, v in state.items()}


def archival_block(height):
    for h in range(height, height + 9):  # some heights are skipped
        b = rpc("block", {"block_id": h}, ARCHIVAL)
        if b:
            return header(b)
    raise RuntimeError(f"no block in {height}..{height + 8}")


def block_for_time(target_s, head):
    est = head["height"] - round((int(head["timestamp_ns"]) / 1e9 - target_s) / 86400 * BLOCKS_PER_DAY)
    b = archival_block(est)
    err = target_s - int(b["timestamp_ns"]) / 1e9
    if abs(err) > 600:  # one correction step gets within minutes
        b = archival_block(b["height"] + round(err / 86400 * BLOCKS_PER_DAY))
    return b


def point(label, b):
    h = b["height"]
    print(f"  {label}: block {h}", file=sys.stderr)
    return {"label": label, **b,
            "mpc_state": trim_state(view("state", h, ARCHIVAL)),
            "mpc_version": view("version", h, ARCHIVAL),
            "tee_accounts": view("get_tee_accounts", h, ARCHIVAL),
            "buyback": account(BUYBACK, h, ARCHIVAL)}


def main():
    print("head (rpc.mainnet.near.org)", file=sys.stderr)
    head_block = rpc("block", {"finality": "final"})
    head = header(head_block)
    vals = rpc("validators", [None])
    head_raw = {
        **head,
        "protocol_config": {k: v for k, v in rpc("EXPERIMENTAL_protocol_config", {"finality": "final"}).items()
                            if k in ("max_inflation_rate", "protocol_reward_rate", "protocol_version", "epoch_length")},
        "validators": {"epoch_height": vals["epoch_height"],
                       "current": [{"account_id": v["account_id"], "stake": v["stake"]} for v in vals["current_validators"]],
                       "next_count": len(vals["next_validators"]),
                       "prev_epoch_kickout": [k["account_id"] for k in vals["prev_epoch_kickout"]]},
        "signer_access_keys": rpc("query", {"request_type": "view_access_key_list", "account_id": SIGNER, "finality": "final"})["keys"],
        "signer_account": account(SIGNER),
        "mpc_state": trim_state(view("state")),
        "mpc_version": view("version"),
        "tee_accounts": view("get_tee_accounts"),
        "contract_update_votes": view("contract_update_votes"),
        "buyback": account(BUYBACK),
    }

    print("history (archival-rpc.mainnet.fastnear.com)", file=sys.stderr)
    head_s = int(head["timestamp_ns"]) / 1e9
    history = [point(f"-{d}d", block_for_time(head_s - d * 86400, head)) for d in OFFSETS_DAYS]
    head_date = dt.datetime.fromtimestamp(head_s, dt.timezone.utc).date()
    m = FIRST_MONTH
    while m <= head_date:
        t = dt.datetime(m.year, m.month, 1, tzinfo=dt.timezone.utc).timestamp()
        history.append(point(m.isoformat(), block_for_time(t, head)))
        m = dt.date(m.year + m.month // 12, m.month % 12 + 1, 1)

    print("defillama + price", file=sys.stderr)
    def chart(path):
        r = http(LLAMA + path)
        return {k: r.get(k) for k in ("totalDataChart", "total24h", "total30d", "total60dto30d", "methodology")}
    llama = {
        "volume": chart("/summary/dexs/near-intents?excludeTotalDataChartBreakdown=true"),
        "fees": chart("/summary/fees/near-intents?dataType=dailyFees&excludeTotalDataChartBreakdown=true"),
        "revenue": chart("/summary/fees/near-intents?dataType=dailyRevenue&excludeTotalDataChartBreakdown=true"),
        "tvl_usd": http(LLAMA + "/tvl/near-intents"),
    }
    start = int(dt.datetime(2025, 9, 1, tzinfo=dt.timezone.utc).timestamp())
    days = (int(head_s) - start) // 86400 + 1
    daily = http(f"https://coins.llama.fi/chart/coingecko:near?start={start}&span={days}&period=1d")["coins"]["coingecko:near"]["prices"]
    try:
        spot, spot_source = http("https://api.coingecko.com/api/v3/simple/price?ids=near&vs_currencies=usd")["near"]["usd"], "coingecko"
    except Exception as e:  # CoinGecko rate-limits shared CI addresses; fall back to the latest daily price
        print(f"  coingecko spot failed ({e}); using latest coins.llama.fi price", file=sys.stderr)
        spot, spot_source = daily[-1]["price"], "coins.llama.fi (latest daily)"
    price = {"spot_usd": spot, "spot_source": spot_source, "daily": daily}

    out = os.path.join("data", "raw", head_date.isoformat())
    os.makedirs(out, exist_ok=True)
    for name, obj in (("head", head_raw), ("history", history), ("defillama", llama), ("price", price)):
        with open(os.path.join(out, name + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, indent=1, sort_keys=True)
    print(f"wrote {out}/ (block {head['height']})")


if __name__ == "__main__":
    main()
