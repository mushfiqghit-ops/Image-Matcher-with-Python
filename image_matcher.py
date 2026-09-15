#!/usr/bin/env python3
"""
Image Matcher System
Finds exact duplicate images by pixel-perfect comparison.
Compares reference images against production series images.
Version 1.1.3

Built by: Mushfiqur Rahman
AI Assistance: Claude (Anthropic) — architecture, logic design, and iterative development support
Concept, requirements, and domain knowledge by Mushfiqur Rahman.
"""

import os
import sys
import hashlib
import csv
from datetime import datetime
from PIL import Image
import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import time


class ImageMatcher:
    def __init__(self):
        self.reference_images = {}   # hash -> list of image info
        self.matches = []
        self.report_path = ""
        self.reference_folders = []
        self.production_folders = []

    def get_image_hash(self, image_path):
        """Generate SHA-256 hash from pixel data for exact matching."""
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                pixel_array = np.array(img)
                pixel_bytes = pixel_array.tobytes()
                return hashlib.sha256(pixel_bytes).hexdigest()
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None

    def compare_images_pixel_by_pixel(self, path1, path2):
        """Compare two images pixel by pixel — confirms exact match."""
        try:
            with Image.open(path1) as img1, Image.open(path2) as img2:
                if img1.mode != 'RGB':
                    img1 = img1.convert('RGB')
                if img2.mode != 'RGB':
                    img2 = img2.convert('RGB')
                if img1.size != img2.size:
                    return False
                arr1 = np.array(img1)
                arr2 = np.array(img2)
                return np.array_equal(arr1, arr2)
        except Exception as e:
            print(f"Error comparing images: {e}")
            return False

    def get_unique_image_files(self, folder):
        """Get unique image files, handling case-insensitive duplicates."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif'}
        all_files = []
        for item in Path(folder).iterdir():
            if item.is_file() and item.suffix.lower() in image_extensions:
                all_files.append(item)

        # Group by normalized filename to deduplicate
        file_groups = {}
        for item in all_files:
            norm_name = item.name.lower()
            if norm_name not in file_groups:
                file_groups[norm_name] = item

        return list(file_groups.values())

    def load_reference_images(self):
        """Load and hash all reference images."""
        print("\n" + "=" * 60)
        print("LOADING REFERENCE IMAGES")
        print("=" * 60)

        total_loaded = 0
        for folder in self.reference_folders:
            if not os.path.exists(folder):
                print(f"Warning: Folder not found - {folder}")
                continue

            print(f"\nProcessing reference folder: {folder}")
            folder_name = os.path.basename(folder)
            image_files = self.get_unique_image_files(folder)

            for img_path in image_files:
                img_hash = self.get_image_hash(str(img_path))
                if img_hash:
                    img_name = img_path.stem
                    if img_hash not in self.reference_images:
                        self.reference_images[img_hash] = []
                    self.reference_images[img_hash].append({
                        'name': img_name,
                        'folder': folder_name,
                        'full_path': str(img_path)
                    })
                    total_loaded += 1
                    if total_loaded % 10 == 0:
                        print(f"  Loaded {total_loaded} reference images...")

        print(f"\nTotal reference images loaded: {total_loaded}")

        duplicates = sum(1 for img_list in self.reference_images.values() if len(img_list) > 1)
        if duplicates > 0:
            print(f"Note: {duplicates} unique pixel patterns have multiple reference images")

        return total_loaded

    def process_production_images(self):
        """Hash production images and match against reference set."""
        print("\n" + "=" * 60)
        print("PROCESSING PRODUCTION IMAGES")
        print("=" * 60)

        total_processed = 0
        total_matches = 0

        for folder in self.production_folders:
            if not os.path.exists(folder):
                print(f"Warning: Folder not found - {folder}")
                continue

            series_name = os.path.basename(folder)
            print(f"\nProcessing series: {series_name}")
            image_files = self.get_unique_image_files(folder)
            series_matches = 0

            for img_path in image_files:
                total_processed += 1
                img_hash = self.get_image_hash(str(img_path))

                if img_hash and img_hash in self.reference_images:
                    ref_list = self.reference_images[img_hash]
                    prod_name = img_path.stem

                    for ref_info in ref_list:
                        # Pixel-by-pixel confirmation
                        if self.compare_images_pixel_by_pixel(ref_info['full_path'], str(img_path)):
                            self.matches.append({
                                'reference_image': ref_info['name'],
                                'reference_folder': ref_info['folder'],
                                'production_image': prod_name,
                                'production_series': series_name
                            })
                            series_matches += 1
                            total_matches += 1
                            print(f"  MATCH: {ref_info['name']} <-> {prod_name}")

                if total_processed % 50 == 0:
                    print(f"  Processed {total_processed} images, {total_matches} matches so far...")

            print(f"  Series {series_name}: {series_matches} matches found")

        print(f"\n{'=' * 60}")
        print(f"TOTAL IMAGES PROCESSED : {total_processed}")
        print(f"TOTAL MATCHES FOUND    : {total_matches}")
        print("=" * 60)

        return total_matches

    def save_report(self):
        """Save match results to a timestamped CSV file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.report_path, f"image_matches_{timestamp}.csv")

        try:
            with open(report_file, 'w', newline='') as csvfile:
                fieldnames = [
                    'Reference_Image', 'Reference_Folder',
                    'Production_Image', 'Production_Series'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for match in self.matches:
                    writer.writerow({
                        'Reference_Image':    match['reference_image'],
                        'Reference_Folder':   match['reference_folder'],
                        'Production_Image':   match['production_image'],
                        'Production_Series':  match['production_series']
                    })

            print(f"\nReport saved: {report_file}")
            return report_file
        except Exception as e:
            print(f"Error saving report: {e}")
            return None


def get_folder_path(prompt):
    """Open a folder selection dialog."""
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title=prompt)
    root.destroy()
    return folder


def main():
    print("\n" + "=" * 60)
    print(" IMAGE MATCHER — PIXEL-PERFECT DUPLICATE FINDER")
    print(" Version 1.1.3")
    print("=" * 60)

    matcher = ImageMatcher()

    # ── Step 1: Report output folder ─────────────────────────
    print("\n1. SELECT REPORT OUTPUT FOLDER")
    matcher.report_path = get_folder_path("Select Report Output Folder")
    if not matcher.report_path:
        print("No report path selected. Exiting.")
        return
    print(f"Report path: {matcher.report_path}")

    # ── Step 2: Reference folders ─────────────────────────────
    print("\n2. REFERENCE IMAGE FOLDERS")
    print("How many reference folders do you want to add?")
    try:
        num_ref = int(input("Number of reference folders: ").strip())
    except ValueError:
        print("Invalid input. Exiting.")
        return

    for i in range(num_ref):
        folder = get_folder_path(f"Select Reference Folder {i + 1}")
        if folder:
            matcher.reference_folders.append(folder)

    if not matcher.reference_folders:
        print("No reference folders selected. Exiting.")
        return

    # ── Step 3: Series list from text file ───────────────────
    print("\n3. PRODUCTION SERIES LIST")
    print("Select a text file containing series numbers (one per line).")

    root = tk.Tk()
    root.withdraw()
    series_file = filedialog.askopenfilename(
        title="Select Series List Text File",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    root.destroy()

    if not series_file:
        print("No series file selected. Exiting.")
        return

    series_list = []
    try:
        with open(series_file, 'r') as f:
            for line in f:
                series = line.strip()
                if series:
                    series_list.append(series)
        print(f"Loaded {len(series_list)} series numbers from: {series_file}")
    except Exception as e:
        print(f"Error reading series file: {e}")
        return

    if not series_list:
        print("No series numbers found in file. Exiting.")
        return

    # ── Step 4: Mother folder ─────────────────────────────────
    print("\n4. SELECT PRODUCTION IMAGES PARENT FOLDER")
    mother_folder = get_folder_path("Select folder containing all production series subfolders")
    if not mother_folder:
        print("No parent folder selected. Exiting.")
        return
    print(f"Parent folder: {mother_folder}")

    # ── Step 5: Scan for matching series folders ──────────────
    print("\n5. SCANNING FOR SERIES FOLDERS")
    found_series = []
    missing_series = []

    for series in series_list:
        series_path = os.path.join(mother_folder, series)
        if os.path.exists(series_path) and os.path.isdir(series_path):
            matcher.production_folders.append(series_path)
            found_series.append(series)
        else:
            missing_series.append(series)

    print(f"\n✓ Found   : {len(found_series)} series folders")
    print(f"✗ Missing : {len(missing_series)} series folders")

    if missing_series:
        preview = missing_series[:5]
        print(f"  Missing (first {len(preview)}): {', '.join(preview)}")

    if not found_series:
        print("\nNo matching series folders found. Exiting.")
        return

    proceed = input(f"\nProceed with {len(found_series)} series? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Operation cancelled.")
        return

    # ── Processing ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("STARTING IMAGE COMPARISON")
    print("=" * 60)

    start_time = time.time()

    num_ref = matcher.load_reference_images()
    if num_ref == 0:
        print("No reference images found. Exiting.")
        return

    num_matches = matcher.process_production_images()

    if num_matches > 0:
        report_file = matcher.save_report()
        if report_file:
            print(f"\n✓ {num_matches} matching images found.")
            print(f"✓ Report: {report_file}")
    else:
        print("\n⚠  No matching images found.")

    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.2f} seconds.")
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        input("Press Enter to exit...")
