import xml.etree.ElementTree as ET
import sys

# Register namespace
ET.register_namespace('', "http://www.opengis.net/kml/2.2")
ns = {'kml': 'http://www.opengis.net/kml/2.2'}

def finalize_kml(input_file, output_file, remove_points=False):
    print(f"Reading {input_file}...")
    tree = ET.parse(input_file)
    root = tree.getroot()
    document = root.find('kml:Document', ns)
    
    # Create a new Folder element for the points
    points_folder = ET.Element('Folder')
    name_elem = ET.SubElement(points_folder, 'name')
    name_elem.text = "Data Points"
    
    # We will iterate and move things around
    placemarks = document.findall('kml:Placemark', ns)
    
    # Remove all placemarks from Document first (we will add them back in order)
    for pm in placemarks:
        document.remove(pm)
        
    line_placemark = None
    points_count = 0
    
    for pm in placemarks:
        if pm.find('kml:LineString', ns) is not None:
            line_placemark = pm
            # Give the LineString a name
            name_tag = pm.find('kml:name', ns)
            if name_tag is None:
                name_tag = ET.SubElement(pm, 'name')
            name_tag.text = "Track Path"
        elif pm.find('kml:Point', ns) is not None:
            if not remove_points:
                points_folder.append(pm)
                points_count += 1
    
    # Add the LineString back to Document
    if line_placemark is not None:
        document.append(line_placemark)
    else:
        print("Warning: No LineString path found.")
        
    # Add the Folder back to Document (if we are keeping points)
    if not remove_points and points_count > 0:
        document.append(points_folder)
        print(f"Moved {points_count} points into 'Data Points' folder.")
    elif remove_points:
        print(f"Removed {points_count} points.")
        
    tree.write(output_file, encoding='UTF-8', xml_declaration=True)
    print(f"Written to {output_file}")

if __name__ == "__main__":
    # Default behavior: Keep points but group them. 
    # To remove points, change remove_points=True
    finalize_kml("culled.kml", "final_track.kml", remove_points=False)
