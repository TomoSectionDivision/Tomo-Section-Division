# TOMO (desktop)

Natywna aplikacja desktopowa **TOMO** — Tauri 2 na Windows.

Wersja: **0.3.1**

## Start (dev)

```bash
cd D:\BursztynDesktop\tomo-desktop
npm install
npm run dev
```

Okno otwiera się fullscreen. `F11` = windowed / fullscreen.

## Instalator (release, Windows)

```bash
npm install
npm run build:win
```

Instalator NSIS:

`src-tauri/target/release/bundle/nsis/TOMO_0.3.1_x64-setup.exe`

Zainstaluj → skrót w menu Start. Po restarcie Windowsa dane zostają lokalnie:

| Dane | Gdzie |
|------|--------|
| Section library + miniatury | IndexedDB w profilu WebView |
| Autosave draft | localStorage |
| MATCH user samples | IndexedDB |
| CAP / DNA↓ pliki | `Downloads/TOMO/{session}/` (CAP) · Downloads (DNA↓ fallback) |

To **nie jest chmura** — wszystko na tym PC (`127.0.0.1` w WebView = lokalnie).

## Co jest w środku

- Void instrument + SEED / FORM / DUAL  
- SYNTH ↔ MATCH + master glue  
- CAP pack → `Downloads/TOMO/{session}/`  
- Tempo (BPM + swing) + melody bass  
- DNA v2 (MATCH, swing, splices, wet)  
- LIVE: DUAL / KIT / LIB / SYNTH · PREFS (CAP defaults, tut reset)  
- Perform mode (`P`)  
- Section library (`L`) z fork / rename  

UI: `src/index.html`
