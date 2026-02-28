from scrapling import StealthyFetcher
import time
from urllib.parse import quote_plus
from .utils import save_to_json, save_debug_html
from .llm_enricher import enrich_job_lead

def scrape_linkedin(queries=None, regions=None):
    """
    Scrapes LinkedIn Jobs using StealthyFetcher and structured selectors.
    Enriches with Gemini. Works across multiple regions.
    """
    if not queries:
        queries = ["3D Artist OR Motion Designer OR CGI"]
    if not regions:
        regions = ["United Arab Emirates"]

    print(f"[...] Scraping LinkedIn Jobs for {len(regions)} regions and {len(queries)} queries...")
    stealth = StealthyFetcher()
    leads = []
    
    for region in regions:
        for query in queries:
            print(f"\n[➡] LinkedIn Search: {query} in {region}")
            
            # URl encodes strings for safer request construction
            safe_query = quote_plus(query)
            safe_region = quote_plus(region)
            
            url = f"https://www.linkedin.com/jobs/search/?keywords={safe_query}&location={safe_region}&f_TPR=r2592000"
            
            try:
                # Fetch without strict wait_selector
                page = stealth.fetch(url, timeout=60000)
                save_debug_html(page, f"linkedin_{region}")
                
                cards = page.css("div.base-card, .base-search-card")
                if not cards:
                    print("  [!] No cards found for this query.")
                    continue
                    
                for card in cards:
                    title_el = card.css("h3.base-search-card__title").first
                    company_el = card.css("h4.base-search-card__subtitle a").first
                    location_el = card.css("span.job-search-card__location").first
                    date_el = card.css("time.job-search-card__listdate").first or card.css("time.job-search-card__listdate--new").first
                    link_el = card.css("a.base-card__full-link").first
                    
                    if not title_el or not company_el:
                        continue
                        
                    raw_title = title_el.text.strip()
                    raw_company = company_el.text.strip()
                    raw_location = location_el.text.strip() if location_el else region
                    posted_date = date_el.attrib.get("datetime", "Unknown") if date_el else "Recent"
                    job_url = link_el.attrib.get("href", "").split("?")[0] # Clean URL
                    
                    # LLM Enrichment
                    enriched = enrich_job_lead(
                        raw_title, 
                        raw_company, 
                        raw_location, 
                        ""
                    )
                    
                    clean_title = enriched.get("clean_title", raw_title)
                    country = enriched.get("country", region)
                    city = enriched.get("city", raw_location)
                    priority = enriched.get("priority", "A")
                    service_needed = enriched.get("service_needed", "3D/Motion Design")
                    
                    leads.append({
                        "company": raw_company,
                        "country": country,
                        "city": city,
                        "category": "LinkedIn Target",
                        "source": "LinkedIn",
                        "demand_signal": f"Hiring: {clean_title} ({posted_date})",
                        "service_needed": service_needed,
                        "notes": f"Job Title: {clean_title} | Location: {raw_location} | Link: {job_url}",
                        "priority": priority
                    })
                    print(f"  [+] Added LinkedIn: {raw_company} - Priority: {priority}")

            except Exception as e:
                print(f"[ERROR] LinkedIn scraping failed for {query} in {region}: {e}")

    print(f"[OK] Found {len(leads)} total LinkedIn leads.")
    save_to_json(leads, 'leads_linkedin.json')
    return leads
