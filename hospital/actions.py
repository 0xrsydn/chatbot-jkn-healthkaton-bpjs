import sqlite3
import math
import pandas as pd
from geopy.geocoders import Nominatim
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionCheckNearestHospital(Action):
    def name(self) -> Text:
        return "action_check_nearest_hospital"
    
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0 # Earth radius in kilometers

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Distance in kilometers
        distance = R * c
        return distance

    @staticmethod
    def get_coordinate(location):
        # Use a more specific and unique user-agent string
        geolocator = Nominatim(user_agent="my_geolocation_app")
        
        # Get location
        loc = geolocator.geocode(location)
        
        # Return the latitude and longitude
        if loc:
            return loc.latitude, loc.longitude
        else:
            return None, None

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the patient address from the user's input
        patient_addr = tracker.get_slot('address')
        
        if not patient_addr:
            dispatcher.utter_message(text="Saya belum mengenal alamat Anda, bisa Anda sebutkan alamat lengkap Anda?")
            return []
        
        user_lat, user_lon = self.get_coordinate(patient_addr)

        if user_lat is None or user_lon is None:
            dispatcher.utter_message(text="Maaf, saya tidak dapat menemukan koordinat untuk alamat yang Anda berikan.")
            return []
        
        try:
            # Connect to the sqlite db
            conn = sqlite3.connect("./db/hospital_db.sqlite")
            cursor = conn.cursor()

            # Query all hospital with their latitudes and longitudes
            cursor.execute("SELECT nama_rs, latitude, longitude FROM info_lokasi_faskes")
            hospitals = cursor.fetchall()

            # List to hold places within the specified distance
            nearby_places = []

            for hospital in hospitals:
                name, place_lat, place_lon = hospital
                haversine_distance = self.haversine(user_lat, user_lon, place_lat, place_lon)
                nearby_places.append((name, haversine_distance))
            
            # Sort places by distance (ascending)
            nearby_places.sort(key=lambda x: x[1])

            conn.close()

            print(nearby_places)
            if nearby_places:
                nearest_hospital, distance = nearby_places[0]
                message = f"Rumah sakit terdekat dari lokasi Anda adalah {nearest_hospital} yang berjarak sejauh {distance:.2f} km."
                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(text="Maaf, saya tidak dapat menemukan rumah sakit terdekat dari lokasi Anda.")

        except sqlite3.Error as e:
            dispatcher.utter_message(text="Mohon maaf, terdapat kendala dalam mengakses database internal.")
            print(f"Database error: {e}")

        return []


class ActionCheckHospitalRoomAvailability(Action):
    def name(self) -> Text:
        return "action_check_hospital_room_availability"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the hospital name from the user's input
        hospital = tracker.get_slot('hospital')
        
        if not hospital:
            message = "Saya tidak mengenali rumah sakit yang anda cari, bisakah anda menyebutkannya secara spesifik?"
            dispatcher.utter_message(text=message)
            return []
        
        # Connect to the sqlite database
        conn = sqlite3.connect("./db/hospital_db.sqlite")
        cursor = conn.cursor()
        
        try:
            # Query to check room availability
            query = """SELECT nama_rs, tipe_kamar, total_kamar, ketersediaan
                FROM info_tempat_tidur
                WHERE nama_rs = ?"""
            
            df = pd.read_sql_query(query, conn, params=(hospital,))
            df = df[df['ketersediaan'] > 0]
            
            if df.empty:
                message = f"Maaf, tidak ada kamar yang tersedia di {hospital} saat ini."
            else:
                message = f"Informasi ketersediaan kamar di {hospital}:\n"
                for _, row in df.iterrows():
                    message += f"- Tipe kamar {row['tipe_kamar']} masih tersedia sebanyak {row['ketersediaan']} kamar.\n"
            
            dispatcher.utter_message(text=message)
        
        except sqlite3.Error as e:
            message = "Terdapat gangguan ketika mengakses database internal."
            dispatcher.utter_message(text=message)
            print(f"Database error: {e}")
        
        finally:
            # Close the database connection
            conn.close()
        
        return []
    

