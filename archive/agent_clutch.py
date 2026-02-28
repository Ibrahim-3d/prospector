import json
import time
from scrapling.fetchers import StealthyFetcher
from datetime import datetime

def run_agent():
    print(f"[{datetime.now()}] Agent Clutch: Starting...")
    url = "https://clutch.co/agencies/3d-animation"
    leads = []
    
    try:
        # Clutch is heavily protected, using StealthyFetcher with wait
        page = StealthyFetcher.fetch(url, headless=True, wait=10000)
        
        # Save raw text for debugging if needed
        text = page.get_all_text()
        with open("debug_clutch_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Simple heuristic to extract company names and locations
        # Clutch typically lists "Company Name" then stats like "Min. project size", "Avg. hourly rate", "Employees", "Location"
        
        for i, line in enumerate(lines):
            # Look for indicators of a company card
            if "Employees" in line or "Avg. hourly rate" in line:
                # The company name is usually a few lines above
                company_name = lines[i-4] if i >= 4 else "Unknown"
                location = lines[i+1] if i+1 < len(lines) else "Unknown"
                
                # Filter out obvious non-companies
                if len(company_name) > 2 and "Clutch" not in company_name and "Filter" not in company_name:
                    leads.append({
                        "company": company_name,
                        "title": "3D Animation Agency (Potential Partner/Competitor)",
                        "location": location,
                        "posted": "N/A",
                        "source": "Clutch.co",
                        "demand_signal": "Directory Listing - High Intent for 3D Work"
                    })
        
        # Deduplicate
        unique_leads = {lead['company']: lead for lead in leads}.values()
        
        print(f"[{datetime.now()}] Agent Clutch: Found {len(unique_leads)} potential leads.")
        
        with open("leads_clutch.json", "w", encoding="utf-8") as f:
            json.dump(list(unique_leads), f, indent=4)
            
        print(f"[{datetime.now()}] Agent Clutch: Finished. Saved to leads_clutch.json")
        
    except Exception as e:
        print(f"[{datetime.now()}] Agent Clutch: Failed with error: {e}")

if __name__ == "__main__":
    run_agent()
