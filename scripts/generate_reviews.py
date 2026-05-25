import urllib.request

url = "https://www.heureka.cz/direct/dotaznik/export-review.php?key=92e89a3db1d387c08989d130cf1977f0"

req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
})

with urllib.request.urlopen(req) as response:
    xml_data = response.read()

with open("data/reviews.xml", "wb") as f:
    f.write(xml_data)

print("reviews.xml saved successfully")
