from scrapling import StealthyFetcher
import time
from .utils import save_to_json, save_debug_html

def scrape_upwork():
    """
    Scrapes Upwork Jobs using StealthyFetcher and structured selectors.
    Focuses on 3D Animation projects.
    """
    print("[...] Scraping Upwork Jobs (3D Animation)...")
    stealth = StealthyFetcher()
    
    # Query: 3D Animation
    base_url = "https://www.upwork.com/freelance-jobs/3d-animation/"
    leads = []
    
    for page_num in range(1, 4):
        # Upwork uses page query parameter (e.g. ?page=2)
        url = base_url if page_num == 1 else f"{base_url}?page={page_num}"
        print(f"  -> Scraping page {page_num}...")
        
        try:
            # Upwork needs heavy stealth
            page = stealth.fetch(url, timeout=45000, wait_selector="div.job-tile")
            
            # Save HTML for debugging if no results found
            if not page.css("div.job-tile"):
                if page_num == 1:
                    save_debug_html(page.text, "upwork")
                    print("[!] Upwork returned no job tiles (likely blocked). Check debug_upwork_html.html")
                break # Stop if no more jobs found
                
            jobs = page.css("div.job-tile")
            
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
                    
                title = title_el.text.strip()
                job_url = page.urljoin(title_el.attrib.get('href', ''))
                job_type = type_el.text.strip() if type_el else "Fixed-price"
                budget = budget_el.text.strip() if budget_el else ""
                duration = duration_el.text.strip() if duration_el else ""
                experience = exp_el.text.strip() if exp_el else ""
                description = desc_el.text.strip() if desc_el else ""
                posted = posted_el.text.strip() if posted_el else "Recent"
                
                # Extract skills/tags
                skills = [s.text.strip() for s in job.css(".air3-token-container span.air3-token")]
                
                leads.append({
                    "title": title,
                    "budget": budget,
                    "type": job_type,
                    "duration": duration,
                    "experience": experience,
                    "skills": ", ".join(skills),
                    "description": description[:300] + "..." if len(description) > 300 else description,
                    "posted": posted,
                    "job_url": job_url,
                    "priority": "A+" if any(x in title.lower() for x in ["long-term", "expert", "high budget"]) else "A",
                    "notes": "Direct pitch target. Check description for client cues."
                })

        except Exception as e:
            print(f"[ERROR] Upwork scraping failed on page {page_num}: {e}")
            break

    print(f"[OK] Found {len(leads)} Upwork projects.")
    save_to_json(leads, 'leads_upwork.json')
    return leads
