from scrapling.fetchers import DynamicFetcher
import openpyxl
from datetime import datetime

def scrape_artstation_studios():
    url = "https://www.artstation.com/jobs/studios"
    print(f"Scraping {url}...")
    
    # Use DynamicFetcher for ArtStation
    page = DynamicFetcher.fetch(url)
    
    # We need to find the studio names and their links
    # Based on ArtStation's structure, they might be in cards
    studios = []
    
    # Let's inspect the page text first to see what's there
    # print(page.get_all_text()[:500])
    
    # Let's try some common selectors for ArtStation
    # Studio cards are usually in a grid
    studio_cards = page.css(".studio-card")
    
    for card in studio_cards:
        name = card.css_first(".studio-card-name").text.strip()
        location = card.css_first(".studio-card-location").text.strip()
        # For now, let's just collect names and locations
        studios.append({
            "name": name,
            "location": location,
            "source": "ArtStation Jobs (Studios)"
        })
    
    return studios

if __name__ == "__main__":
    studios = scrape_artstation_studios()
    print(f"Found {len(studios)} studios.")
    for s in studios:
        print(s)
