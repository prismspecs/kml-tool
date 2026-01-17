# KML Processing Tools

This repository contains a set of Python scripts for processing, merging, and analyzing KML GPS data files.

## Workflow & Scripts

The scripts are designed to be run in a sequence, but can be used independently if input files match expected names.

### 1. Merge (`merge_kml.py`)
- **Function**: Combines multiple KML files found in the `input/` directory.
- **Features**:
    - Deduplicates points based on ID.
    - Sorts points by timestamp.
    - Rebuilds the LineString track.
- **Input**: `input/*.kml`
- **Output**: `output/merged.kml`

### 2. Cull (`cull_kml.py`)
- **Function**: Reduces the density of points by filtering out those that are too close to the previous point.
- **Default**: 50 meters minimum distance.
- **Input**: `merged.kml` (or specified)
- **Output**: `culled.kml`

### 3. Finalize (`finalize_kml.py`)
- **Function**: Structures the KML for final use (e.g., Google Earth). Groups points into a folder and ensures the LineString path is visible.
- **Input**: `culled.kml` (or specified)
- **Output**: `final_track.kml`

### 4. Analyze (`analyze_kml.py`)
- **Function**: Calculates statistics about the track, specifically time intervals between points to identify gaps or high-frequency data.
- **Input**: `merged.kml` (or specified)

## Usage

1. **Setup**:
   Ensure you have Python 3 installed. No external dependencies are required (uses standard libraries).

2. **Prepare Data**:
   Place your raw `.kml` files into a directory named `input/`.

3. **Run Merge**:
   ```bash
   python merge_kml.py
   ```
   This will generate `output/merged.kml`.

4. **(Optional) Clean & Finalize**:
   You can run the other scripts to refine the output:
   ```bash
   # Filter close points
   python cull_kml.py
   
   # Organize structure
   python finalize_kml.py
   ```

## Dependencies

- Python 3.x
- Standard libraries: `xml.etree.ElementTree`, `datetime`, `math`, `statistics`, `glob`, `os`
