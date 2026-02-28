import json
import time
from scrapling.fetchers import StealthyFetcher
from datetime import datetime

def run_agent():
    print(f"[{datetime.now()}] Agent Upwork: Starting...")
    url = "https://www.upwork.com/freelance-jobs/3d-animation/"
    leads = []
    
    try:
        # Upwork is very aggressive with bot protection, so we use StealthyFetcher
        page = StealthyFetcher.fetch(url, headless=True, wait=15000)
        
        # Dump text for backup/debugging
        text = page.get_all_text()
        with open("debug_upwork_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Simple parsing logic for Upwork job cards
        # Job titles are usually standalone lines followed by "Fixed-price" or "Hourly"
        
        for i, line in enumerate(lines):
            # Identifying common Upwork job markers
            if "Fixed-price" in line or "Hourly" in line or "Est. budget" in line:
                # The title is usually above the budget/type info
                job_title = lines[i-1] if i >= 1 else "Unknown"
                
                # Check for 3D/Motion relevance
                keywords = ["3D", "ANIMAT", "MOTION", "CGI", "RENDER", "VFX"]
                if any(kw in job_title.upper() for kw in keywords) and len(job_title) > 5:
                    leads.append({
                        "company": "Upwork Client (Direct Pitch Target)",
                        "title": job_title,
                        "location": "Global",
                        "posted": "Recent",
                        "source": "Upwork Jobs",
                        "demand_signal": f"Active Upwork Listing: {job_title}"
                    })
        
        # Deduplicate
        unique_titles = set()
        unique_leads = []
        for lead in leads:
            if lead['title'] not in unique_titles:
                unique_titles.add(lead['title'])
                unique_leads.append(lead)
        
        print(f"[{datetime.now()}] Agent Upwork: Found {len(unique_leads)} potential leads.")
        
        with open("leads_upwork.json", "w", encoding="utf-8") as f:
            json.dump(unique_leads, f, indent=4)
            
        print(f"[{datetime.now()}] Agent Upwork: Finished. Saved to leads_upwork.json")
        
    except Exception as e:
        print(f"[{datetime.now()}] Agent Upwork: Failed with error: {e}")

if __name__ == "__main__":
    run_agent()
