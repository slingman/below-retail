import requests
from bs4 import BeautifulSoup
import json

# Define the sneaker deal website (example)
URL = "https://www.example.com/sneaker-deals"  # Replace with a real URL
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Extract sneaker deals (Modify based on actual website structure)
deals = []
for deal in soup.find_all("div", class_="deal-card"):
    name = deal.find("h2").text.strip()
    price = deal.find("span", class_="price").text.strip()
    link = deal.find("a")["href"]
   
    deals.append({"name": name, "price": price, "link": link})

# Save to JSON
with open("deals.json", "w") as f:
    json.dump(deals, f, indent=4)

print("Sneaker deals updated!")
