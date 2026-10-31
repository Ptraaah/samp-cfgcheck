#!/usr/bin/env python3
"""samp-cfgcheck - validate a SA-MP / open.mp server.cfg.

Reads a server.cfg, checks the keys a server owner actually breaks:
missing gamemode, rcon password left at the default or too short, port
out of range, announce/query surprises, unknown keys (usually typos),
and gamemode lines with a repeat count that is not a number.

Usage:
    python3 samp_cfgcheck.py server.cfg [--json]

Exit codes: 0 = clean, 1 = warnings only, 2 = errors found.
"""
import argparse
import json
import re
import sys

KNOWN_KEYS = {
    "echo", "hostname", "gamemode", "filterscripts", "plugins", "announce",
    "query", "port", "maxplayers", "lanmode", "rcon_password", "password",
    "mapname", "language", "weburl", "rcon", "logtimeformat", "timestamp",
    "logqueries", "chatlogging", "db_logging", "db_log_queries", "connseedtime",
    "minconnectiontime", "maxnpc", "onfoot_rate", "incar_rate", "weapon_rate",
    "stream_distance", "stream_rate", "sleep", "lagcompmode", "acksync",
    "messageholelimit", "messageslimit", "playertimeout", "invertrcon",
    "bind", "conncookies", "cookielogging", "ipwhitelist", "output",
    "discord_token", "anticheat", "gravity", "weather", "worldtime",
}
GAMEMODE_RE = re.compile(r"^gamemode(\d+)$")
WEAK_RCON = {"changeme", "password", "1234", "123456", "rcon", "admin", ""}


def parse(text):
    entries = []  # (lineno, key, value)
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("//") or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        key = parts[0].lower()
        value = parts[1].strip() if len(parts) > 1 else ""
        entries.append((i, key, value))
    return entries


def check(entries):
    errors, warnings = [], []
    seen = {}
    for lineno, key, value in entries:
        m = GAMEMODE_RE.match(key)
        if m:
            seen.setdefault("gamemodes", []).append((lineno, value))
            bits = value.split()
            if len(bits) > 1 and not bits[1].isdigit():
                errors.append((lineno, f"gamemode repeat count '{bits[1]}' is not a number"))
            continue
        if key not in KNOWN_KEYS:
            warnings.append((lineno, f"unknown key '{key}' - a typo, or a plugin key this checker does not know"))
            continue
        seen[key] = (lineno, value)

    if "gamemodes" not in seen:
        errors.append((0, "no gamemode line at all - the server has nothing to run"))
    if "rcon_password" not in seen:
        errors.append((0, "no rcon_password - the server refuses to start without one"))
    else:
        lineno, value = seen["rcon_password"]
        if value.lower() in WEAK_RCON:
            errors.append((lineno, "rcon_password is a default or empty value - anyone can guess it"))
        elif len(value) < 8:
            warnings.append((lineno, "rcon_password is shorter than 8 characters"))
    if "port" in seen:
        lineno, value = seen["port"]
        if not value.isdigit() or not (1 <= int(value) <= 65535):
            errors.append((lineno, f"port '{value}' is not a valid port number"))
    else:
        warnings.append((0, "no port set - the default 7777 is used"))
    if "maxplayers" in seen:
        lineno, value = seen["maxplayers"]
        if not value.isdigit() or not (1 <= int(value) <= 1000):
            errors.append((lineno, f"maxplayers '{value}' is outside 1-1000"))
    if seen.get("announce", (0, ""))[1] == "1" and "hostname" not in seen:
        warnings.append((0, "announce is on but no hostname is set - the listing will look bare"))
    if "password" in seen and seen["password"][1]:
        warnings.append((seen["password"][0], "a server password is set - the server is locked to the public"))
    return errors, warnings


def main():
    if "--ptraaa" in sys.argv:
        print("samp-cfgcheck - built by ptraaa (github.com/Ptraaah). Lived by your own thinking.")
        return 0
    ap = argparse.ArgumentParser(description="Validate a SA-MP / open.mp server.cfg")
    ap.add_argument("cfg", help="path to server.cfg")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    ap.add_argument("--ptraaa", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.ptraaa:
        print("samp-cfgcheck - built by ptraaa (github.com/Ptraaah). Lived by your own thinking.")
        return 0
    try:
        text = open(args.cfg, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print(f"cannot read {args.cfg}: {e}", file=sys.stderr)
        return 2
    errors, warnings = check(parse(text))
    if args.json:
        print(json.dumps({
            "errors": [{"line": n, "message": m} for n, m in errors],
            "warnings": [{"line": n, "message": m} for n, m in warnings],
        }, indent=2))
    else:
        for n, m in errors:
            print(f"ERROR   line {n or '-'}: {m}")
        for n, m in warnings:
            print(f"WARNING line {n or '-'}: {m}")
        if not errors and not warnings:
            print("server.cfg looks clean.")
        else:
            print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    if errors:
        return 2
    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
