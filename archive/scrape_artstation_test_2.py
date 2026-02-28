from scrapling.fetchers import DynamicFetcher
import openpyxl
from datetime import datetime

def scrape_artstation_studios():
    url = "https://www.artstation.com/jobs/studios"
    print(f"Scraping {url}...")
    
    # Use DynamicFetcher for ArtStation
    page = DynamicFetcher.fetch(url)
    
    # Let's inspect the page text first to see what's there
    text = page.get_all_text()
    print(f"Text content: {text[:500]}...")
    
    # Try searching for some common studio names or keywords
    # Studio names often are in h4 or a tags
    
    # Let's try some different selectors
    # Sometimes ArtStation uses .studio-card or similar
    # Let's try finding all links or titles
    
    # Looking at ArtStation, job cards have class "job-listing" or similar
    # But for studios, let's try to find studio names
    
    # Let's try finding all elements with class containing 'studio'
    # elements = page.css("[class*='studio']")
    # print(f"Found {len(elements)} elements with 'studio' in class.")
    
    # Let's try to find elements with some studio-related text
    # Or just find all h4, maybe?
    
    studios = []
    
    # Let's try to find all studio items
    # Looking at the site, they are often in a grid with class .gallery-grid
    # and each studio is a .studio-card-container or similar
    
    # Let's try to get all text and see if we can find studio names
    # Or just use a broader selector
    
    # For now, let's just print all text to understand the page structure
    # better.
    
    return studios

if __name__ == "__main__":
    studios = scrape_artstation_studios()
    print(f"Found {len(studios)} studios.")
