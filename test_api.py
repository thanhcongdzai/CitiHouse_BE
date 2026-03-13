import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/users/"

sample_user = {
  "firstName": "Tran",
  "lastName": "Binh",
  "phone": "0901000002",
  "role": "Broker"
}

def test_api():
    print("1. Testing POST (Create User)")
    res = requests.post(BASE_URL, json=sample_user)
    print("Status:", res.status_code)
    try:
        created_data = res.json()
        print("Response:", json.dumps(created_data, indent=2))
        apt_id = created_data.get("id")
    except Exception as e:
        print("Failed to parse JSON:", res.text)
        return

    print("\n2. Testing GET (List Users)")
    res = requests.get(BASE_URL)
    print("Status:", res.status_code)
    try:
        print("Total items:", len(res.json()))
    except Exception as e:
        print("Failed to parse JSON")

    print(f"\n3. Testing GET (Retrieve User {apt_id})")
    res = requests.get(f"{BASE_URL}{apt_id}/")
    print("Status:", res.status_code)

    print(f"\n4. Testing PUT (Update User {apt_id})")
    update_data = sample_user.copy()
    update_data["firstName"] = "Nguyen"
    res = requests.put(f"{BASE_URL}{apt_id}/", json=update_data)
    print("Status:", res.status_code)
    try:
        print("Updated Name:", res.json().get("firstName"))
    except:
        pass

    print(f"\n5. Testing DELETE (Delete User {apt_id})")
    res = requests.delete(f"{BASE_URL}{apt_id}/")
    print("Status:", res.status_code)

    print(f"\n6. Verify DELETE (Retrieve User {apt_id})")
    res = requests.get(f"{BASE_URL}{apt_id}/")
    print("Status:", res.status_code)

if __name__ == "__main__":
    time.sleep(1)
    test_api()
