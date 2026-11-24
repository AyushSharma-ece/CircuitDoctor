"""
CircuitDoctor - DeepPCB Dataset Acquisition Module
Downloads and extracts the DeepPCB dataset from the official research repository.
Reference: Tang et al., 2019 (https://github.com/tangsanli5201/DeepPCB)
"""

import os
import sys
import zipfile
import urllib.request
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
DOWNLOADS_DIR = DATASETS_DIR / "downloads"
RAW_EXTRACT_DIR = DATASETS_DIR / "DeepPCB_raw"

DEEPPCB_ZIP_URL = "https://codeload.github.com/tangsanli5201/DeepPCB/zip/refs/heads/master"
ARCHIVE_PATH = DOWNLOADS_DIR / "DeepPCB_master.zip"

def download_deeppcb(force: bool = False) -> Path:
    """Download DeepPCB master archive from GitHub."""
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    if ARCHIVE_PATH.exists() and not force:
        size_mb = ARCHIVE_PATH.stat().st_size / (1024 * 1024)
        if size_mb > 10.0:
            print(f"[Dataset Download] Found existing archive at {ARCHIVE_PATH} ({size_mb:.1f} MB). Skipping download.")
            return ARCHIVE_PATH

    print(f"[Dataset Download] Fetching DeepPCB repository from {DEEPPCB_ZIP_URL}...")
    req = urllib.request.Request(
        DEEPPCB_ZIP_URL,
        headers={"User-Agent": "CircuitDoctor-Dataset-Engineer/1.0"}
    )
    
    chunk_size = 1024 * 1024  # 1 MB chunks
    downloaded_bytes = 0
    
    with urllib.request.urlopen(req) as response, open(ARCHIVE_PATH, "wb") as out_file:
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded_bytes += len(chunk)
            print(f"\r[Dataset Download] Downloaded {downloaded_bytes / (1024 * 1024):.1f} MB...", end="", flush=True)
            
    print(f"\n[Dataset Download] Completed download: {ARCHIVE_PATH} ({downloaded_bytes / (1024 * 1024):.1f} MB)")
    return ARCHIVE_PATH

def extract_deeppcb(archive_path: Path, force: bool = False) -> Path:
    """Extract DeepPCB zip archive into raw storage."""
    RAW_EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    
    target_pcb_data = RAW_EXTRACT_DIR / "DeepPCB-master" / "PCBData"
    if target_pcb_data.exists() and not force:
        print(f"[Dataset Extract] Found extracted PCBData at {target_pcb_data}. Skipping extraction.")
        return target_pcb_data
        
    print(f"[Dataset Extract] Extracting archive {archive_path.name} to {RAW_EXTRACT_DIR}...")
    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(RAW_EXTRACT_DIR)
        
    extracted_pcb_data = RAW_EXTRACT_DIR / "DeepPCB-master" / "PCBData"
    if not extracted_pcb_data.exists():
        # Fallback if unzipped without top-level directory
        extracted_pcb_data = RAW_EXTRACT_DIR / "PCBData"
        
    if not extracted_pcb_data.exists():
        raise FileNotFoundError(f"Failed to locate PCBData folder in extracted archive {RAW_EXTRACT_DIR}")
        
    print(f"[Dataset Extract] Successfully extracted PCBData to {extracted_pcb_data}")
    return extracted_pcb_data

if __name__ == "__main__":
    archive = download_deeppcb()
    pcb_data_dir = extract_deeppcb(archive)
    print(f"[Dataset Setup] PCB Data Ready at: {pcb_data_dir}")
