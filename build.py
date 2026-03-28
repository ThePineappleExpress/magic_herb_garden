"""build.py - Production build script for Magic Herb Tracker.

Workflow
--------
1. Compile the Rust ``crypto_rs`` extension via maturin (release mode).
2. Compile the entire Python application to a native binary via Nuitka.
3. Archive the output into ``dist/magic-herb-tracker-<version>-<platform>.zip``
   (Linux / Windows) or a ``.dmg`` (macOS, requires ``create-dmg``).

Usage
-----
    python build.py                 # standalone onefile binary
    python build.py --no-onefile    # standalone folder (faster, easier to debug)
    python build.py --skip-maturin  # skip the Rust build step (already built)
    python build.py --no-archive    # skip zip/dmg creation

Requirements
------------
    uv pip install --python .venv/bin/python maturin nuitka
    # macOS DMG packaging (optional):  brew install create-dmg
    # Rust toolchain: https://rustup.rs

The resulting binary is fully self-contained - no Python runtime required.
User data lives in the OS data directory (platformdirs) and is never touched
by the build process.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# -- paths ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
PYTHON = VENV / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")
DIST = ROOT / "dist"
CARGO_MANIFEST = ROOT / "crypto_rs" / "Cargo.toml"

# -- version -------------------------------------------------------------------

def _get_version() -> str:
    try:
        import tomllib
        with open(ROOT / "pyproject.toml", "rb") as f:
            return tomllib.load(f)["project"]["version"]
    except Exception:
        return "0.0.0"


# -- helpers -------------------------------------------------------------------

def _run(args: list[str], **kwargs) -> None:
    """Run a subprocess, raising on non-zero exit."""
    print(f"\n> {' '.join(str(a) for a in args)}\n")
    subprocess.run([str(a) for a in args], check=True, **kwargs)


def _platform_tag() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "darwin":
        return f"macos-{machine}"
    if system == "windows":
        return f"windows-{machine}"
    return f"linux-{machine}"


# -- step 1: maturin -----------------------------------------------------------

def build_rust(skip: bool = False) -> None:
    if skip:
        print("Skipping maturin build (--skip-maturin)")
        return

    maturin = VENV / ("Scripts/maturin.exe" if platform.system() == "Windows" else "bin/maturin")
    if not maturin.exists():
        print("maturin not found in venv - attempting install")
        _run([PYTHON, "-m", "pip", "install", "maturin"])

    print("Building crypto_rs Rust extension (release) ...")
    _run([
        maturin, "develop",
        "--release",
        "--manifest-path", CARGO_MANIFEST,
    ])


# -- step 2: nuitka ------------------------------------------------------------

def build_nuitka(onefile: bool = True) -> Path:
    """Compile main.py with Nuitka and return the path to the output binary / folder."""

    system = platform.system()
    version = _get_version()
    output_dir = ROOT / "build" / _platform_tag()
    output_dir.mkdir(parents=True, exist_ok=True)

    # -- base flags ------------------------------------------------------------
    cmd: list[str | Path] = [
        PYTHON, "-m", "nuitka",
        "--standalone",
        "--enable-plugin=kivy",

        # bin/ contains Python packages (bin.themes, bin.shaders, bin.lang)
        # AND data files (.glsl, .toml, .json). Include as both package and data.
        "--include-package=bin",
        f"--include-data-files={ROOT / 'bin' / 'db'}/*.json=bin/db/",
        f"--include-data-files={ROOT / 'bin' / 'shaders'}/*.glsl=bin/shaders/",
        f"--include-data-files={ROOT / 'bin' / 'themes'}/*.toml=bin/themes/",

        # Static assets (fonts, icons, branding)
        f"--include-data-dir={ROOT / 'res'}=res",
        f"--include-data-files={ROOT / 'magicherbtracker.kv'}=magicherbtracker.kv",

        # Service layer (services/)
        "--include-package=services",

        # Kivy discovers its own data via its package path
        "--include-package=kivy",
        "--include-package=kivy_garden",

        # crypto_rs is a compiled extension - Nuitka picks it up automatically
        # but naming it here ensures it's never missed.
        "--include-package=crypto_rs",

        # Dynamic imports that Nuitka cannot trace statically:
        # - lang.py uses importlib.import_module(f"bin.lang.{name}")
        # - validators.py uses jsonschema conditionally
        "--include-package=jsonschema",

        # Remove unused heavy imports that may have been auto-detected
        "--nofollow-import-to=tkinter",
        "--nofollow-import-to=test",
        "--nofollow-import-to=unittest",

        # Output location
        f"--output-dir={output_dir}",

        # Give the binary the right name
        "--output-filename=magic-herb-tracker",

        # Product metadata (used by macOS / Windows)
        f"--product-version={version}",
        "--product-name=MagicHerbTracker",
        "--company-name=MagicHerbTracker",
    ]

    # -- platform-specific flags -----------------------------------------------
    # Allow Nuitka to auto-download tools (Dependency Walker etc.) in CI
    cmd.append("--assume-yes-for-downloads")

    if system == "Windows":
        cmd += [
            "--windows-console-mode=disable",   # GUI app - no terminal window
        ]
        icon = ROOT / "res" / "branding" / "icon.ico"
        if icon.exists():
            cmd.append(f"--windows-icon-from-ico={icon}")

    elif system == "Darwin":
        cmd += [
            "--macos-create-app-bundle",
            "--macos-app-name=MagicHerbTracker",
            f"--macos-app-version={version}",
        ]
        icon = ROOT / "res" / "branding" / "icon.icns"
        if icon.exists():
            cmd.append(f"--macos-app-icon={icon}")

    # -- onefile vs standalone-folder -----------------------------------------
    if onefile:
        cmd.append("--onefile")

    # -- entry point ----------------------------------------------------------
    cmd.append(ROOT / "main.py")

    print(f"Compiling with Nuitka (onefile={onefile}) ...")
    _run(cmd)

    # Locate the output artifact
    if system == "Darwin" and not onefile:
        artifact = output_dir / "main.app"
    elif system == "Windows":
        artifact = output_dir / "magic-herb-tracker.exe"
    else:
        artifact = output_dir / "magic-herb-tracker"

    if not artifact.exists():
        # Nuitka may use main.dist / main.onefile-build naming - search broadly
        candidates = list(output_dir.glob("magic-herb-tracker*")) + list(output_dir.glob("main*"))
        artifact = next((p for p in candidates if p.is_file() or p.is_dir()), output_dir)

    print(f"Build artifact: {artifact}")
    return artifact


# -- step 3: archive -----------------------------------------------------------

def archive(artifact: Path, skip: bool = False) -> None:
    if skip:
        print("Skipping archive creation (--no-archive)")
        return

    system = platform.system()
    version = _get_version()
    tag = _platform_tag()
    archive_stem = f"magic-herb-tracker-{version}-{tag}"
    DIST.mkdir(parents=True, exist_ok=True)

    if system == "Darwin" and shutil.which("create-dmg") and artifact.suffix == ".app":
        dmg_path = DIST / f"{archive_stem}.dmg"
        _run([
            "create-dmg",
            "--volname", "MagicHerbTracker",
            "--window-size", "540", "380",
            "--app-drop-link", "380", "170",
            str(dmg_path),
            str(artifact),
        ])
        print(f"DMG: {dmg_path}")
    else:
        zip_path = DIST / f"{archive_stem}.zip"
        print(f"Creating archive: {zip_path}")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            if artifact.is_file():
                zf.write(artifact, artifact.name)
            else:
                for file in sorted(artifact.rglob("*")):
                    if file.is_file():
                        zf.write(file, file.relative_to(artifact.parent))
        print(f"Archive: {zip_path}  ({zip_path.stat().st_size / 1_048_576:.1f} MB)")


# -- CLI -----------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build Magic Herb Tracker for distribution")
    parser.add_argument("--no-onefile", action="store_true", help="Produce a folder instead of a single file")
    parser.add_argument("--skip-maturin", action="store_true", help="Skip the Rust/maturin build step")
    parser.add_argument("--no-archive", action="store_true", help="Skip zip/dmg archiving")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Magic Herb Tracker - build {_get_version()}  ({_platform_tag()})")
    print(f"{'='*60}\n")

    build_rust(skip=args.skip_maturin)
    artifact = build_nuitka(onefile=not args.no_onefile)
    archive(artifact, skip=args.no_archive)

    print(f"\n{'='*60}")
    print(f"  Build complete OK")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
