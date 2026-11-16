# auth_client.py
import requests
import os

# ⚠️ آی‌پی کامپیوتر خود را اینجا وارد کنید
BASE_URL = "http://192.168.1.5:8000"  # <--- این را با آی‌پی خود عوض کنید

def check_login(username, password):
    try:
        r = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
        if r.status_code == 200:
            return r.json().get("role")
        return None
    except Exception as e:
        print("Login Error:", e)
        return None

def register_user(fullname, phone, national, password, role="user", shaba="", garadad=""):
    try:
        r = requests.post(f"{BASE_URL}/register", json={
            "fullname": fullname, "phone": phone, "national": national, 
            "password": password, "role": role, "shaba": shaba, "garadad": garadad
        })
        return r.status_code == 200
    except Exception:
        return False

def add_restaurant(name, food, capacity, category, host_username=None, price="", address="", location="", phone="", image_path=None, date_start="", date_finish="", time_start="", time_finish=""):
    try:
        r = requests.post(f"{BASE_URL}/restaurants", json={
            "name": name, "food": food, "capacity": int(capacity), "category": category, 
            "host_username": host_username, "price": price, "address": address, 
            "location": location, "phone": phone, "image_path": image_path,
            "date_start": date_start, "date_finish": date_finish, 
            "time_start": time_start, "time_finish": time_finish
        })
        return r.status_code == 200
    except Exception:
        return False

def update_service(name, food, capacity, price, address, phone, date_start, date_finish, time_start, time_finish, host_username):
    try:
        r = requests.put(f"{BASE_URL}/restaurants/{name}", json={
            "food": food, "capacity": int(capacity), "price": price, 
            "address": address, "phone": phone, 
            "date_start": date_start, "date_finish": date_finish, 
            "time_start": time_start, "time_finish": time_finish, 
            "host_username": host_username
        })
        return r.status_code == 200
    except Exception:
        return False

def get_restaurants():
    try:
        r = requests.get(f"{BASE_URL}/restaurants")
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def get_restaurants_SelectDay(date):
    try:
        r = requests.get(f"{BASE_URL}/restaurants/{date}")
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def make_reservation(restaurant_name, host_fullname, services, date, time, count, cost_person, cost_total, cost_app, final_cost, guest_username, category="", address="", host_phone="", tracking_code="", host_username=""):
    try:
        r = requests.post(f"{BASE_URL}/reserve", json={
            "restaurant_name": restaurant_name, "host_fullname": host_fullname, "services": services,
            "date": date, "time": time, "count": count, "cost_person": cost_person,
            "cost_total": cost_total, "cost_app": cost_app, "final_cost": final_cost,
            "guest_username": guest_username, "category": category, "address": address,
            "host_phone": host_phone, "tracking_code": tracking_code, "host_username": host_username
        })
        return r.status_code == 200
    except Exception:
        return False

def get_reservations_for_user(username):
    try:
        r = requests.get(f"{BASE_URL}/reservations/user/{username}")
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def get_services_by_host(host_username):
    try:
        r = requests.get(f"{BASE_URL}/host_services/{host_username}")
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def get_reservations_for_host(host_username):
    try:
        r = requests.get(f"{BASE_URL}/reservations/host/{host_username}")
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []
    
# این تابع برای آپلود عکس است (اختیاری، اگر عکس دارید)
def upload_image(file_path):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            r = requests.post(f"{BASE_URL}/upload", files=files)
            if r.status_code == 200:
                return r.json().get("path")
        return None
    except Exception:
        return None
