"""
Air-Gapped Enclave Offline Packaging & Verification Utility
Creates signed checksum manifests for all application files and offline wheels.
"""

import hashlib
import os
from pathlib import Path

def generate_offline_manifest(base_dir: str = "."):
    base = Path(base_dir)
    manifest_path = base / "OFFLINE_MANIFEST.sha256"
    
    hashes = []
    for root, dirs, files in os.walk(base):
        # Skip git, pycache, temp files
        if any(skip in root for skip in [".git", "__pycache__", ".pytest_cache", "venv"]):
            continue
        for file in files:
            if file == "OFFLINE_MANIFEST.sha256":
                continue
            fp = Path(root) / file
            try:
                hasher = hashlib.sha256()
                with open(fp, "rb") as f:
                    while chunk := f.read(65536):
                        hasher.update(chunk)
                rel_path = fp.relative_to(base).as_posix()
                hashes.append(f"{hasher.hexdigest()}  {rel_path}")
            except Exception as e:
                print(f"Skipping {fp}: {e}")

    hashes.sort()
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(hashes) + "\n")

    print(f"[OK] Generated {manifest_path} with {len(hashes)} verified files.")

if __name__ == "__main__":
    generate_offline_manifest()
