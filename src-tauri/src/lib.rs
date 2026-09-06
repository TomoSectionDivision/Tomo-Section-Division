use std::fs;
use std::path::PathBuf;
use tauri_plugin_opener::OpenerExt;

fn sanitize_bank(bank: &str) -> String {
    bank.chars()
        .filter(|c| c.is_ascii_alphanumeric() || *c == '-' || *c == '_')
        .take(32)
        .collect()
}

fn find_samples_root() -> Option<PathBuf> {
    let mut cands: Vec<PathBuf> = Vec::new();
    if let Ok(cwd) = std::env::current_dir() {
        cands.push(cwd.join("src").join("samples"));
        cands.push(cwd.join("samples"));
        cands.push(cwd.join("..").join("src").join("samples"));
    }
    if let Ok(exe) = std::env::current_exe() {
        if let Some(dir) = exe.parent() {
            cands.push(dir.join("samples"));
            cands.push(dir.join("resources").join("samples"));
            cands.push(dir.join("..").join("src").join("samples"));
            cands.push(dir.join("..").join("..").join("src").join("samples"));
        }
    }
    for p in &cands {
        if p.is_dir() {
            return Some(p.clone());
        }
    }
    // Create under src/samples when the frontend src tree is present
    if let Ok(cwd) = std::env::current_dir() {
        let src = cwd.join("src");
        if src.is_dir() {
            return Some(src.join("samples"));
        }
        let up = cwd.join("..").join("src");
        if up.is_dir() {
            return Some(up.join("samples"));
        }
    }
    None
}

#[tauri::command]
fn open_match_samples_dir(app: tauri::AppHandle, bank: String) -> Result<String, String> {
    let bank = sanitize_bank(&bank);
    if bank.is_empty() {
        return Err("bad bank".into());
    }
    let root = find_samples_root().ok_or_else(|| "samples folder not found".to_string())?;
    for b in [
        "COLD-01", "WARM-01", "NIGHT-01", "FILM-01", "CLUB-01", "HAZE-01", "STEEL-01", "BLOOM-01",
    ] {
        let _ = fs::create_dir_all(root.join(b));
    }
    let dir = root.join(&bank);
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let path = dir
        .canonicalize()
        .unwrap_or(dir)
        .to_string_lossy()
        .trim_start_matches(r"\\?\")
        .to_string();
    app.opener()
        .open_path(&path, None::<&str>)
        .map_err(|e| e.to_string())?;
    Ok(path)
}

fn sanitize_session(s: &str) -> String {
    s.chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || c == '-' || c == '_' {
                c
            } else {
                '_'
            }
        })
        .take(96)
        .collect()
}

fn sanitize_filename(s: &str) -> String {
    s.chars()
        .filter(|c| c.is_ascii_alphanumeric() || *c == '.' || *c == '-' || *c == '_')
        .take(128)
        .collect()
}

fn downloads_tomo_root() -> Result<PathBuf, String> {
    let home = std::env::var("USERPROFILE")
        .or_else(|_| std::env::var("HOME"))
        .map_err(|_| "home folder not found".to_string())?;
    Ok(PathBuf::from(home).join("Downloads").join("TOMO"))
}

fn path_display(p: PathBuf) -> String {
    p.canonicalize()
        .unwrap_or(p)
        .to_string_lossy()
        .trim_start_matches(r"\\?\")
        .to_string()
}

/// Write one CAP/export file into Downloads/TOMO/{session}/{filename}.
#[tauri::command]
fn write_export_file(session: String, filename: String, contents: Vec<u8>) -> Result<String, String> {
    let session = sanitize_session(&session);
    let filename = sanitize_filename(&filename);
    if session.is_empty() || filename.is_empty() {
        return Err("bad path".into());
    }
    if filename.contains("..") {
        return Err("bad filename".into());
    }
    let dir = downloads_tomo_root()?.join(&session);
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let path = dir.join(&filename);
    fs::write(&path, &contents).map_err(|e| e.to_string())?;
    Ok(path_display(path))
}

/// Open Downloads/TOMO/{session} in the OS file manager.
#[tauri::command]
fn open_export_folder(app: tauri::AppHandle, session: String) -> Result<String, String> {
    let session = sanitize_session(&session);
    if session.is_empty() {
        return Err("bad session".into());
    }
    let dir = downloads_tomo_root()?.join(&session);
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let path = path_display(dir);
    app.opener()
        .open_path(&path, None::<&str>)
        .map_err(|e| e.to_string())?;
    Ok(path)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        // single-instance disabled: it was focusing an older installed exe
        // instead of the build / `tauri dev` you just launched.
        .invoke_handler(tauri::generate_handler![
            open_match_samples_dir,
            write_export_file,
            open_export_folder
        ])
        .build(tauri::generate_context!())
        .expect("error while building TOMO")
        .run(|app_handle, event| {
            // When the main window is destroyed, kill the process.
            // Prevents zombie taskbar icons after close / failed JS quit.
            if let tauri::RunEvent::WindowEvent { label, event, .. } = &event {
                if label == "main" {
                    if let tauri::WindowEvent::Destroyed = event {
                        app_handle.exit(0);
                    }
                }
            }
        });
}
