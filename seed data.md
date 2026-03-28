# Freelance Command Center — Content & Data Reference

## Purpose

This document is the **content layer** for the Freelance Command Center app. It maps all strategic content from the Guerrilla Targeting System (Excel workbook) into the app’s database models and UI components. Every seed record, every template variable, every query string, every pipeline stage — defined here so the app launches with a fully loaded operational system, not an empty shell.

**Source file**: `ibrahim_guerrilla_targeting_v2.xlsx` (6 sheets)
**Target**: PostgreSQL seed data + frontend content + Celery job configs

-----

## 1. PIPELINE STAGES (seed: `pipeline_stages` table)

These are the default deal stages for the Kanban board. Order matters — it defines left-to-right flow.

```json
[
  {"position": 1,  "name": "New Lead",       "color": "#636E72", "description": "Just discovered. No research done yet."},
  {"position": 2,  "name": "Researched",     "color": "#6C5CE7", "description": "Company + contact researched. Ready for outreach."},
  {"position": 3,  "name": "Contacted",      "color": "#0984E3", "description": "First outreach sent (email, DM, or proposal)."},
  {"position": 4,  "name": "Responded",      "color": "#00B894", "description": "They replied. Conversation started."},
  {"position": 5,  "name": "Meeting",        "color": "#FDCB6E", "description": "Call or meeting scheduled/completed."},
  {"position": 6,  "name": "Proposal Sent",  "color": "#E17055", "description": "Formal proposal or quote delivered."},
  {"position": 7,  "name": "Negotiating",    "color": "#D63031", "description": "Discussing scope, rate, or timeline."},
  {"position": 8,  "name": "Won",            "color": "#00B894", "description": "Deal closed. Work started or contract signed."},
  {"position": 9,  "name": "Lost",           "color": "#B2BEC3", "description": "Deal didn't close. Log reason."},
  {"position": 10, "name": "Nurture",        "color": "#A29BFE", "description": "Not now, but keep warm for future."}
]
```

**UI behavior**:

- Deals in “Won” auto-prompt: “Create invoice?” and “Log revenue”
- Deals in “Lost” require a `lost_reason` (dropdown: “Too expensive”, “Went with competitor”, “Project cancelled”, “No budget”, “No response”, “Bad timing”, “Other”)
- Deals in “Nurture” auto-create a recurring task: “Check in with [Company]” every 30 days
- Deals idle for 7+ days in any stage get a yellow “stale” badge
- Deals idle for 14+ days get a red “at risk” badge

-----

## 2. COMPANY CATEGORIES & SUBCATEGORIES (seed: `companies` table enums)

These map to the Excel Sheet 1 “Target Companies” category groups and Sheet 3 “Regional Discovery” segments.

### Categories (primary classification)

```json
[
  {
    "value": "studio",
    "label": "3D / CGI / Animation Studio",
    "icon": "🎨",
    "description": "Companies whose core business is producing 3D, CGI, motion, or animation content",
    "why_target": "They outsource overflow work to freelancers during peak periods. Smaller studios (2-50 people) are most likely to use freelancers."
  },
  {
    "value": "dooh_ooh",
    "label": "DOOH / OOH / Anamorphic",
    "icon": "🔥",
    "description": "Companies that produce or sell digital out-of-home and anamorphic 3D billboard content",
    "why_target": "Niche specialty with few qualified freelancers globally. High project values ($5K-$50K+). White-label partnerships common."
  },
  {
    "value": "agency",
    "label": "Creative / Ad Agency",
    "icon": "🏢",
    "description": "Full-service advertising, creative, or digital agencies that commission 3D/motion/video work for clients",
    "why_target": "Agencies take on more client work than they can handle. They maintain freelancer pools for overflow. Getting into an agency's approved roster = recurring work."
  },
  {
    "value": "production_house",
    "label": "Production / Post-Production House",
    "icon": "🎬",
    "description": "Film, TV, and commercial production/post-production companies (VFX, compositing, 3D)",
    "why_target": "Project-based hiring. They scale up with freelancers for specific productions. Once trusted, you get called back."
  },
  {
    "value": "brand",
    "label": "Brand / In-House Team",
    "icon": "🏷️",
    "description": "Companies with in-house marketing/creative teams that commission external 3D/motion/video work",
    "why_target": "Direct client = no middleman. Higher margins. But longer sales cycle. Best approached via marketing directors or brand managers."
  },
  {
    "value": "startup",
    "label": "Startup / Tech Company",
    "icon": "🤖",
    "description": "Funded startups and tech companies needing creative content (product demos, marketing, explainers)",
    "why_target": "Post-funding startups have budget but no creative team. They need fast, affordable creative help. High volume of small projects."
  },
  {
    "value": "real_estate",
    "label": "Real Estate Developer / Architecture",
    "icon": "🏙️",
    "description": "Property developers, architecture firms, and interior design studios needing 3D visualization",
    "why_target": "Every new building/project needs renders before construction. Recurring need. Large project volumes in UAE, Kuwait, Saudi."
  },
  {
    "value": "ecommerce",
    "label": "E-Commerce / D2C Brand",
    "icon": "🛒",
    "description": "Online retail brands needing CGI product renders, animations, and marketing content",
    "why_target": "Product renders are high-volume recurring work. One brand = dozens of SKUs = dozens of renders. Growing fast in MENA."
  },
  {
    "value": "event_exhibition",
    "label": "Event / Exhibition Company",
    "icon": "🎪",
    "description": "Event production, exhibition design, and experiential marketing companies",
    "why_target": "Events need 3D content for LED walls, immersive installations, and booth designs. Seasonal peaks = freelancer demand."
  },
  {
    "value": "game_studio",
    "label": "Game Art / VFX Studio",
    "icon": "🎮",
    "description": "Game development studios and game art outsourcing companies",
    "why_target": "Art outsourcing model is standard in gaming. Studios scale up/down with freelancers per project. AAA and indie."
  },
  {
    "value": "platform",
    "label": "Freelance Platform / Network",
    "icon": "📱",
    "description": "Platforms and networks where you can find freelance work (Upwork, Toptal, A.Team, etc.)",
    "why_target": "Not a client target — a channel to find clients. Profile optimization and active presence = inbound leads."
  }
]
```

### Subcategories (secondary tags, multi-select)

```json
[
  "3d_animation", "cgi_rendering", "motion_design", "motion_graphics",
  "anamorphic_billboard", "dooh_content", "led_screen_content",
  "product_visualization", "architectural_visualization", "interior_design_viz",
  "vfx_compositing", "character_animation", "technical_animation",
  "ai_video", "ai_creative", "generative_ai",
  "web_interactive", "threejs_webgl", "ar_vr",
  "brand_identity", "packaging_design", "social_media_content",
  "explainer_video", "commercial_production", "music_video",
  "game_art", "concept_art", "environment_design",
  "medical_visualization", "scientific_visualization",
  "real_estate_marketing", "virtual_staging", "3d_walkthrough"
]
```

-----

## 3. DEMAND SIGNALS (seed: signal type enums + detection rules)

These are the strategic signals from Excel Sheet 1 “Strategy Framework” that indicate a company needs freelance help RIGHT NOW.

```json
[
  {
    "signal_type": "unfilled_job_post",
    "label": "Unfilled Job Post",
    "icon": "📋",
    "priority_boost": 25,
    "description": "Company posted a full-time 3D/motion/CGI role 30+ days ago and it's still open",
    "why_high_value": "If they can't hire full-time in 30+ days, they're desperate. A freelancer solves their immediate pain while they keep searching.",
    "expected_hit_rate": "25-35%",
    "detection_method": "LinkedIn Jobs API scrape: filter by date posted > 30 days, role matches our keywords",
    "outreach_angle": "While you're searching for the right full-time hire, I can handle projects immediately — no onboarding needed.",
    "auto_task": "Research company → Find hiring manager on LinkedIn → Send 'Job Post Reverse' template within 24 hours"
  },
  {
    "signal_type": "recent_funding",
    "label": "Recently Funded",
    "icon": "💰",
    "priority_boost": 20,
    "description": "Startup raised Seed/Series A/B in the last 90 days",
    "why_high_value": "Post-funding: they have money, pressure to execute, but no team yet. Need freelance creative ASAP.",
    "expected_hit_rate": "20-30%",
    "detection_method": "Crunchbase/Tracxn/Wamda/TechCrunch RSS monitoring for funding announcements",
    "outreach_angle": "Congrats on the raise! As you ramp up marketing, I can help with [3D/video/creative] — startup speed at startup rates.",
    "auto_task": "Add to pipeline as 'New Lead' → Research their product → Send 'Funded Startup' email template within 48 hours"
  },
  {
    "signal_type": "key_person_departure",
    "label": "Key Person Left",
    "icon": "🚪",
    "priority_boost": 30,
    "description": "Company's 3D artist, motion designer, or creative lead just left (visible on LinkedIn job changes)",
    "why_high_value": "They have an immediate gap. Freelancer is the fastest way to maintain production while they recruit.",
    "expected_hit_rate": "30-40%",
    "detection_method": "LinkedIn alerts on tracked companies — watch for job title changes of creative staff",
    "outreach_angle": "I noticed [Name] recently moved on from [Company]. If you need coverage while you hire, I'm available immediately.",
    "auto_task": "Flag as HIGH priority → Send outreach within 24 hours → Follow up in 3 days"
  },
  {
    "signal_type": "bad_diy_content",
    "label": "Bad DIY Content",
    "icon": "😬",
    "priority_boost": 20,
    "description": "Company posted amateur 3D/CGI/motion content on social media — they tried but it looks unprofessional",
    "why_high_value": "They already WANT 3D content (proven intent) but lack the skill. Easiest sell — show them what a pro can do.",
    "expected_hit_rate": "20-30%",
    "detection_method": "Manual social media monitoring of target companies. Instagram/LinkedIn/YouTube review.",
    "outreach_angle": "Loved that you're exploring 3D content — here's how we could take it to the next level. [Attach quick mockup or relevant portfolio piece]",
    "auto_task": "Screenshot their content → Create before/after comparison → DM with portfolio link"
  },
  {
    "signal_type": "expansion",
    "label": "New Office / Expansion",
    "icon": "🌍",
    "priority_boost": 15,
    "description": "Company opened a new office, entered a new market, or announced expansion",
    "why_high_value": "Expansion = new marketing campaigns, new audiences, new content needs. Budget is flowing.",
    "expected_hit_rate": "15-25%",
    "detection_method": "Google Alerts + LinkedIn company page updates + press releases",
    "outreach_angle": "Congrats on the expansion to [market]! I'd love to help with creative content as you build your presence there.",
    "auto_task": "Research their expansion → Identify creative needs → Send tailored outreach"
  },
  {
    "signal_type": "award_win",
    "label": "Award Winner",
    "icon": "🏆",
    "priority_boost": 10,
    "description": "Agency or studio just won an industry award (Cannes Lions, D&AD, The One Show, Loeries, etc.)",
    "why_high_value": "Awards attract new clients to the agency → more work → need more freelancers for overflow.",
    "expected_hit_rate": "15-20%",
    "detection_method": "Monitor award show results. Google Alerts for agency award wins.",
    "outreach_angle": "Congrats on the [Award] win! As you take on more work, I'd love to be your go-to 3D resource for overflow.",
    "auto_task": "Add to pipeline → Send congratulatory DM → Pitch services"
  },
  {
    "signal_type": "competitor_campaign",
    "label": "Competitor Just Did It",
    "icon": "👀",
    "priority_boost": 15,
    "description": "A company's competitor just launched a 3D billboard, CGI campaign, or viral 3D content",
    "why_high_value": "FOMO is real in marketing. When a competitor does something flashy, the CMO asks 'Why don't WE have that?'",
    "expected_hit_rate": "10-20%",
    "detection_method": "Social media monitoring for 3D billboard/campaign launches. Track brand responses.",
    "outreach_angle": "Saw [Competitor]'s 3D campaign getting massive engagement. I can help [Company] do something even better.",
    "auto_task": "Document competitor campaign → Identify 3-5 companies in same industry → Send tailored outreach"
  },
  {
    "signal_type": "rfp_tender",
    "label": "RFP / Tender",
    "icon": "📑",
    "priority_boost": 20,
    "description": "Government or brand posted a formal RFP/tender for creative, 3D, DOOH, or media production work",
    "why_high_value": "Pre-qualified demand with approved budget. They MUST spend this money on creative.",
    "expected_hit_rate": "15-25%",
    "detection_method": "UAE govt portals (Tejari), Kuwait CAPT, EU tender databases",
    "outreach_angle": "Respond to RFP directly, or partner with an agency responding to the tender.",
    "auto_task": "Evaluate RFP requirements → Decide: respond directly or partner with agency → Submit or pitch partnership"
  },
  {
    "signal_type": "product_launch",
    "label": "Product Launch",
    "icon": "🚀",
    "priority_boost": 15,
    "description": "Company is launching a new product and needs marketing content (renders, videos, demos)",
    "why_high_value": "Product launches have deadlines and budgets. They need content fast.",
    "expected_hit_rate": "15-25%",
    "detection_method": "Product Hunt, press releases, LinkedIn announcements",
    "outreach_angle": "Congrats on the upcoming launch! I can help with product renders/demo videos to make it stand out.",
    "auto_task": "Research product → Identify visual needs → Send tailored pitch"
  },
  {
    "signal_type": "seasonal_peak",
    "label": "Seasonal Peak",
    "icon": "📅",
    "priority_boost": 10,
    "description": "Industry seasonal peak approaching (Q4 retail, Ramadan campaigns, summer launches, festival season)",
    "why_high_value": "Agencies and brands scramble for creative capacity during peak seasons.",
    "expected_hit_rate": "15-20%",
    "detection_method": "Calendar-based. Set reminders 6-8 weeks before peak seasons.",
    "outreach_angle": "I know [season] is coming up — I'm booking projects now. Want to lock in availability?",
    "auto_task": "Auto-trigger outreach to all 'Nurture' stage deals 6-8 weeks before known peaks"
  }
]
```

### Seasonal Calendar (auto-trigger outreach)

```json
[
  {"month": 1,  "event": "CES / New Year campaigns",       "regions": ["US", "Global"],      "outreach_weeks_before": 8},
  {"month": 2,  "event": "Super Bowl ad season",            "regions": ["US"],                "outreach_weeks_before": 10},
  {"month": 3,  "event": "Ramadan campaigns",               "regions": ["UAE", "Kuwait", "MENA"], "outreach_weeks_before": 8},
  {"month": 4,  "event": "Spring product launches",         "regions": ["US", "EU"],          "outreach_weeks_before": 6},
  {"month": 5,  "event": "Cannes Lions prep",               "regions": ["Global"],            "outreach_weeks_before": 6},
  {"month": 6,  "event": "Summer campaigns",                "regions": ["Global"],            "outreach_weeks_before": 8},
  {"month": 7,  "event": "Back-to-school campaigns",        "regions": ["US", "EU"],          "outreach_weeks_before": 8},
  {"month": 8,  "event": "GITEX prep (Dubai)",              "regions": ["UAE", "MENA"],       "outreach_weeks_before": 8},
  {"month": 9,  "event": "Q4 planning / Holiday creative",  "regions": ["Global"],            "outreach_weeks_before": 10},
  {"month": 10, "event": "GITEX Dubai",                     "regions": ["UAE", "MENA"],       "outreach_weeks_before": 4},
  {"month": 11, "event": "Black Friday / Cyber Monday",     "regions": ["Global"],            "outreach_weeks_before": 8},
  {"month": 12, "event": "New Year / Holiday campaigns",    "regions": ["Global"],            "outreach_weeks_before": 6}
]
```

-----

## 4. OUTREACH TEMPLATES (seed: `outreach_templates` table)

Every template from Excel Sheet 6 “Outreach Templates” + additional templates, with variable placeholders mapped to database fields.

### Variable Reference

These placeholders are auto-replaced when rendering a message. The system pulls data from the `companies`, `contacts`, and `portfolio_items` tables.

```json
{
  "{{contact_first_name}}":   "contacts.first_name",
  "{{contact_full_name}}":    "contacts.first_name + contacts.last_name",
  "{{contact_title}}":        "contacts.title",
  "{{company_name}}":         "companies.name",
  "{{company_website}}":      "companies.website",
  "{{company_city}}":         "companies.city",
  "{{company_country}}":      "companies.country",
  "{{company_industry}}":     "companies.industry",
  "{{specific_project}}":     "AI-generated OR manual — a specific project/campaign the company did",
  "{{competitor_name}}":      "Manual — a competitor of the target company",
  "{{service_match}}":        "AI-generated — which of your services best matches their needs",
  "{{relevant_portfolio}}":   "portfolio_items.media_urls[0] — link to your most relevant work",
  "{{funding_source}}":       "Source where you saw their funding news",
  "{{project_name}}":         "Manual — name of their specific project/development",
  "{{season}}":               "Auto — current quarter or upcoming season",
  "{{portfolio_url}}":        "Static — ibrahim3d.com",
  "{{your_name}}":            "Static — Ibrahim"
}
```

### Template Records

```json
[
  {
    "name": "LinkedIn DM — Cold (Short)",
    "channel": "linkedin_dm",
    "category": "cold_initial",
    "subject_line": null,
    "body": "Hey {{contact_first_name}},\n\nJust saw {{company_name}}'s {{specific_project}} — really sharp work.\n\nI'm a 3D artist who does overflow production for studios like yours. Specialize in anamorphic billboards, CGI motion, and AI-accelerated workflows.\n\nWould love to be on your radar for when projects stack up.\n\nibrahim3d.com\n\nCheers,\n{{your_name}}",
    "variables": ["contact_first_name", "company_name", "specific_project", "your_name"],
    "tags": ["cold", "short", "linkedin", "all_categories"],
    "notes": "Keep under 75 words. Reference ONE specific thing about their work. Best for Creative Directors and Producers.",
    "best_for_categories": ["studio", "agency", "production_house", "dooh_ooh"],
    "best_for_roles": ["creative_director", "art_director", "producer", "founder"],
    "character_limit": 300
  },
  {
    "name": "LinkedIn DM — Warm (Engaged with your post)",
    "channel": "linkedin_dm",
    "category": "warm_initial",
    "subject_line": null,
    "body": "Hey {{contact_first_name}}, thanks for engaging with my post!\n\nI noticed you're at {{company_name}} — looks like you do some great {{specific_project}}. If you ever need extra 3D/motion capacity, I'd love to be your go-to overflow resource.\n\nPortfolio: ibrahim3d.com\n\nHappy to chat anytime.",
    "variables": ["contact_first_name", "company_name", "specific_project"],
    "tags": ["warm", "linkedin", "post_engagement"],
    "notes": "Only use after someone liked, commented, or shared your content. Reference YOUR post they engaged with.",
    "best_for_categories": ["studio", "agency", "dooh_ooh"],
    "best_for_roles": ["any"],
    "character_limit": 300
  },
  {
    "name": "LinkedIn DM — Job Post Reverse",
    "channel": "linkedin_dm",
    "category": "demand_signal_response",
    "subject_line": null,
    "body": "Hey {{contact_first_name}},\n\nI noticed {{company_name}} has been looking for a {{contact_title}}. While you're searching for the right full-time hire, I'm available to handle projects immediately as a freelancer.\n\nI've done similar work for brands like ALDO and Cadbury. No onboarding needed — just send a brief and I deliver.\n\nibrahim3d.com\n\nHappy to chat if helpful.",
    "variables": ["contact_first_name", "company_name", "contact_title"],
    "tags": ["demand_signal", "job_post", "linkedin", "high_conversion"],
    "notes": "Use when you find a company with an unfilled 3D/motion job post (30+ days old). Reference their exact job title. Highest conversion template (25-35%).",
    "best_for_categories": ["studio", "agency", "brand", "startup"],
    "best_for_roles": ["hiring_manager", "hr", "creative_director", "founder"],
    "character_limit": 300
  },
  {
    "name": "Cold Email — Studio / Agency",
    "channel": "email",
    "category": "cold_initial",
    "subject_line": "Freelance 3D resource — when projects pile up",
    "body": "Hi {{contact_first_name}},\n\nI came across {{company_name}}'s work on {{specific_project}} — impressive quality.\n\nI'm Ibrahim, a freelance 3D artist and motion designer. I work with studios as an overflow resource when projects stack up or deadlines get tight.\n\nWhat I bring:\n→ Anamorphic 3D billboard production (ALDO, Cadbury, Steve Madden)\n→ CGI motion design & product visualization\n→ AI-accelerated workflows for faster turnarounds\n→ Cinema 4D, Blender, Houdini, After Effects\n\nI work remotely at competitive rates with fast turnarounds.\n\nPortfolio: ibrahim3d.com\n\nWould it make sense to be in your freelancer pool for busy periods?\n\nBest,\nIbrahim",
    "variables": ["contact_first_name", "company_name", "specific_project"],
    "tags": ["cold", "email", "studio", "agency"],
    "notes": "Reference a specific project they did. Emphasize 'overflow resource' framing — you're not replacing anyone, you're extra capacity.",
    "best_for_categories": ["studio", "agency", "production_house"],
    "best_for_roles": ["creative_director", "producer", "founder", "head_of_production"],
    "character_limit": null
  },
  {
    "name": "Cold Email — DOOH / Anamorphic Partner",
    "channel": "email",
    "category": "cold_initial",
    "subject_line": "Anamorphic 3D production — white-label partner",
    "body": "Hi {{contact_first_name}},\n\nI run Viral X, a Dubai-based 3D anamorphic production studio. We produce 3D billboard content for brands including ALDO, Steve Madden, and Dubai Safari Park.\n\nI'd love to explore a production partnership where I handle overflow 3D work for {{company_name}} — either white-label or co-branded.\n\nOur setup:\n→ Full anamorphic pipeline (concept → final delivery)\n→ AI-accelerated rendering for faster turnarounds\n→ Experience with major LED screen formats\n→ Competitive rates, remote delivery\n\nPortfolio: ibrahim3d.com\n\nWould a 15-min call make sense to explore fit?\n\nBest,\nIbrahim",
    "variables": ["contact_first_name", "company_name"],
    "tags": ["cold", "email", "dooh", "anamorphic", "partnership"],
    "notes": "Position as studio-to-studio partnership, not individual freelancer. Lead with Viral X brand. Emphasize white-label model.",
    "best_for_categories": ["dooh_ooh"],
    "best_for_roles": ["founder", "creative_director", "producer", "business_development"],
    "character_limit": null
  },
  {
    "name": "Cold Email — Funded Startup",
    "channel": "email",
    "category": "demand_signal_response",
    "subject_line": "Creative help for {{company_name}} — 3D + AI video",
    "body": "Hi {{contact_first_name}},\n\nCongrats on the recent raise! Saw {{company_name}}'s funding news on {{funding_source}}.\n\nAs you ramp up marketing, I wanted to offer my services as a freelance 3D artist and creative technologist. I specialize in:\n\n→ Product visualization and CGI renders\n→ 3D motion content for social and ads\n→ AI-powered video production (faster + cheaper)\n→ Interactive web experiences\n\nI've worked with enterprise brands (ALDO, Cadbury) and can deliver startup-speed at startup-friendly rates.\n\nPortfolio: ibrahim3d.com\n\nHappy to chat about what creative support could look like.\n\nBest,\nIbrahim",
    "variables": ["contact_first_name", "company_name", "funding_source"],
    "tags": ["demand_signal", "funding", "email", "startup"],
    "notes": "Reference the exact funding source. Emphasize speed and cost-effectiveness. Match language to startup culture (less formal).",
    "best_for_categories": ["startup"],
    "best_for_roles": ["founder", "cmo", "head_of_marketing", "cto"],
    "character_limit": null
  },
  {
    "name": "Cold Email — Real Estate Developer",
    "channel": "email",
    "category": "cold_initial",
    "subject_line": "3D visualization for {{project_name}}",
    "body": "Hi {{contact_first_name}},\n\nI came across {{company_name}}'s {{project_name}}. Impressive vision.\n\nI'm a 3D visualization specialist based in Dubai, offering:\n→ Photorealistic architectural renders\n→ 3D walkthrough animations\n→ Interior design visualization\n→ Aerial fly-through videos\n\nI work with developers and architects to create marketing-ready visuals that help sell off-plan properties faster.\n\nPortfolio: ibrahim3d.com\n\nWould you be open to seeing some relevant examples?\n\nBest,\nIbrahim",
    "variables": ["contact_first_name", "company_name", "project_name"],
    "tags": ["cold", "email", "real_estate", "architecture"],
    "notes": "Name their specific development project. Emphasize 'sell faster' — that's what developers care about.",
    "best_for_categories": ["real_estate"],
    "best_for_roles": ["marketing_director", "sales_director", "founder", "project_director"],
    "character_limit": null
  },
  {
    "name": "Cold Email — E-Commerce Brand",
    "channel": "email",
    "category": "cold_initial",
    "subject_line": "CGI product renders for {{company_name}}",
    "body": "Hi {{contact_first_name}},\n\nI noticed {{company_name}} is growing fast — congrats on the momentum.\n\nI specialize in CGI product renders that look better than photography — at a fraction of the cost. Benefits:\n→ No physical sample needed\n→ Unlimited angles, colors, and environments\n→ Consistent quality across your entire catalog\n→ 3D animation for social ads and product demos\n\nSome examples: ibrahim3d.com\n\nWould it be helpful to see a test render of one of your products?\n\nBest,\nIbrahim",
    "variables": ["contact_first_name", "company_name"],
    "tags": ["cold", "email", "ecommerce", "product_viz"],
    "notes": "Offer a free test render as a hook. This is a volume play — one brand = dozens of SKUs.",
    "best_for_categories": ["ecommerce"],
    "best_for_roles": ["founder", "marketing_director", "creative_director", "ecommerce_manager"],
    "character_limit": null
  },
  {
    "name": "Upwork Proposal — Universal",
    "channel": "upwork_proposal",
    "category": "platform_application",
    "subject_line": null,
    "body": "Hi {{contact_first_name}},\n\n{{specific_project}}\n\nThis aligns directly with my experience. I've produced {{service_match}} content for brands including ALDO, Cadbury, and Steve Madden.\n\nMy approach:\n1. Quick concept alignment (within 24hrs of start)\n2. First draft delivery in [X] days\n3. [X] revision rounds included\n4. AI-assisted workflow = faster delivery at same quality\n\nTools: Cinema 4D / Blender / Houdini / After Effects\n\nPortfolio: ibrahim3d.com\n\nHappy to discuss scope. Looking forward to your thoughts.\n\nIbrahim",
    "variables": ["contact_first_name", "specific_project", "service_match"],
    "tags": ["upwork", "proposal", "universal"],
    "notes": "{{specific_project}} here should be 1-2 sentences referencing their EXACT brief. Quote a detail from their job post to prove you read it. Never send generic proposals.",
    "best_for_categories": ["any"],
    "best_for_roles": ["any"],
    "character_limit": 5000
  },
  {
    "name": "Follow-Up #1 — New Value",
    "channel": "email",
    "category": "follow_up",
    "subject_line": "Quick follow-up — {{service_match}}",
    "body": "Hi {{contact_first_name}},\n\nJust bumping my note from last week. No pressure — I know things get busy.\n\nHere's a recent project that might be relevant to what {{company_name}} does: {{relevant_portfolio}}\n\nHappy to chat whenever timing works.\n\nBest,\nIbrahim",
    "variables": ["contact_first_name", "company_name", "service_match", "relevant_portfolio"],
    "tags": ["follow_up", "email", "linkedin"],
    "notes": "Must include NEW value — a relevant portfolio link they haven't seen. Never just say 'following up'.",
    "sequence_position": 2,
    "delay_days_after_previous": 5,
    "condition": "no_response",
    "best_for_categories": ["any"],
    "best_for_roles": ["any"],
    "character_limit": null
  },
  {
    "name": "Follow-Up #2 — Industry Insight",
    "channel": "email",
    "category": "follow_up",
    "subject_line": "Thought you might find this useful",
    "body": "Hi {{contact_first_name}},\n\nI noticed {{competitor_name}} just launched a {{specific_project}}. The engagement numbers have been impressive.\n\nIf {{company_name}} ever wants to explore this space, I'd love to help. My door is always open.\n\nibrahim3d.com\n\nBest,\nIbrahim",
    "variables": ["contact_first_name", "company_name", "competitor_name", "specific_project"],
    "tags": ["follow_up", "email", "value_add"],
    "notes": "Lead with a genuine industry insight or competitor observation. No ask — just value. Builds authority.",
    "sequence_position": 3,
    "delay_days_after_previous": 7,
    "condition": "no_response",
    "best_for_categories": ["any"],
    "best_for_roles": ["any"],
    "character_limit": null
  },
  {
    "name": "Follow-Up #3 — Final (Soft Close)",
    "channel": "email",
    "category": "follow_up",
    "subject_line": "Keeping the door open",
    "body": "Hi {{contact_first_name}},\n\nLast note from me! Just leaving the door open — if {{company_name}} ever needs freelance 3D/motion support, I'm an email away.\n\nWishing you and the team a great {{season}}.\n\nBest,\nIbrahim",
    "variables": ["contact_first_name", "company_name", "season"],
    "tags": ["follow_up", "final", "email"],
    "notes": "Warm, no pressure. Leave relationship positive. Move deal to 'Nurture' stage after this.",
    "sequence_position": 4,
    "delay_days_after_previous": 14,
    "condition": "no_response",
    "auto_action": "move_to_nurture_stage",
    "best_for_categories": ["any"],
    "best_for_roles": ["any"],
    "character_limit": null
  }
]
```

-----

## 5. OUTREACH SEQUENCES (seed: `outreach_sequences` + `sequence_steps` tables)

Pre-built multi-step sequences that auto-enroll contacts.

```json
[
  {
    "name": "Cold Studio/Agency Sequence",
    "description": "Standard 4-step outreach for 3D studios and creative agencies",
    "steps": [
      {"step": 1, "template": "Cold Email — Studio / Agency",    "channel": "email",      "delay_days": 0,  "condition": "always"},
      {"step": 2, "template": "LinkedIn DM — Cold (Short)",      "channel": "linkedin_dm","delay_days": 3,  "condition": "no_response"},
      {"step": 3, "template": "Follow-Up #1 — New Value",        "channel": "email",      "delay_days": 5,  "condition": "no_response"},
      {"step": 4, "template": "Follow-Up #3 — Final",            "channel": "email",      "delay_days": 14, "condition": "no_response"}
    ]
  },
  {
    "name": "DOOH Partnership Sequence",
    "description": "3-step outreach for anamorphic/DOOH production companies",
    "steps": [
      {"step": 1, "template": "Cold Email — DOOH / Anamorphic Partner", "channel": "email",       "delay_days": 0,  "condition": "always"},
      {"step": 2, "template": "Follow-Up #1 — New Value",              "channel": "email",       "delay_days": 5,  "condition": "no_response"},
      {"step": 3, "template": "Follow-Up #2 — Industry Insight",       "channel": "email",       "delay_days": 7,  "condition": "no_response"}
    ]
  },
  {
    "name": "Funded Startup Sequence",
    "description": "Fast 3-step sequence for recently funded startups",
    "steps": [
      {"step": 1, "template": "Cold Email — Funded Startup",    "channel": "email",      "delay_days": 0,  "condition": "always"},
      {"step": 2, "template": "LinkedIn DM — Cold (Short)",     "channel": "linkedin_dm","delay_days": 2,  "condition": "no_response"},
      {"step": 3, "template": "Follow-Up #1 — New Value",       "channel": "email",      "delay_days": 5,  "condition": "no_response"}
    ]
  },
  {
    "name": "Job Post Reverse Sequence",
    "description": "High-conversion sequence targeting companies with unfilled 3D roles",
    "steps": [
      {"step": 1, "template": "LinkedIn DM — Job Post Reverse", "channel": "linkedin_dm","delay_days": 0,  "condition": "always"},
      {"step": 2, "template": "Cold Email — Studio / Agency",   "channel": "email",      "delay_days": 3,  "condition": "no_response"},
      {"step": 3, "template": "Follow-Up #1 — New Value",       "channel": "email",      "delay_days": 5,  "condition": "no_response"}
    ]
  },
  {
    "name": "Nurture Re-engagement",
    "description": "Quarterly check-in for deals in Nurture stage",
    "steps": [
      {"step": 1, "template": "Follow-Up #2 — Industry Insight","channel": "email",      "delay_days": 0,  "condition": "always"}
    ],
    "auto_trigger": "deal_in_nurture_90_days"
  }
]
```

-----

## 6. SAVED QUERIES (seed: `saved_queries` table)

All 113 queries from Excel Sheet 2 “Query Library” loaded as saved queries. Below is the structured format for each. Full query list is in the Excel file — here’s the schema and representative samples per platform.

### Schema per query

```json
{
  "name": "string — human-readable name",
  "platform": "string — linkedin_people | linkedin_companies | linkedin_posts | linkedin_jobs | google | google_xray | crunchbase | tracxn | upwork | x_twitter | reddit | artstation | clutch | designrush | goodfirms | sortlist | google_alerts | instagram | youtube | tiktok | vimeo | government_registry",
  "query_text": "string — the exact search string to use",
  "query_type": "string — people | companies | jobs | posts | general",
  "category": "string — demand_signal | company_discovery | decision_maker | job_opportunity | platform_profile | news_monitoring",
  "frequency": "string — daily | weekly | biweekly | monthly | once | auto",
  "auto_run": "boolean — should Celery run this automatically?",
  "difficulty": "string — easy | medium | hard",
  "expected_results": "string — what you'll find",
  "notes": "string — tips for using this query"
}
```

### Query count by platform (from Excel)

|Platform               |Count  |Auto-runnable           |
|-----------------------|-------|------------------------|
|LinkedIn People Search |8      |No (manual)             |
|LinkedIn Company Search|3      |No (manual)             |
|LinkedIn Post Search   |6      |No (manual, daily check)|
|LinkedIn Job Search    |9      |Yes (daily scrape)      |
|Google X-Ray LinkedIn  |4      |Yes (weekly)            |
|Google Direct Search   |13     |Yes (weekly/monthly)    |
|Google Funded Startups |4      |Yes (weekly)            |
|Startup Databases      |5      |Partial                 |
|Upwork                 |8      |Yes (daily)             |
|X (Twitter)            |5      |Yes (daily)             |
|Reddit                 |6      |Yes (daily)             |
|Job Boards             |9      |Partial                 |
|Directories            |10     |No (monthly manual)     |
|Business Registries    |4      |No (monthly manual)     |
|Social Media           |4      |No (weekly manual)      |
|Google Alerts          |7      |Yes (auto)              |
|Niche Platforms        |8      |No (one-time setup)     |
|**TOTAL**              |**113**|~40 auto-runnable       |

-----

## 7. REGIONAL DISCOVERY CHANNELS (seed: reference data for Scraper Control Panel UI)

All channels from Excel Sheet 3 “Regional Discovery” — the app should display these as a guided checklist for each region.

### Structure per region

```json
{
  "region": "USA",
  "channels": [
    {
      "source": "Clutch.co",
      "method": "3D Animation → United States → Filter size 2-50",
      "url": "https://clutch.co",
      "what_to_find": "Small-mid agencies that outsource",
      "expected_companies": "200+",
      "frequency": "monthly",
      "last_scraped": null,
      "companies_found": 0,
      "notes": "Filter by reviews for quality"
    }
  ]
}
```

### Region summary

|Region|Discovery Channels|Expected Companies                |
|------|------------------|----------------------------------|
|USA   |10 channels       |1,500+                            |
|Europe|10 channels       |1,000+ (across UK, DE, FR, NL, ES)|
|UAE   |12 channels       |1,000+                            |
|Kuwait|11 channels       |500+                              |

-----

## 8. SNIPPET LIBRARY (seed: `outreach_snippets` or inline in template UI)

Reusable text blocks insertable with `/` shortcut in the message composer.

```json
[
  {
    "shortcut": "/bio",
    "title": "Short Bio",
    "content": "I'm Ibrahim, a 3D artist and motion designer specializing in anamorphic billboards, CGI motion design, and AI-accelerated creative workflows. Based in Dubai, working remotely with clients worldwide."
  },
  {
    "shortcut": "/clients",
    "title": "Client List",
    "content": "I've produced 3D content for brands including ALDO, Cadbury, Steve Madden, and Dubai Safari Park."
  },
  {
    "shortcut": "/services",
    "title": "Service List",
    "content": "→ Anamorphic 3D billboard production\n→ CGI motion design & product visualization\n→ AI-powered video production\n→ Interactive web experiences (Three.js, React)\n→ Architectural 3D visualization"
  },
  {
    "shortcut": "/tools",
    "title": "Tool Stack",
    "content": "Cinema 4D, Blender, Houdini, After Effects, Premiere Pro, Three.js, React, AI-assisted workflows (Midjourney, Runway, Veo)"
  },
  {
    "shortcut": "/portfolio",
    "title": "Portfolio Link",
    "content": "Portfolio: ibrahim3d.com"
  },
  {
    "shortcut": "/rates",
    "title": "Rate Info",
    "content": "I work at competitive rates ($20-40/hr equivalent) with project-based pricing available. Happy to discuss based on your specific needs."
  },
  {
    "shortcut": "/turnaround",
    "title": "Turnaround Promise",
    "content": "Typical turnaround: 24hr concept alignment, 3-5 day first draft, 2 revision rounds included. AI-assisted workflows mean faster delivery without quality compromise."
  },
  {
    "shortcut": "/whitelabel",
    "title": "White-Label Pitch",
    "content": "I work as a white-label production partner — your clients never know I exist. You sell, I produce. Same quality, lower overhead for your studio."
  },
  {
    "shortcut": "/viralx",
    "title": "Viral X Intro",
    "content": "I run Viral X (viralx.ae), a Dubai-registered 3D anamorphic billboard production studio. We produce immersive DOOH content for brands and agencies."
  },
  {
    "shortcut": "/cta-call",
    "title": "Call CTA",
    "content": "Would a quick 15-min call make sense to explore fit?"
  },
  {
    "shortcut": "/cta-soft",
    "title": "Soft CTA",
    "content": "Would it make sense to keep me in your freelancer pool for busy periods?"
  },
  {
    "shortcut": "/cta-portfolio",
    "title": "Portfolio CTA",
    "content": "Would you be open to seeing some relevant examples?"
  }
]
```

-----

## 9. AI COPILOT PROMPTS (seed: system prompts for each AI feature)

These are the Claude API system prompts used by each AI Copilot feature.

### Company Research Agent

```
SYSTEM PROMPT:
You are a competitive intelligence analyst helping a freelance 3D artist find business opportunities.

Given a company name and any available data (website, LinkedIn, industry), produce a structured research brief:

1. COMPANY OVERVIEW: What they do, how big they are, key markets
2. CREATIVE NEEDS: Based on their industry and recent activity, what 3D/motion/video services could they need?
3. RECENT ACTIVITY: Any recent campaigns, launches, expansions, or hires visible online?
4. KEY PEOPLE: Who would be the decision maker for outsourcing creative work? (title + likely LinkedIn search)
5. TALKING POINTS: 2-3 specific things to reference in outreach that show you've done your homework
6. SERVICE MATCH: Which of these services best fits their needs: anamorphic billboards, CGI motion, product visualization, architectural viz, AI video, interactive web
7. PRIORITY SCORE: 0-100 score with reasoning

Output as JSON.
```

### Message Personalization Agent

```
SYSTEM PROMPT:
You are an expert copywriter helping a freelance 3D artist personalize outreach messages.

You will receive:
- A template message with {{variables}}
- Company data (name, industry, recent projects, etc.)
- Contact data (name, title, etc.)

Your job:
1. Fill in all {{variables}} with specific, researched content
2. Rewrite the {{specific_project}} variable to reference something REAL about the company
3. Adjust tone to match the company culture (startup = casual, enterprise = professional, agency = creative peer)
4. Keep the message within the original length (don't make it longer)
5. Make it sound human, not templated

Output the final rendered message only. No explanations.
```

### Lead Scoring Agent

```
SYSTEM PROMPT:
You are a lead qualification expert for a freelance 3D artist / motion designer.

Score this company 0-100 based on these factors:
- SERVICE FIT (0-25): How well do their needs match 3D/CGI/motion/DOOH/AI video/product viz/arch viz?
- BUDGET LIKELIHOOD (0-25): Based on company size, funding, industry — can they afford $20-40/hr freelance?
- ACCESSIBILITY (0-25): How easy is it to reach the decision maker? Small company = easier. Enterprise = harder.
- TIMING (0-25): Any demand signals? (unfilled job, recent funding, expansion, seasonal peak, competitor campaign)

Output JSON:
{
  "score": int,
  "service_fit": int,
  "budget_likelihood": int,
  "accessibility": int,
  "timing": int,
  "reasoning": "1-2 sentence explanation",
  "recommended_action": "specific next step",
  "recommended_template": "template name from library"
}
```

### Upwork Proposal Generator

```
SYSTEM PROMPT:
You are an expert Upwork proposal writer for a freelance 3D artist.

You will receive: The full text of an Upwork job posting.

Write a proposal that:
1. Opens by referencing a SPECIFIC detail from their job description (prove you read it)
2. Connects their need to your relevant experience (ALDO, Cadbury, Steve Madden for commercial work)
3. Outlines a clear approach with timeline
4. Mentions AI-assisted workflow as a speed advantage
5. Lists relevant tools (Cinema 4D, Blender, Houdini, After Effects)
6. Ends with a soft call to action
7. Stays under 200 words
8. Sounds confident but not arrogant, professional but not corporate

Portfolio link: ibrahim3d.com
```

-----

## 10. DAILY TARGETS & SCORECARD (seed: `weekly_targets` config)

From Excel Sheet 5 “Weekly Playbook” — these are the default daily/weekly targets the scorecard tracks.

```json
{
  "daily_targets": {
    "linkedin_dms_sent": 5,
    "cold_emails_sent": 3,
    "upwork_proposals_sent": 3,
    "follow_ups_sent": 5,
    "companies_researched": 5,
    "companies_added": 3
  },
  "weekly_targets": {
    "linkedin_dms_sent": 20,
    "cold_emails_sent": 10,
    "upwork_proposals_sent": 10,
    "follow_ups_sent": 30,
    "companies_researched": 20,
    "companies_added": 10,
    "content_posts": 1,
    "meetings_booked": 2,
    "proposals_sent": 2
  },
  "monthly_targets": {
    "total_outreach": 300,
    "responses_received": 30,
    "meetings_booked": 8,
    "proposals_sent": 8,
    "deals_won": 2,
    "revenue": 2000
  },
  "streak_rules": {
    "minimum_daily_actions": 10,
    "streak_counts_weekdays_only": true,
    "streak_milestones": [7, 14, 30, 60, 90]
  }
}
```

-----

## 11. SERVICE TYPES & PRICING REFERENCE (seed: reference data)

Used by the AI pricing advisor and invoice generator.

```json
[
  {
    "service": "Anamorphic 3D Billboard",
    "hourly_range": "$30-50",
    "project_range": "$2,000-15,000",
    "typical_timeline": "2-6 weeks",
    "deliverables": "15-60 second anamorphic animation, screen-calibrated, multiple format outputs",
    "upsells": ["Social media cutdowns", "Behind-the-scenes video", "Multiple screen formats"]
  },
  {
    "service": "CGI Motion Design",
    "hourly_range": "$25-40",
    "project_range": "$500-5,000",
    "typical_timeline": "1-3 weeks",
    "deliverables": "15-60 second motion piece, 2 revision rounds",
    "upsells": ["Social media versions", "Looping versions", "Sound design"]
  },
  {
    "service": "Product Visualization / CGI Renders",
    "hourly_range": "$20-35",
    "project_range": "$200-2,000 per product",
    "typical_timeline": "3-7 days per product",
    "deliverables": "3-5 angles per product, white/lifestyle backgrounds, 4K resolution",
    "upsells": ["360 spin", "Animation", "AR-ready models", "Bulk discount for catalog"]
  },
  {
    "service": "Architectural Visualization",
    "hourly_range": "$25-40",
    "project_range": "$500-5,000 per view",
    "typical_timeline": "1-2 weeks per view",
    "deliverables": "Photorealistic exterior/interior render, day/night versions",
    "upsells": ["Walkthrough animation", "Aerial fly-through", "VR experience"]
  },
  {
    "service": "AI-Enhanced Video Production",
    "hourly_range": "$25-40",
    "project_range": "$500-3,000",
    "typical_timeline": "3-10 days",
    "deliverables": "AI-generated + manually refined video content",
    "upsells": ["Multiple variants", "A/B testing versions", "Localization"]
  },
  {
    "service": "Interactive Web (Three.js / WebGL)",
    "hourly_range": "$30-45",
    "project_range": "$1,000-10,000",
    "typical_timeline": "2-6 weeks",
    "deliverables": "Interactive 3D web experience, responsive, optimized",
    "upsells": ["CMS integration", "Analytics", "A/B testing", "Mobile optimization"]
  },
  {
    "service": "Explainer / Commercial Animation",
    "hourly_range": "$25-40",
    "project_range": "$1,000-8,000",
    "typical_timeline": "2-4 weeks",
    "deliverables": "30-90 second animated explainer or commercial",
    "upsells": ["Voiceover", "Sound design", "Multiple language versions", "Social cutdowns"]
  }
]
```

-----

## 12. KNOWN COMPANIES TO SEED (from Excel Sheet 1)

The first batch of companies to import into the database on app launch. These are from the original guerrilla targeting spreadsheet.

### Format per company

```json
{
  "name": "string",
  "category": "string (from category enum)",
  "country": "string",
  "city": "string",
  "website": "string",
  "why_target": "string",
  "priority": "A|B|C",
  "contact_strategy": "string",
  "services_needed": ["array of service types"],
  "notes": "string"
}
```

### Count by category (from Excel)

|Category                 |Companies|Priority A|Priority B|Priority C|
|-------------------------|---------|----------|----------|----------|
|DOOH / Anamorphic Studios|7        |4         |3         |0         |
|3D / CGI Studios         |12       |2         |7         |3         |
|Creative / Ad Agencies   |9        |4         |5         |0         |
|AI / Tech Startups       |5        |0         |3         |2         |
|Game Art Studios         |3        |0         |2         |1         |
|Dubai / MENA Agencies    |6        |4         |2         |0         |
|Production Houses        |5        |2         |2         |1         |
|Platforms to Join        |7        |4         |3         |0         |
|**TOTAL**                |**54**   |**20**    |**27**    |**7**     |

The full company records are in the Excel file Sheet 1. The app’s import function should parse that sheet and create records using the schema above.

-----

## 13. GOOGLE ALERTS CONFIGURATION (auto-setup on app launch)

These 7 Google Alerts from Excel Sheet 2 (queries #99-105) should be created via the Google Alerts integration and feed into the Intel Feed.

```json
[
  {
    "name": "3D Freelance Demand",
    "query": "\"looking for 3D artist\" OR \"need 3D freelancer\" OR \"hiring 3D animator\" remote",
    "frequency": "as_it_happens",
    "sources": "automatic",
    "language": "en",
    "region": "any"
  },
  {
    "name": "DOOH / Anamorphic News",
    "query": "\"anamorphic billboard\" OR \"3D billboard\" OR \"DOOH campaign\" launch",
    "frequency": "daily",
    "sources": "news",
    "language": "en",
    "region": "any"
  },
  {
    "name": "UAE Creative Industry",
    "query": "\"creative agency\" OR \"advertising agency\" Dubai OR Kuwait launch OR opens OR expands",
    "frequency": "daily",
    "sources": "automatic",
    "language": "en",
    "region": "any"
  },
  {
    "name": "MENA Funding Rounds",
    "query": "\"raises\" OR \"funding\" OR \"investment\" startup OR company Dubai OR Kuwait OR UAE OR MENA",
    "frequency": "daily",
    "sources": "news",
    "language": "en",
    "region": "any"
  },
  {
    "name": "3D Animation Industry Moves",
    "query": "\"3D animation\" OR \"motion design\" OR \"CGI\" studio OR agency launch OR opens OR hires",
    "frequency": "daily",
    "sources": "automatic",
    "language": "en",
    "region": "any"
  },
  {
    "name": "UAE Real Estate Launches",
    "query": "\"new project\" OR \"launches\" real estate OR property OR tower OR villa Dubai OR \"Abu Dhabi\" OR Kuwait",
    "frequency": "daily",
    "sources": "news",
    "language": "en",
    "region": "any"
  },
  {
    "name": "E-Commerce Brand Launches",
    "query": "\"launches\" OR \"new brand\" OR \"D2C\" product OR e-commerce render OR 3D OR visualization",
    "frequency": "weekly",
    "sources": "automatic",
    "language": "en",
    "region": "any"
  }
]
```

-----

## 14. DASHBOARD KPI DEFINITIONS

How each analytics metric is calculated from the database.

```json
{
  "pipeline_value": {
    "formula": "SUM(deals.estimated_value) WHERE deals.stage NOT IN ('Won', 'Lost')",
    "display": "currency",
    "label": "Pipeline Value"
  },
  "weighted_pipeline": {
    "formula": "SUM(deals.estimated_value * deals.probability / 100) WHERE deals.stage NOT IN ('Won', 'Lost')",
    "display": "currency",
    "label": "Weighted Pipeline"
  },
  "revenue_mtd": {
    "formula": "SUM(deals.won_amount) WHERE deals.actual_close_date >= FIRST_DAY_OF_MONTH",
    "display": "currency",
    "label": "Revenue (MTD)"
  },
  "revenue_ytd": {
    "formula": "SUM(deals.won_amount) WHERE deals.actual_close_date >= FIRST_DAY_OF_YEAR",
    "display": "currency",
    "label": "Revenue (YTD)"
  },
  "win_rate": {
    "formula": "COUNT(deals WHERE stage='Won') / COUNT(deals WHERE stage IN ('Won','Lost')) * 100",
    "display": "percentage",
    "label": "Win Rate"
  },
  "response_rate": {
    "formula": "COUNT(messages WHERE status='replied') / COUNT(messages WHERE status IN ('sent','delivered','opened','replied')) * 100",
    "display": "percentage",
    "label": "Response Rate"
  },
  "avg_deal_size": {
    "formula": "AVG(deals.won_amount) WHERE deals.stage = 'Won'",
    "display": "currency",
    "label": "Avg Deal Size"
  },
  "avg_days_to_close": {
    "formula": "AVG(deals.actual_close_date - deals.created_at) WHERE deals.stage = 'Won'",
    "display": "days",
    "label": "Avg Days to Close"
  },
  "outreach_today": {
    "formula": "COUNT(messages WHERE sent_at >= TODAY AND sent_at < TOMORROW)",
    "display": "number",
    "label": "Outreach Today"
  },
  "follow_ups_due": {
    "formula": "COUNT(tasks WHERE task_type='follow_up' AND due_date <= TODAY AND status='todo')",
    "display": "number",
    "label": "Follow-Ups Due"
  },
  "stale_deals": {
    "formula": "COUNT(deals WHERE updated_at < NOW() - INTERVAL '7 days' AND stage NOT IN ('Won','Lost','Nurture'))",
    "display": "number",
    "label": "Stale Deals"
  },
  "current_streak": {
    "formula": "Consecutive days where daily_metrics.outreach_sent + tasks_completed >= minimum_daily_actions",
    "display": "days",
    "label": "Current Streak"
  }
}
```

-----

## 15. FILE RELATIONSHIPS MAP

How all the pieces connect:

```
Excel Sheet 1 "Target Companies"
  → seeds `companies` table (54 initial records)
  → populates Pipeline Board on first launch
  → each company auto-generates a "Research" task

Excel Sheet 2 "Query Library (113)"
  → seeds `saved_queries` table (113 records)
  → populates Scraper Control Panel
  → ~40 queries marked auto_run=true → Celery periodic tasks

Excel Sheet 3 "Regional Discovery"
  → seeds regional discovery checklist UI
  → feeds the Scraper Control Panel per-region tabs
  → each channel = a clickable workflow with progress tracking

Excel Sheet 4 "Company Tracker"
  → replaced by the `companies` + `contacts` + `deals` tables
  → the app IS the tracker now

Excel Sheet 5 "Weekly Playbook"
  → seeds `daily_targets` config
  → drives the Weekly Scorecard analytics
  → auto-generates recurring tasks in `tasks` table

Excel Sheet 6 "Outreach Templates"
  → seeds `outreach_templates` table (11+ templates)
  → seeds `outreach_sequences` table (5 sequences)
  → seeds snippet library
  → populates the Outreach Command Center template picker
```

-----

## END OF DOCUMENT

This file + `TECHNICAL_PLAN_FreelanceCommandCenter.md` together form the complete specification. The technical plan defines HOW to build it. This document defines WHAT goes into it.

Next step: Start Phase 1 implementation.