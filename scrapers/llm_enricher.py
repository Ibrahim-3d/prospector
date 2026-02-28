import subprocess
import json
import logging
import os

def parse_with_gemini(data_dict, expected_keys, context=""):
    """
    Uses the local Gemini CLI to parse, clean, or enrich data.
    data_dict: Dictionary of raw data extracted via CSS.
    expected_keys: List of keys the JSON object should contain.
    context: Additional prompt context (e.g. "This is a Wamda article about a funded startup").
    """
    
    prompt = f"""
    You are an expert data analyst. I have extracted some rough data from a webpage.
    Please clean, fix typos, infer missing details based on your knowledge, and format it exactly.
    
    Context: {context}
    
    Raw Data:
    {json.dumps(data_dict, indent=2)}
    
    Return ONLY a single valid JSON object containing exactly these keys: {expected_keys}.
    Do NOT wrap it in markdown code blocks like ```json ... ```. Just return the raw JSON object.
    If you truly cannot infer a value, use "Unknown". Do not leave fields empty.
    """
    
    try:
        executable = "gemini.cmd" if os.name == "nt" else "gemini"
        
        # Calls the local gemini CLI in non-interactive prompt mode
        result = subprocess.run(
            [executable, "-p", prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=20
        )
        
        output = result.stdout.strip()
        
        # Clean potential markdown wrapping if the LLM disobeys
        if output.startswith("```json"):
            output = output[7:]
        if output.startswith("```"):
            output = output[3:]
        if output.endswith("```"):
            output = output[:-3]
            
        output = output.strip()
        
        parsed_data = json.loads(output)
        return parsed_data
        
    except subprocess.TimeoutExpired:
        logging.error("Gemini CLI timed out.")
        return data_dict # Fallback
    except json.JSONDecodeError:
        logging.error(f"Failed to decode Gemini output as JSON: {output[:100]}...")
        return data_dict # Fallback
    except Exception as e:
        logging.error(f"Gemini execution failed: {e}")
        return data_dict # Fallback

def enrich_startup_lead(raw_headline, raw_date, article_url=""):
    """Specifically built for Wamda / Startup funding news."""
    data = {
        "raw_headline": raw_headline,
        "date": raw_date
    }
    keys = ["company", "country", "city", "demand_signal"]
    context = "This is a startup funding news headline in the MENA region. Extract the literal 'company' name. Based on the headline, figure out the 'country' and 'city' if mentioned, otherwise infer 'MENA' and 'Unknown'. Summarize the 'demand_signal' (e.g., 'Raised $5M Seed')."
    
    enriched = parse_with_gemini(data, keys, context)
    return enriched

def enrich_job_lead(raw_title, raw_company, raw_location, raw_description=""):
    """For Upwork / LinkedIn roles to get better categories and priorities."""
    data = {
        "job_title": raw_title,
        "company": raw_company,
        "location": raw_location,
        "description": raw_description[:500]
    }
    keys = ["clean_title", "company", "country", "city", "service_needed", "priority"]
    context = "This is a job / freelance posting. Determine 'service_needed' (e.g. 3D Animation, Motion Design, Product Render). Determine 'priority' as 'A+' if it explicitly mentions 3D/CGI/Unreal/Motion with high budget or urgent need, else 'A' or 'B'. Extract the exact 'country' and 'city' from the location string."
    
    enriched = parse_with_gemini(data, keys, context)
    return enriched
