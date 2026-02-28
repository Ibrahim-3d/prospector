from scrapers.artstation import scrape_artstation
from scrapers.wamda import scrape_wamda
from scrapers.linkedin import scrape_linkedin
from scrapers.upwork import scrape_upwork
from scrapers.utils import save_to_excel, save_upwork_to_excel
import os
from datetime import datetime

def run_suite():
    """
    Main orchestrator for the Master Scraping Suite.
    Runs all scrapers and updates the Excel tracker.
    """
    start_time = datetime.now()
    print("="*60)
    print(f"🚀 MASTER SCRAPING SUITE STARTED at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # 1. Scraping Phase
    # We collect results in a list to process later
    all_company_leads = []
    upwork_leads = []

    # ArtStation (Priority A+)
    try:
        artstation_results = scrape_artstation()
        if artstation_results:
            all_company_leads.extend(artstation_results)
    except Exception as e:
        print(f"[ERROR] ArtStation Scraper Failed: {e}")

    # LinkedIn (Priority A+)
    try:
        linkedin_results = scrape_linkedin()
        if linkedin_results:
            all_company_leads.extend(linkedin_results)
    except Exception as e:
        print(f"[ERROR] LinkedIn Scraper Failed: {e}")

    # Wamda (MENA Funding)
    try:
        wamda_results = scrape_wamda()
        if wamda_results:
            all_company_leads.extend(wamda_results)
    except Exception as e:
        print(f"[ERROR] Wamda Scraper Failed: {e}")

    # Upwork (Project Leads)
    try:
        upwork_results = scrape_upwork()
        if upwork_results:
            upwork_leads = upwork_results
    except Exception as e:
        print(f"[ERROR] Upwork Scraper Failed: {e}")

    # 2. Excel Update Phase
    print("\n" + "-"*30)
    print("📊 UPDATING EXCEL TRACKER...")
    
    # Save standard company leads
    added_companies = save_to_excel(all_company_leads)
    
    # Save specialized Upwork leads
    added_upwork = save_upwork_to_excel(upwork_leads)
    
    # 3. Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print(f"🏁 SCRAPING SUITE COMPLETED")
    print(f"⏱️ Duration: {duration}")
    print(f"✨ New Companies Added: {added_companies}")
    print(f"🔧 New Upwork Projects Added: {added_upwork}")
    print(f"📁 Output: ibrahim_guerrilla_targeting_v2.xlsx")
    print("="*60)

if __name__ == "__main__":
    run_suite()
