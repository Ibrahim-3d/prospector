from scrapling import DynamicFetcher
import time
from .utils import save_to_json

def scrape_artstation():
    """
    Scrapes ArtStation Jobs using structured CSS selectors.
    """
    print("[...] Scraping ArtStation Jobs...")
    fetcher = DynamicFetcher()
    
    # ArtStation is JS-heavy, so we use DynamicFetcher (implicit in Fetcher for these URLs usually)
    
    leads = []
    
    for page_num in range(1, 4):
        url = f"https://www.artstation.com/jobs/all?page={page_num}"
        print(f"  -> Scraping page {page_num}...")
        try:
            # Using a longer wait for JS to render the job cards
            page = fetcher.fetch(url, timeout=30000, wait_selector="div.job-listing")
            
            if page.status not in [200, 404]: # ArtStation sometimes returns 200 with empty content if blocked
                 print(f"[!] ArtStation returned status {page.status}")
            
            jobs = page.css("div.job-listing")
            if not jobs:
                break # Stop if no more jobs found
            
            for job in jobs:
                title_el = job.css(".job-listing-header-title").first
                company_el = job.css(".job-listing-header-company").first
                info_el = job.css(".job-listing-header-info").first
                posted_el = job.css(".text-small.text-white").first
                
                if not title_el or not company_el:
                    continue
                    
                title = title_el.text.strip()
                company = company_el.text.strip()
                job_url = page.urljoin(title_el.attrib.get('href', ''))
                company_url = page.urljoin(company_el.attrib.get('href', ''))
                location = info_el.text.strip() if info_el else "Remote/Unknown"
                posted = posted_el.text.strip() if posted_el else "Recently"
                
                # Extract tags/labels
                labels = [l.text.strip() for l in job.css(".job-item-info-label")]
                
                # Simple location parsing
                country = "Unknown"
                city = location
                if "," in location:
                    parts = [p.strip() for p in location.split(",")]
                    city = parts[0]
                    country = parts[-1]
                elif location.lower() == "remote":
                    country = "Remote"
                    city = "Remote"

                leads.append({
                    "company": company,
                    "country": country,
                    "city": city,
                    "category": "Studio/Agency",
                    "source": "ArtStation",
                    "demand_signal": f"Hiring: {title} ({posted})",
                    "service_needed": "3D/Motion Design",
                    "website": company_url, # ArtStation company profile
                    "notes": f"Job URL: {job_url} | Tags: {', '.join(labels)}",
                    "priority": "A+" if any(x in title.lower() for x in ["3d", "motion", "cgi", "unreal"]) else "A"
                })

        except Exception as e:
            print(f"[ERROR] ArtStation scraping failed on page {page_num}: {e}")
            break

    print(f"[OK] Found {len(leads)} jobs on ArtStation.")
    save_to_json(leads, 'leads_artstation.json')
    return leads
