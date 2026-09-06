# MATCH samples

## In-app (recommended)

1. Open **KIT** (or click `SUBSTANCE / MATCH`, or press **K**)
2. Pick bank: `LAB-01` / `CLUB-01` / `FILM-01` / `HAZE-01` / `STEEL-01`
3. **LOAD** or drag-drop a WAV/MP3 onto a slot
4. **▶** preview · **✕** restore bake

User drops are stored on this machine (IndexedDB) and survive restarts.

## Banks

| Bank | Feel |
|------|------|
| LAB-01 | warm writing kit |
| CLUB-01 | hard transient / bite |
| FILM-01 | soft body · long air |
| HAZE-01 | murky fog · long pad |
| STEEL-01 | industrial edge |

Moods auto-bias banks (e.g. HAZE→HAZE-01, STEEL→STEEL-01). Shift+click **SOUND** cycles banks.

## Optional folder drops

Still works if you prefer files on disk:

```
src/samples/{BANK}/{slot}.wav
```

Slots: `kick_h` `kick_s` `snare_h` `snare_s` `hat_h` `hat_s` `bass` `keys` `pluck` `pad`

Priority: **user KIT drop > folder WAV > procedural bake**
