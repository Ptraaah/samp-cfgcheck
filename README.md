# samp-cfgcheck

Validate a SA-MP / open.mp `server.cfg` before you start the server, and catch
the mistakes that cost an evening: a gamemode line with a bad repeat count, the
rcon password still set to a default, a port that is not a port, a mistyped key
that the server silently ignores.

One file, Python 3 standard library only, nothing to install.

## Use

```bash
python3 samp_cfgcheck.py server.cfg
python3 samp_cfgcheck.py server.cfg --json
```

```
ERROR   line 6: gamemode repeat count 'two' is not a number
ERROR   line 3: rcon_password is a default or empty value - anyone can guess it
ERROR   line 5: port '77777' is not a valid port number
WARNING line 18: unknown key 'hostnme' - a typo, or a plugin key this checker does not know
```

Exit codes: `0` clean, `1` warnings only, `2` errors — so it drops straight
into a start script or CI.

## What it checks

- at least one `gamemode<N>` line, with a numeric repeat count
- `rcon_password` present, not a default value, not too short
- `port` and `maxplayers` in range
- unknown keys (usually typos — the server ignores them without telling you)
- `announce 1` without a hostname, and a forgotten server `password`

Indonesian: pemeriksa file konfigurasi server.cfg SA-MP / open.mp — menangkap
password rcon bawaan, port tidak valid, salah ketik nama key, dan baris
gamemode yang rusak, sebelum server dinyalakan.

## Support / Dukung

Free and MIT. If it saved you an evening, you can support the maker:
https://trakteer.id/adel_putra2

Gratis dan berlisensi MIT. Kalau tool ini menyelamatkan servermu, dukung
pembuatnya di https://trakteer.id/adel_putra2
