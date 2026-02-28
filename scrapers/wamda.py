from scrapling import StealthyFetcher
from .utils import save_to_json, save_debug_html
from .llm_enricher import enrich_startup_lead

def scrape_wamda():
    """
    Scrapes Wamda News using structured CSS selectors, then enriches with Gemini.
    Focuses on funded startups in MENA region.
    """
    print("[...] Scraping Wamda Funding News...")
    fetcher = StealthyFetcher()
    
    url = "https://www.wamda.com/news"
    
    try:
        # Fetch without strict wait_selector
        page = fetcher.fetch(url, timeout=40000)
        
        # Save HTML for debugging
        save_debug_html(page, "wamda")
        
        # Wamda uses c-media class for articles
        articles = page.css("div.c-media, .c-media")
        leads = []
        
        for article in articles:
            # Selectors updated for actual Wamda structure
            title_el = article.css("h2.c-media__title a").first
            meta_el = article.css(".c-media__meta").first
            
            if not title_el:
                continue
                
            headline = title_el.text.strip()
            # Meta usually contains "By Author Name | Date"
            meta_text = meta_el.text.strip() if meta_el else "Recent"
            date = meta_text.split("|")[-1].strip() if "|" in meta_text else meta_text
            article_url = page.urljoin(title_el.attrib.get('href', ''))
            
            # Use Gemini to enrich the startup data
            enriched = enrich_startup_lead(headline, date, article_url)
            
            # Fallback if enrichment returns the raw dict
            company = enriched.get("company", headline)
            country = enriched.get("country", "MENA")
            city = enriched.get("city", "Unknown")
            demand_signal = enriched.get("demand_signal", headline)

            # Only keep if company name is reasonable length
            if len(company) < 2 or len(company) > 40:
                continue

            leads.append({
                "company": company,
                "country": country,
                "city": city,
                "category": "Funded Startup",
                "source": "Wamda",
                "demand_signal": f"Funding News: {demand_signal}",
                "date": date,
                "article_url": article_url,
                "service_needed": "3D/CGI Ads / Branding",
                "notes": f"Full Article: {article_url} | Headline: {headline}",
                "priority": "A+" # Funded startups are high priority
            })

            print(f"  [+] Added: {company} ({city}, {country}) - {demand_signal}")

        print(f"[OK] Found {len(leads)} Wamda funding leads.")
        save_to_json(leads, 'leads_wamda.json')
        return leads

    except Exception as e:
        print(f"[ERROR] Wamda scraping failed: {e}")
        return []
