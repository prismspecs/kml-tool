# KML Processing Tools

This repository contains a set of Python scripts for processing, merging, and analyzing KML GPS data files.

## Workflow & Scripts

The scripts are designed to be run in a sequence, but can be used independently. All scripts support command-line arguments to specify input and output paths.

### 1. Merge (`merge_kml.py`)
- **Function**: Combines multiple KML files found in the specified directory.
- **Features**:
    - Deduplicates points based on ID.
    - Sorts points by timestamp.
    - Rebuilds the LineString track.
- **Arguments**:
    - `--input`: Input directory or glob pattern (default: `input`)
    - `--output`: Output file path (default: `output/merged.kml`)
- **Example**: `python merge_kml.py --input "data/*.kml" --output "result.kml"`

### 2. Cull (`cull_kml.py`)
- **Function**: Reduces the density of points by filtering out those that are too close to the previous point.
- **Arguments**:
    - `--input`: Input KML file (default: `merged.kml`)
    - `--output`: Output KML file (default: `culled.kml`)
    - `--distance`: Minimum distance in meters (default: 50)
- **Example**: `python cull_kml.py --input result.kml --output small.kml --distance 100`

### 3. Finalize (`finalize_kml.py`)
- **Function**: Structures the KML for final use (e.g., Google Earth). Groups points into a folder and ensures the LineString path is visible.
- **Arguments**:
    - `--input`: Input KML file (default: `culled.kml`)
    - `--output`: Output KML file (default: `final_track.kml`)
    - `--remove-points`: Flag to remove individual points and keep only the path.
- **Example**: `python finalize_kml.py --input small.kml --output final.kml --remove-points`

### 4. Analyze (`analyze_kml.py`)
- **Function**: Calculates statistics about the track, specifically time intervals between points to identify gaps or high-frequency data.
- **Arguments**:
    - `--input`: Input KML file (default: `merged.kml`)
- **Example**: `python analyze_kml.py --input final.kml`

## Usage

1. **Setup**:
   Ensure you have Python 3 installed. No external dependencies are required (uses standard libraries).

2. **Prepare Data**:
   Place your raw `.kml` files into a directory (default is `input/`).

3. **Run Merge**:
   ```bash
   python merge_kml.py
   ```
   This will generate `output/merged.kml` by default.

4. **(Optional) Clean & Finalize**:
   You can run the other scripts to refine the output:
   ```bash
   # Filter close points
   python cull_kml.py --input output/merged.kml
   
   # Organize structure
   python finalize_kml.py
   ```

## Dependencies

- Python 3.x
- Standard libraries: `xml.etree.ElementTree`, `datetime`, `math`, `statistics`, `glob`, `os`, `argparse`