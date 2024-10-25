import sqlite3
import math
import pandas as pd
from rapidfuzz import process
from geopy.geocoders import Nominatim
from typing import Any, Coroutine, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict

class ActionCheckNearestHospital(Action):
    def name(self) -> Text:
        return "action_check_nearest_hospital"
    
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0 # Earth radius in kilometers

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    @staticmethod
    def get_coordinate(location):
        geolocator = Nominatim(user_agent="my_geolocation_app")
        loc = geolocator.geocode(location)
        if loc:
            return loc.latitude, loc.longitude
        return None, None

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        patient_addr = tracker.get_slot('address')
        
        if not patient_addr:
            dispatcher.utter_message(text="Saya belum mengenal alamat Anda, bisa Anda sebutkan alamat lengkap Anda?")
            return []
        
        user_lat, user_lon = self.get_coordinate(patient_addr)

        if user_lat is None or user_lon is None:
            dispatcher.utter_message(text="Maaf, saya tidak dapat menemukan koordinat untuk alamat yang Anda berikan.")
            return []

        try:
            conn = sqlite3.connect("./db/hospital_db.sqlite")
            cursor = conn.cursor()

            cursor.execute("SELECT nama_rs, latitude, longitude FROM info_lokasi_faskes")
            hospitals = cursor.fetchall()

            nearby_places = []
            for hospital in hospitals:
                name, place_lat, place_lon = hospital
                haversine_distance = self.haversine(user_lat, user_lon, place_lat, place_lon)
                nearby_places.append((name, haversine_distance))
            
            nearby_places.sort(key=lambda x: x[1])

            if nearby_places:
                nearest_hospital, distance = nearby_places[0]
                message = f"Rumah sakit terdekat dari lokasi Anda adalah {nearest_hospital} yang berjarak sejauh {distance:.2f} km."
                dispatcher.utter_message(text=message)
                
                # Debugging log
                print(f"Nearest hospital found: {nearest_hospital}")
                
                return [SlotSet("hospital", nearest_hospital)]
                
            else:
                dispatcher.utter_message(text="Maaf, tidak ada rumah sakit terdekat yang ditemukan.")
                return []

        except sqlite3.Error as e:
            dispatcher.utter_message(text="Mohon maaf, terdapat kendala dalam mengakses database internal.")
            print(f"Database error: {e}")
            return []

        finally:
            conn.close()


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
    

class ActionStoreLocationEntityToSlot(Action):
    def name(self) -> Text:
        return "action_store_location_to_slot"
    
    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain:  Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Try to get location from entities in latest message
        location = None

        # Extract location from entities
        for entity in tracker.latest_message.get('entities', []):
            if entity['entity'] == 'location':
                location = entity["value"]
                break
        
        return [SlotSet("loc", location)]


class ActionStoreHospitalNameToSlot(Action):
    def name(self) -> Text:
        return "action_store_hospital_name_to_slot"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Try to get hospital name from entities in latest message
        hospital_name = None

        # Extract hospital name from entities
        for entity in tracker.latest_message.get('entities', []):
            if entity['entity'] == 'hospital_name':
                hospital_name = entity["value"]
                break

        return [SlotSet("similar_name", hospital_name)]
    

class ActionListSimilarHospitalName(Action):
    def name(self) -> Text:
        return "action_list_all_similar_hospital"
    
    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get location from slot
        addr = tracker.get_slot('address')
        if not addr:
            message = "Untuk mendapatkan informasi rumah sakit yang anda maksud, \
                kami membutuhkan informasi lokasi anda, \
                bisakah anda memberikan alamat domisili anda sekarang?"
            dispatcher.utter_message(text=message)
            return []
        
        # Get hospital from slot
        hospital = tracker.get_slot('similar_name')
        if not hospital:
            message = "Rumah sakit yang anda cari sepertinya belum terdaftar dalam sistem kami."
            dispatcher.utter_message(text=message)
            return []
        
        # Debug logging
        print(f"Hospital from entity: {hospital}")
        print(f"Address from entity: {addr}")
        print(f"Latest message: {tracker.latest_message}")


        # Connect to SQLite database
        conn = sqlite3.connect("./db/hospital_db.sqlite")
        cursor = conn.cursor()

        # Query to retrieve all hospitals and their addresses
        query = "SELECT nama_rs, alamat || ' ' || alamat2 AS full_address FROM info_lokasi_faskes"
        cursor.execute(query)
        all_hospitals = cursor.fetchall()

        # Close the connection
        conn.close()

        # Use rapidfuzz to get the best matches based on similarity
        hospital_names = [result[0] for result in all_hospitals]
        matches = process.extract(hospital, hospital_names, score_cutoff=70)
        
        if matches:
            matched_hospitals = [match[0] for match in matches]
            message = f"Berikut ini adalah rumah sakit yang mirip dengan '{hospital}' di sekitar {addr}: " + ", ".join(matched_hospitals)
        else:
            message = "Tidak ditemukan rumah sakit di lokasi tersebut yang mirip dengan nama yang diberikan."

        # Send response to the user
        dispatcher.utter_message(text=message)
    

class ActionListHospitalNameBasedLocation(Action):
    def name(self) -> Text:
        return "action_list_hospital_name_based_location"
    
    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain:  Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Try to get location from entities in latest message
        location = None

        # Extract location from entities
        for entity in tracker.latest_message.get('entities', []):
            if entity['entity'] == 'location':
                location = entity["value"]
                break
        
        # Debug logging
        print(f"Location from entity: {location}")
        print(f"Latest message: {tracker.latest_message}")
        print(f"Current slots: {tracker.slots}")
        
        if not location:
            dispatcher.utter_message(text="Mohon maaf, rumah sakit di lokasi tersebut belum tersedia atau belum terdaftar.")
            return []

        # Connect to SQLite database
        conn = sqlite3.connect("./db/hospital_db.sqlite")
        cursor = conn.cursor()

        # Query for similar hospital names
        query = """SELECT nama_rs, alamat || ' ' || alamat2 AS full_address
        FROM info_lokasi_faskes 
        WHERE (alamat || ' ' || alamat2) LIKE ?"""
        cursor.execute(query, ('%' + location + '%',))
        results = cursor.fetchall()

        # Format the result
        if results:
            hospital_list = [result[0] for result in results]
            message = f"""Berikut ini adalah rumah sakit yang berada di {location}: """ + ", ".join(hospital_list)
        else:
            message = "Tidak ditemukan rumah sakit di lokasi tersebut."

        # Send response to the user
        dispatcher.utter_message(text=message)

        # Close the connection
        conn.close()
        
        return [SlotSet("loc", location)]
