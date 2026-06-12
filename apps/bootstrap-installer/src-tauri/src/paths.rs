//! Filesystem paths + logging setup.
//!
//! Mirrors `hermes_constants.get_hermes_home()` from the Python CLI:
//!   Windows: %LOCALAPPDATA%\berdaya
//!   macOS:   ~/.berdaya
//!   Linux:   ~/.berdaya  (override via $BERDAYA_HOME / $HERMES_HOME)
//!
//! IMPORTANT: this must match exactly. Drift here means install.ps1
//! writes to one place and the installer reads from another, breaking
//! the bootstrap-complete check.

use std::path::{Path, PathBuf};
#[cfg(target_os = "macos")]
use std::process::Command;
use tracing_appender::non_blocking::WorkerGuard;

pub const PREFERRED_INSTALL_DIR: &str = "berdaya-agent";
pub const LEGACY_INSTALL_DIR: &str = "hermes-agent";

/// Returns the canonical Berdaya Agent home directory.
pub fn hermes_home() -> PathBuf {
    if let Ok(override_path) = std::env::var("BERDAYA_HOME") {
        if !override_path.trim().is_empty() {
            return PathBuf::from(override_path);
        }
    }
    if let Ok(override_path) = std::env::var("HERMES_HOME") {
        if !override_path.trim().is_empty() {
            return PathBuf::from(override_path);
        }
    }

    #[cfg(target_os = "windows")]
    {
        if let Some(local_app_data) = dirs::data_local_dir() {
            return local_app_data.join("berdaya");
        }
    }

    if let Some(home) = dirs::home_dir() {
        return home.join(".berdaya");
    }

    PathBuf::from(".berdaya")
}

/// Git checkout + venv under Berdaya home (berdaya-agent, legacy hermes-agent).
pub fn agent_install_dir() -> PathBuf {
    let home = hermes_home();
    let preferred = home.join(PREFERRED_INSTALL_DIR);
    let legacy = home.join(LEGACY_INSTALL_DIR);
    if preferred.is_dir() {
        return preferred;
    }
    if legacy.is_dir() {
        return legacy;
    }
    preferred
}

pub fn log_dir() -> PathBuf {
    hermes_home().join("logs")
}

pub fn log_path() -> PathBuf {
    log_dir().join("bootstrap-installer.log")
}

pub fn bootstrap_cache_dir() -> PathBuf {
    hermes_home().join("bootstrap-cache")
}

/// Stable location the installer copies itself to after a successful install.
pub fn installer_dest() -> PathBuf {
    let name = if cfg!(target_os = "windows") {
        "hermes-setup.exe"
    } else {
        "hermes-setup"
    };
    hermes_home().join(name)
}

/// Copy the currently-running installer binary to `installer_dest()`.
pub fn copy_self_to_hermes_home() -> std::io::Result<()> {
    let src = std::env::current_exe()?;
    let dest = installer_dest();

    let same = match (src.canonicalize(), dest.canonicalize()) {
        (Ok(a), Ok(b)) => a == b,
        _ => src == dest,
    };
    if same {
        tracing::info!(?dest, "installer already at destination; skipping self-copy");
        return Ok(());
    }

    if let Some(parent) = dest.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::copy(&src, &dest)?;
    repair_macos_installer_helper(&dest);
    tracing::info!(?src, ?dest, "copied installer to HERMES_HOME");
    Ok(())
}

#[cfg(target_os = "macos")]
fn repair_macos_installer_helper(path: &Path) {
    let _ = Command::new("/usr/bin/xattr")
        .args(["-cr"])
        .arg(path)
        .status();

    let verify = Command::new("/usr/bin/codesign")
        .arg("--verify")
        .arg(path)
        .status();

    if !matches!(verify, Ok(status) if status.success()) {
        let _ = Command::new("/usr/bin/codesign")
            .args(["--force", "--sign", "-"])
            .arg(path)
            .status();
    }
}

#[cfg(not(target_os = "macos"))]
fn repair_macos_installer_helper(_path: &Path) {}

pub fn likely_bootstrap_marker(install_root: &Path) -> PathBuf {
    install_root.join(".hermes-bootstrap-complete")
}

pub fn init_logging() -> Option<WorkerGuard> {
    let dir = log_dir();
    if let Err(err) = std::fs::create_dir_all(&dir) {
        eprintln!("[hermes-setup] could not create log dir {dir:?}: {err}");
        return None;
    }

    let file_appender = tracing_appender::rolling::never(&dir, "bootstrap-installer.log");
    let (non_blocking, guard) = tracing_appender::non_blocking(file_appender);

    let env_filter = tracing_subscriber::EnvFilter::try_from_env("HERMES_BOOTSTRAP_LOG")
        .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("info"));

    tracing_subscriber::fmt()
        .with_env_filter(env_filter)
        .with_writer(non_blocking)
        .with_ansi(false)
        .with_target(true)
        .init();

    Some(guard)
}

#[tauri::command]
pub fn get_log_path() -> String {
    log_path().to_string_lossy().into_owned()
}

#[tauri::command]
pub fn get_hermes_home() -> String {
    hermes_home().to_string_lossy().into_owned()
}

#[tauri::command]
pub fn open_log_dir(app: tauri::AppHandle) -> Result<(), String> {
    use tauri_plugin_opener::OpenerExt;
    let path = log_dir();
    app.opener()
        .open_path(path.to_string_lossy(), None::<&str>)
        .map_err(|e| e.to_string())
}
