import json
import random
import os

def generate_parking_spots():
    spots = []
    for i in range(1, 1000):
        # Generate random price between 100 and 300 BYN
        price = round(random.uniform(100, 300), 2)
        
        spot = {
            "model": "myparking.parkingspot",
            "pk": i,
            "fields": {
                "number": i,
                "price": f"{price:.2f}",
                "currency": "BYN",
                "is_busy": False,
                "user": None,
                "date_of_rent": None,
                "last_payment_date": None,
                "paid_months": 0,
                "next_payment_date": None
            }
        }
        spots.append(spot)
    
    # Ensure the directory exists
    os.makedirs('myparking/fixtures', exist_ok=True)
    
    # Write to file
    with open('myparking/fixtures/parking_spots.json', 'w', encoding='utf-8') as f:
        json.dump(spots, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    generate_parking_spots() 