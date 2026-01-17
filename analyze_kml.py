import xml.etree.ElementTree as ET
from datetime import datetime
import statistics
import argparse

# Register namespace
ET.register_namespace('', "http://www.opengis.net/kml/2.2")
ns = {'kml': 'http://www.opengis.net/kml/2.2'}

def analyze_kml(file_path):
    print(f"Analyzing {file_path}...")
    try:
        tree = ET.parse(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    root = tree.getroot()
    document = root.find('kml:Document', ns)
    
    if document is None:
        print("Invalid KML: Document not found")
        return

    placemarks = document.findall('kml:Placemark', ns)
    
    timestamps = []
    
    for pm in placemarks:
        ts_element = pm.find('kml:TimeStamp', ns)
        if ts_element is not None:
            when = ts_element.find('kml:when', ns)
            if when is not None:
                ts_str = when.text.replace('Z', '+00:00')
                try:
                    dt = datetime.fromisoformat(ts_str)
                    timestamps.append(dt)
                except ValueError:
                    pass
    
    timestamps.sort()
    
    deltas = []
    for i in range(1, len(timestamps)):
        diff = (timestamps[i] - timestamps[i-1]).total_seconds()
        if diff > 0: # Filter out duplicates if any remain or 0-second diffs
            deltas.append(diff)
            
    if not deltas:
        print("No time intervals found.")
        return

    print(f"Total points: {len(timestamps)}")
    print(f"Min interval: {min(deltas)}s")
    print(f"Max interval: {max(deltas)}s")
    print(f"Mean interval: {statistics.mean(deltas):.2f}s")
    print(f"Median interval: {statistics.median(deltas):.2f}s")
    
    # Check what % of data is under 1 minute
    under_60 = sum(1 for d in deltas if d <= 60)
    print(f"Intervals <= 60s: {under_60 / len(deltas) * 100:.1f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze time intervals in a KML file.")
    parser.add_argument("--input", default="merged.kml", help="Input KML file (default: merged.kml)")
    
    args = parser.parse_args()
    
    analyze_kml(args.input)