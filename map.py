import folium

# Define the list of cities with their coordinates
cities_coordinates = {
    "Jerusalem": (31.7683, 35.2137),
    "Bethany": (31.7625, 35.2603),
    "Joppa (Jaffa)": (32.0554, 34.7522),
    "Caesarea": (32.5000, 34.9000),
    "Antioch": (36.2021, 36.1606),
    "Nazareth": (32.6996, 35.3035),
    "Tarsus": (36.9173, 34.8916),
    "Lystra": (37.5714, 32.3009),
    "Derbe": (37.3500, 33.3500),
    "Iconium (Konya)": (37.8747, 32.4932),
    "Ephesus": (37.9394, 27.3416),
    "Miletus": (37.5300, 27.2700),
    "Smyrna (Izmir)": (38.4192, 27.1287),
    "Pergamum": (39.1200, 27.1800),
    "Thyatira": (38.9183, 27.8378),
    "Sardis": (38.4886, 28.0383),
    "Philadelphia": (38.4710, 28.3594),
    "Laodicea": (37.8314, 29.0910),
    "Philippi": (41.0153, 24.2866),
    "Thessalonica": (40.6401, 22.9444),
    "Berea (Veria)": (40.5236, 22.2029),
    "Athens": (37.9838, 23.7275),
    "Corinth": (37.9381, 22.9322),
    "Neapolis (Kavala)": (40.9396, 24.4129),
    "Puteoli (Pozzuoli)": (40.8223, 14.1218),
    "Rome": (41.9028, 12.4964),
    "Cyprus": (35.1264, 33.4299),
    "Salamis": (35.1667, 33.9000),
    "Paphos": (34.7754, 32.4245),
    "Patara": (36.2667, 29.3167),
    "Tyre": (33.2700, 35.2033),
    "Colossae": (37.7925, 29.0861),
    "Galatia": (39.5000, 32.5000),
    "Crete": (35.2401, 24.8093),
    "Pontus": (40.0000, 36.0000),
    "Cappadocia": (38.6421, 34.8278),
    "Asia (Roman province)": (39.0000, 28.0000),
    "Bithynia": (40.5000, 30.0000),
    "Macedonia": (41.0000, 22.0000),
    "Troas": (39.8333, 26.1667),
    "Syria": (34.8021, 38.9968),
    "Cyrene": (32.8231, 21.8639),
    "Alexandria": (31.2001, 29.9187),
}

# Main function
def main():
    # Create a map centered around a central location
    m = folium.Map(location=[34.8021, 38.9968], zoom_start=5)

    # Add markers for each city
    for city, coord in cities_coordinates.items():
        folium.Marker(location=coord, popup=city).add_to(m)

    # Save the map to an HTML file
    m.save("historical_cities_map.html")

# Main entry point
if __name__ == "__main__":
    main()
