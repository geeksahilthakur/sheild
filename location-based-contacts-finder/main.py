import googlemaps
API_KEY = 'ENTER_YOUR_API_KEY'
gmaps = googlemaps.Client(key=API_KEY)


def get_nearby_police_stations(location, radius=5000):
    # Geocoding the address to get coordinates
    geocode_result = gmaps.geocode(location)
    if not geocode_result:
        return "Invalid location."

    coords = geocode_result[0]['geometry']['location']

    # Search specifically for police stations
    places_result = gmaps.places_nearby(location=(coords['lat'],
                                                  coords['lng']),
                                        radius=radius,
                                        type='police')

    results = []

    if places_result['results']:
        for place in places_result['results']:
            place_id = place['place_id']
            details = gmaps.place(place_id=place_id)

            # Fetching phone number
            contact_info = details['result'].get('formatted_phone_number',
                                                 'Not available')

            # Fetching email address (rarely provided)
            email_info = details['result'].get('email', 'Not available')

            address = details['result'].get('formatted_address',
                                            'No address available')
            results.append({
                'Name': details['result'].get('name', 'Unknown'),
                'Address': address,
                'Phone Number': contact_info,
                'Email': email_info
            })
    else:
        results.append({
            'Name': 'Not Found',
            'Address': 'Not Available',
            'Phone Number': 'Not Available',
            'Email': 'Not Available'
        })

    return results


# Example usage
location_input = input(
    "Enter the location (e.g., '1600 Amphitheatre Parkway, Mountain View, CA'): "
)
police_stations_info = get_nearby_police_stations(location_input)

if isinstance(police_stations_info, str):
    print(police_stations_info)
else:
    for station in police_stations_info:
        print(f"Name: {station['Name']}")
        print(f"Address: {station['Address']}")
        print(f"Phone Number: {station['Phone Number']}")
        print(f"Email: {station['Email']}\n")
