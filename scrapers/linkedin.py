from scrapling import StealthyFetcher
import time
from .utils import save_to_json, save_debug_html

def scrape_linkedin():
    """
    Scrapes LinkedIn Jobs using StealthyFetcher and structured selectors.
    Focuses on UAE 3D/Motion roles.
    """
    print("[...] Scraping LinkedIn Jobs (UAE)...")
    # Using StealthyFetcher for high-protection site
    stealth = StealthyFetcher()
    
    # Query: 3D Artist, Motion Designer, CGI - Location: UAE - Past month
    url = "https://www.linkedin.com/jobs/search/?keywords=3d%20artist%20motion%20designer%20cgi&location=United%20Arab%20Emirates&f_TPR=r2592000"
    
    try:
        # Use stealthy fetch
        page = stealth.fetch(url, timeout=40000, wait_selector="div.base-card")
        
        # Save HTML for debugging if no results found
        if not page.css("div.base-card"):
            save_debug_html(page.text, "linkedin")
            print("[!] LinkedIn search yielded no results (or blocked). Check debug_linkedin_html.html")
            
        cards = page.css("div.base-card")
        leads = []
        
        for card in cards:
            title_el = card.css("h3.base-search-card__title").first
            company_el = card.css("h4.base-search-card__subtitle a").first
            location_el = card.css("span.job-search-card__location").first
            date_el = card.css("time.job-search-card__listdate").first or card.css("time.job-search-card__listdate--new").first
            link_el = card.css("a.base-card__full-link").first
            
            if not title_el or not company_el:
                continue
                
            title = title_el.text.strip()
            company = company_el.text.strip()
            location = location_el.text.strip() if location_el else "UAE"
            posted_date = date_el.attrib.get("datetime", "Unknown") if date_el else "Recent"
            job_url = link_el.attrib.get("href", "").split("?")[0] # Clean URL
            
            # Simple location parsing for UAE cities
            city = location
            if "," in location:
                parts = [p.strip() for p in location.split(",")]
                city = parts[0]
            
            leads.append({
                "company": company,
                "country": "UAE",
                "city": city,
                "category": "LinkedIn Target",
                "source": "LinkedIn",
                "demand_signal": f"Hiring: {title} ({posted_date})",
                "service_needed": "3D/Motion Design",
                "notes": f"Job Title: {title} | Location: {location} | Link: {job_url}",
                "priority": "A+" if any(x in title.lower() for x in ["3d", "motion", "unreal", "cgi"]) else "A"
            })

        print(f"[OK] Found {len(leads)} LinkedIn leads.")
        save_to_json(leads, 'leads_linkedin.json')
        return leads

    except Exception as e:
        print(f"[ERROR] LinkedIn scraping failed: {e}")
        return []
