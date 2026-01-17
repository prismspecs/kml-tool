import xml.etree.ElementTree as ET
from datetime import datetime
import math

# Register namespace
ET.register_namespace('', "http://www.opengis.net/kml/2.2")
ns = {'kml': 'http://www.opengis.net/kml/2.2'}

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Radius of Earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def parse_coordinate_string(coord_str):
    # KML coords are "lon,lat,alt" or "lon,lat"
    parts = coord_str.strip().split(',')
    return float(parts[1]), float(parts[0]) # lat, lon

def cull_kml(input_file, output_file, min_distance_meters=50):
    print(f"Reading {input_file}...")
    tree = ET.parse(input_file)
    root = tree.getroot()
    document = root.find('kml:Document', ns)
    
    # We need to process both individual Placemarks (Points) and the LineString
    placemarks = document.findall('kml:Placemark', ns)
    
    # Separate LineString (path) from Points (markers)
    path_placemark = None
    point_placemarks = []
    
    for pm in placemarks:
        if pm.find('kml:LineString', ns) is not None:
            path_placemark = pm
        elif pm.find('kml:Point', ns) is not None:
            point_placemarks.append(pm)
            
    # Sort points by time just in case (assuming we can parse them)
    # The merge script already sorted them, but let's be safe if this is run independently
    def get_time(pm):
        ts = pm.find('kml:TimeStamp', ns)
        if ts is not None:
            when = ts.find('kml:when', ns)
            if when is not None:
                return when.text
        return ""
    
    point_placemarks.sort(key=get_time)
    
    kept_points = []
    last_kept_coords = None
    
    print(f"Total input points: {len(point_placemarks)}")
    
    for pm in point_placemarks:
        point = pm.find('kml:Point', ns)
        coords_text = point.find('kml:coordinates', ns).text
        lat, lon = parse_coordinate_string(coords_text)
        
        if last_kept_coords is None:
            kept_points.append(pm)
            last_kept_coords = (lat, lon)
        else:
            dist = haversine_distance(last_kept_coords[0], last_kept_coords[1], lat, lon)
            if dist >= min_distance_meters:
                kept_points.append(pm)
                last_kept_coords = (lat, lon)
                
    print(f"Points kept after {min_distance_meters}m culling: {len(kept_points)}")
    print(f"Reduction: {(1 - len(kept_points)/len(point_placemarks))*100:.1f}%")
    
    # Update the Document: remove old placemarks, add kept ones
    # We first clear the document of placemarks
    for pm in placemarks:
        document.remove(pm)
        
    # Rebuild the LineString from kept points
    if path_placemark is not None:
        ls = path_placemark.find('kml:LineString', ns)
        coord_elem = ls.find('kml:coordinates', ns)
        
        new_coords_list = []
        for pm in kept_points:
            p_elem = pm.find('kml:Point', ns)
            c_text = p_elem.find('kml:coordinates', ns).text.strip()
            new_coords_list.append(c_text)
            
        coord_elem.text = "\n".join(new_coords_list)
        document.append(path_placemark)
        
    # Add back the filtered points
    for pm in kept_points:
        document.append(pm)
        
    tree.write(output_file, encoding='UTF-8', xml_declaration=True)
    print(f"Written to {output_file}")

if __name__ == "__main__":
    # You can adjust the distance here (e.g., 50 meters)
    cull_kml("merged.kml", "culled.kml", min_distance_meters=50)
