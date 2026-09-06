# MATCH samples

## In-app (recommended)

1. Open **KIT** (or click `SUBSTANCE / MATCH`, or press **K**)
2. Pick bank (same names as MOOD): `COLD-01` · `WARM-01` · `NIGHT-01` · `FILM-01` · `CLUB-01` · `HAZE-01` · `STEEL-01` · `BLOOM-01`
3. **LOAD** or drag-drop a WAV/MP3 onto a slot
4. **▶** preview · **✕** restore bake

User drops are stored on this machine (IndexedDB) and survive restarts.

Changing **MOOD** in the program loads that mood’s kit (the samples you dropped for it).

## Banks

| Bank | Feel |
|------|------|
| COLD-01 | cold snap · hard skin |
| WARM-01 | warm writing kit |
| NIGHT-01 | late pulse · shadowed air |
| FILM-01 | soft body · long air |
| CLUB-01 | hard transient / bite |
| HAZE-01 | murky fog · long pad |
| STEEL-01 | industrial edge |
| BLOOM-01 | open air · soft bloom |

## Optional folder drops

```
src/samples/{BANK}/{slot}.wav
```

Slots: `hat` `rim` `snare` `clap` `tom` `kick` `bass` `keys` `pluck` `pad`

PULSE SIZE bands (0–36, six bands of 6):

| SIZE | Drum |
|------|------|
| 0–6 | HAT |
| 6–12 | RIM |
| 12–18 | SNARE |
| 18–24 | CLAP |
| 24–30 | TOM |
| 30–36 | KICK |

Priority: **user KIT drop > folder WAV > procedural bake**
