import cloudscraper

url = "https://www.heureka.cz/direct/dotaznik/export-review.php?key=92e89a3db1d387c08989d130cf1977f0"

scraper = cloudscraper.create_scraper()
response = scraper.get(url)

if response.status_code != 200:
    raise Exception(f"Failed: HTTP {response.status_code}")

if "<review>" not in response.text:
    raise Exception(f"No reviews in response. Got: {response.text[:200]}")

with open("data/reviews.xml", "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"Saved successfully. Size: {len(response.text)} bytes")
