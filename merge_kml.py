import os
import glob
import xml.etree.ElementTree as ET
from datetime import datetime

# Register namespace to avoid ns0: prefixes
ET.register_namespace('', "http://www.opengis.net/kml/2.2")
ns = {'kml': 'http://www.opengis.net/kml/2.2'}

def get_text(element, path):
    found = element.find(path, ns)
    return found.text if found is not None else None

def parse_kml_files():
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    kml_files = glob.glob("input/*.kml")
    
    print(f"Found files: {kml_files}")

    unique_points = {} # Key: ID, Value: (timestamp_obj, placemark_element)
    
    # We need a template for the output file (Styles, Document root)
    template_tree = None
    template_root = None
    
    for file_path in kml_files:
        print(f"Processing {file_path}...")
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        if template_tree is None:
            template_tree = tree
            template_root = root
        
        document = root.find('kml:Document', ns)
        if document is None:
            continue
            
        placemarks = document.findall('kml:Placemark', ns)
        
        for pm in placemarks:
            # Check if it is a Point placemark with ExtendedData (ID)
            extended_data = pm.find('kml:ExtendedData', ns)
            
            # If it has a Point and ExtendedData, we treat it as a track point
            point = pm.find('kml:Point', ns)
            
            if point is not None and extended_data is not None:
                # Try to find ID in ExtendedData
                data_id = None
                for data in extended_data.findall('kml:Data', ns):
                    if data.get('name') == 'id':
                        val = data.find('kml:value', ns)
                        if val is not None:
                            data_id = val.text
                        break
                
                # Try to find timestamp
                timestamp_str = None
                ts_element = pm.find('kml:TimeStamp', ns)
                if ts_element is not None:
                    when = ts_element.find('kml:when', ns)
                    if when is not None:
                        timestamp_str = when.text
                
                if data_id and timestamp_str:
                    # Parse timestamp for sorting
                    # Format example: 2026-01-11T14:33:00Z
                    try:
                        # minimal parsing handling Z
                        ts_str_clean = timestamp_str.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(ts_str_clean)
                        
                        if data_id not in unique_points:
                            unique_points[data_id] = (dt, pm)
                    except ValueError as e:
                        print(f"Error parsing date {timestamp_str}: {e}")
    
    print(f"Total unique points found: {len(unique_points)}")
    
    # Sort points by timestamp
    sorted_points = sorted(unique_points.values(), key=lambda x: x[0])
    
    # Reconstruct the Output KML
    if template_root is None:
        print("No valid KML input found.")
        return

    # Clear existing Placemarks from the template Document
    document = template_root.find('kml:Document', ns)
    
    # We want to keep Styles, but remove all Placemarks (both LineStrings and Points)
    # Because we will rebuild the LineString and add back sorted Points
    original_placemarks = document.findall('kml:Placemark', ns)
    for pm in original_placemarks:
        document.remove(pm)
        
    # 1. Create and add the combined LineString Placemark
    # We need coordinates from all sorted points
    all_coords = []
    for dt, pm in sorted_points:
        point = pm.find('kml:Point', ns)
        coords = point.find('kml:coordinates', ns).text.strip()
        all_coords.append(coords)
    
    # Combine coordinates string
    # KML LineString coordinates are space separated tuples
    line_string_coords = "\n".join(all_coords)
    
    # Create the LineString Placemark
    # We try to copy the style from the first file's LineString if possible, 
    # but for now we'll create a generic one or try to reuse if we saved it?
    # Actually, simpler: just use a hardcoded style or one found in styles.
    # In the input file, the LineString had styleUrl #devicecolor_...
    # Let's try to preserve the LineString style from the template file.
    
    # To do that, let's re-read the first file to find the original LineString Placemark
    # and use it as a base.
    first_file = kml_files[0]
    temp_tree = ET.parse(first_file)
    temp_root = temp_tree.getroot()
    temp_doc = temp_root.find('kml:Document', ns)
    temp_pms = temp_doc.findall('kml:Placemark', ns)
    
    line_placemark_template = None
    for pm in temp_pms:
        if pm.find('kml:LineString', ns) is not None:
            line_placemark_template = pm
            break
            
    if line_placemark_template is not None:
        # Update coordinates
        ls = line_placemark_template.find('kml:LineString', ns)
        coord_elem = ls.find('kml:coordinates', ns)
        coord_elem.text = line_string_coords
        
        # Add to document
        document.append(line_placemark_template)
    else:
        print("Warning: Could not find a template LineString placemark.")

    # 2. Add all sorted Point Placemarks
    for dt, pm in sorted_points:
        document.append(pm)
        
    # Write output
    output_path = "output/merged.kml"
    template_tree.write(output_path, encoding='UTF-8', xml_declaration=True)
    print(f"Successfully wrote {output_path}")

if __name__ == "__main__":
    parse_kml_files()
