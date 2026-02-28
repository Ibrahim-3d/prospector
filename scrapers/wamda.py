from scrapling import StealthyFetcher
import re
from .utils import save_to_json, save_debug_html

def scrape_wamda():
    """
    Scrapes Wamda News using structured CSS selectors.
    Focuses on funded startups in MENA region.
    """
    print("[...] Scraping Wamda Funding News...")
    fetcher = StealthyFetcher()
    
    url = "https://www.wamda.com/news"
    
    try:
        # Wamda is static/SSR, so simple fetch works
        page = fetcher.fetch(url, timeout=30000, wait_selector="article.card-item, div.card-item, .card")
        
        # Save HTML for debugging if no results found
        if not (page.css("article.card-item") or page.css("div.card-item") or page.css(".card")):
            save_debug_html(page.text, "wamda")
            print("[!] Wamda search yielded no results (or blocked). Check debug_wamda_html.html")
        
        # Wamda uses article.card-item or div.card-item
        articles = page.css("article.card-item") or page.css("div.card-item") or page.css(".card")
        leads = []
        
        for article in articles:
            # Selectors based on Wamda's clean structure
            category_el = article.css(".category").first
            title_el = article.css(".title a").first or article.css("h3 a").first
            date_el = article.css(".date").first
            
            if not title_el:
                continue
                
            headline = title_el.text.strip()
            category = category_el.text.strip() if category_el else "MENA"
            date = date_el.text.strip() if date_el else "Recent"
            article_url = page.urljoin(title_el.attrib.get('href', ''))
            
            # Simple company extraction from headline:
            # "Saudi's Red Sea Farms raises $10M" -> "Red Sea Farms"
            # "Takeem raises $5M in seed round" -> "Takeem"
            company = headline
            
            # Cleanup common patterns
            company = re.sub(r'\'s\b', '', company) # Remove 's
            
            # Extract name before common funding keywords
            keywords = [" raises", " secures", " closes", " acquires", " bags", " gets"]
            for kw in keywords:
                if kw in company.lower():
                    company = company.split(kw, 1)[0]
                    break
            
            # Remove country prefixes like "Saudi ", "UAE-based ", "Egypt's "
            prefixes = ["Saudi ", "UAE ", "Egypt ", "Jordan ", "MENA ", "Dubai-based ", "Riyadh-based "]
            for p in prefixes:
                if company.startswith(p):
                    company = company[len(p):]
            
            company = company.strip()
            
            # Only keep if company name is reasonable length
            if len(company) < 2 or len(company) > 40:
                continue

            leads.append({
                "company": company,
                "country": category, # Usually country in Wamda
                "city": "Unknown",
                "category": "Funded Startup",
                "source": "Wamda",
                "demand_signal": f"Funding News: {headline} ({date})",
                "service_needed": "3D/CGI Ads / Branding",
                "notes": f"Full Article: {article_url} | Headline: {headline}",
                "priority": "A+" # Funded startups are high priority
            })

        print(f"[OK] Found {len(leads)} Wamda funding leads.")
        save_to_json(leads, 'leads_wamda.json')
        return leads

    except Exception as e:
        print(f"[ERROR] Wamda scraping failed: {e}")
        return []
