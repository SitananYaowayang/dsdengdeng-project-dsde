from geopy.geocoders import Nominatim

# สร้าง geolocator (ต้องตั้ง user_agent)
geolocator = Nominatim(user_agent="geo_example")

address = "26 ซอยลาดพร้าว 26 จอมพล จตุจักร กรุงเทพ"

location = geolocator.geocode(address)

if location:
    print("Latitude:", location.latitude)
    print("Longitude:", location.longitude)
else:
    print("ไม่พบพิกัด")
