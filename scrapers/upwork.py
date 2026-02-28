from scrapling import StealthyFetcher
import time
from urllib.parse import quote_plus
from .utils import save_to_json, save_debug_html
from .llm_enricher import enrich_job_lead

def scrape_upwork(queries=None):
    """
    Scrapes Upwork Jobs using StealthyFetcher and structured selectors.
    Enriches the extracted data using local Gemini LLM.
    queries: A list of search queries from the Strategy Framework.
    """
    if not queries:
        queries = ["3d-animation"] # fallback
        
    print(f"[...] Scraping Upwork Jobs for queries: {queries}")
    fetcher = StealthyFetcher()
    leads = []
    
    for query in queries:
        print(f"\n[➡] Running Upwork Search for: {query}")
        # Build the exact upwork search URL
        safe_query = quote_plus(query)
        base_url = f"https://www.upwork.com/freelance-jobs/{safe_query}/"
        
        for page_num in range(1, 4):
            # Upwork uses page query parameter (e.g. ?page=2)
            url = base_url if page_num == 1 else f"{base_url}?page={page_num}"
            print(f"  -> Scraping page {page_num}...")
            
            try:
                # solve_cloudflare=True is the key feature here
                page = fetcher.fetch(url, timeout=60000, solve_cloudflare=True)
                
                # Save HTML for debugging on first page
                if page_num == 1:
                    save_debug_html(page, "upwork")
                    
                jobs = page.css("div.job-tile, .job-tile")
                if not jobs:
                    print(f"  [!] No more jobs found for {query} on page {page_num}. Stopping pagination.")
                    break
                    
                for job in jobs:
                    title_el = job.css("h3.job-tile-title a").first or job.css("h2.job-tile-title a").first
                    type_el = job.css("strong[data-test='job-type']").first
                    budget_el = job.css("span[data-test='budget']").first
                    duration_el = job.css("span[data-test='duration']").first
                    exp_el = job.css("span[data-test='experience-level']").first
                    desc_el = job.css("p.job-tile-description").first or job.css("div[data-test='job-description-text']").first
                    posted_el = job.css("time").first or job.css("span[data-test='posted-on']").first
                    
                    if not title_el:
                        continue
                        
                    raw_title = title_el.text.strip()
                    job_url = page.urljoin(title_el.attrib.get('href', ''))
                    job_type = type_el.text.strip() if type_el else "Fixed-price"
                    budget = budget_el.text.strip() if budget_el else ""
                    duration = duration_el.text.strip() if duration_el else ""
                    experience = exp_el.text.strip() if exp_el else ""
                    description = desc_el.text.strip() if desc_el else ""
                    posted = posted_el.text.strip() if posted_el else "Recent"
                    
                    # Extract skills/tags
                    skills = [s.text.strip() for s in job.css(".air3-token-container span.air3-token")]
                    
                    # LLM Enrichment
                    enriched = enrich_job_lead(
                        raw_title, 
                        "Unknown Client", 
                        "Remote", 
                        description
                    )
                    
                    clean_title = enriched.get("clean_title", raw_title)
                    priority = enriched.get("priority", "A")
                    service_needed = enriched.get("service_needed", "3D Animation")

                    leads.append({
                        "title": clean_title,
                        "budget": budget,
                        "type": job_type,
                        "duration": duration,
                        "experience": experience,
                        "skills": ", ".join(skills),
                        "description": description[:300] + "..." if len(description) > 300 else description,
                        "posted": posted,
                        "job_url": job_url,
                        "priority": priority,
                        "notes": f"Service: {service_needed} | Direct pitch target."
                    })
                    print(f"  [+] Added Upwork: {clean_title} - Priority: {priority}")

            except Exception as e:
                print(f"[ERROR] Upwork scraping failed on {query} page {page_num}: {e}")
                break

    print(f"[OK] Found {len(leads)} total Upwork projects.")
    save_to_json(leads, 'leads_upwork.json')
    return leads
