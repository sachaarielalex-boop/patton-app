import streamlit as st

NB = {
    "Allapattah": {
        "zip": "33142", "lat": 25.8103, "lon": -80.2340,
        "tagline": "The emerging arts district redefining Miami's urban core",
        "desc": "Once an overlooked industrial corridor, Allapattah is undergoing a cultural metamorphosis. Anchored by the Rubell Museum and adjacent to the Jackson Health District.",
        "mkt": {"med_price": 420000, "psf": 310, "rent": 2200, "yield": 6.8, "yoy": 7.2, "dom": 28, "inv_mo": 2.8, "ls_ratio": 97.8, "range": "$250K-$800K", "lot": 5800, "type": "Single Family / Small Multifamily", "units_pipeline": 1200, "absorption": 85},
        "demo": {"pop": 52000, "income": 28500, "age": 34, "owner": 28, "renter": 72, "vacancy": 6.2, "college": 18, "foreign": 62},
        "scores": {"walk": 72, "transit": 55, "bike": 62},
        "zoning": {"primary": "T4-R / T5-O", "max_far": 3.5, "max_height": "65 ft", "min_lot": "5,000 sqft", "parking": "1 per unit", "setbacks": "10ft front / 5ft side", "allowed_uses": "Residential, Mixed-Use, Retail, Office, Live-Work"},
        "oz": True, "flood": "AE / X", "school": "C+", "crime": 42,
        "last_sales": [
            {"addr": "1845 NW 20th St", "price": 385000, "date": "2024-11", "sqft": 1250, "type": "SFR"},
            {"addr": "2121 NW 22nd Ct", "price": 520000, "date": "2024-09", "sqft": 1800, "type": "Duplex"},
            {"addr": "1901 NW 17th Ave", "price": 290000, "date": "2024-08", "sqft": 980, "type": "SFR"},
        ],
        "vacant_lots": [
            {"addr": "NW 20th St (Vacant)", "lot_sf": 7500, "zoning": "T5-O", "price": 450000, "potential_units": 6, "far": 3.5},
            {"addr": "NW 22nd Ave (Vacant)", "lot_sf": 12000, "zoning": "T5-L", "price": 680000, "potential_units": 10, "far": 2.5},
        ],
        "highlights": ["Opportunity Zone capital gains deferral", "Rubell Museum anchors arts corridor", "Adjacent to UM/Jackson Health campus", "Mixed-use pipeline >$1B"],
        "risks": ["Eastern AE flood zone exposure", "Income disparity may slow growth", "Supply may outpace absorption"],
    },
    "Coconut Grove": {
        "zip": "33133", "lat": 25.7270, "lon": -80.2417,
        "tagline": "Miami's original village - bayfront elegance since 1873",
        "desc": "Coconut Grove is Miami's oldest neighborhood, a verdant enclave where banyan-lined streets meet Biscayne Bay.",
        "mkt": {"med_price": 950000, "psf": 580, "rent": 3800, "yield": 4.2, "yoy": 5.8, "dom": 45, "inv_mo": 4.5, "ls_ratio": 95.2, "range": "$500K-$5M+", "lot": 8500, "type": "Single Family / Luxury Condo", "units_pipeline": 350, "absorption": 72},
        "demo": {"pop": 20000, "income": 82000, "age": 42, "owner": 58, "renter": 42, "vacancy": 8.1, "college": 72, "foreign": 35},
        "scores": {"walk": 81, "transit": 52, "bike": 74},
        "zoning": {"primary": "T3-R / T4-R", "max_far": 1.5, "max_height": "35 ft", "min_lot": "7,500 sqft", "parking": "2 per unit", "setbacks": "25ft front / 10ft side", "allowed_uses": "Residential, Limited Retail"},
        "oz": False, "flood": "AE / VE (coastal)", "school": "A-", "crime": 25,
        "last_sales": [
            {"addr": "3531 Main Hwy", "price": 2150000, "date": "2024-11", "sqft": 3200, "type": "SFR"},
            {"addr": "2821 S Bayshore Dr #12A", "price": 890000, "date": "2024-10", "sqft": 1650, "type": "Condo"},
        ],
        "vacant_lots": [
            {"addr": "S Bayshore Dr (Vacant)", "lot_sf": 15000, "zoning": "T3-R", "price": 2800000, "potential_units": 1, "far": 1.0},
        ],
        "highlights": ["Established luxury with generational demand", "CocoWalk premier retail anchor", "Bayfront marina access", "Top school zoning"],
        "risks": ["Premium entry compresses yields", "Coastal flood drives insurance up", "Limited developable land"],
    },
    "Westchester": {
        "zip": "33165", "lat": 25.7382, "lon": -80.3442,
        "tagline": "Suburban stability with institutional rental demand",
        "desc": "Classic Miami suburb with well-maintained homes, strong schools, FIU proximity drives rental demand.",
        "mkt": {"med_price": 520000, "psf": 290, "rent": 2400, "yield": 5.5, "yoy": 6.1, "dom": 30, "inv_mo": 3.0, "ls_ratio": 97.0, "range": "$350K-$750K", "lot": 6500, "type": "Single Family Residential", "units_pipeline": 200, "absorption": 90},
        "demo": {"pop": 55000, "income": 48000, "age": 40, "owner": 62, "renter": 38, "vacancy": 4.5, "college": 32, "foreign": 58},
        "scores": {"walk": 58, "transit": 38, "bike": 45},
        "zoning": {"primary": "EU-S / EU-M", "max_far": 0.5, "max_height": "35 ft", "min_lot": "6,000 sqft", "parking": "2 per unit", "setbacks": "25ft front / 7.5ft side", "allowed_uses": "Single Family, Duplex (conditional)"},
        "oz": False, "flood": "X (minimal)", "school": "B", "crime": 30,
        "last_sales": [
            {"addr": "9845 SW 42nd St", "price": 545000, "date": "2024-11", "sqft": 1800, "type": "SFR"},
            {"addr": "10220 SW 38th Terr", "price": 498000, "date": "2024-10", "sqft": 1650, "type": "SFR"},
        ],
        "vacant_lots": [],
        "highlights": ["FEMA Zone X - low flood risk", "High owner-occupancy stabilizes values", "FIU drives rental demand", "Strong family market"],
        "risks": ["Limited transit", "Lower appreciation ceiling", "Aging housing stock"],
    },
    "Little Havana": {
        "zip": "33135", "lat": 25.7658, "lon": -80.2275,
        "tagline": "Cultural capital meets investment frontier",
        "desc": "Miami's Cuban-American heartbeat. Walking distance to Brickell, Opportunity Zone status, highest yields in urban core.",
        "mkt": {"med_price": 385000, "psf": 295, "rent": 2100, "yield": 7.1, "yoy": 8.5, "dom": 22, "inv_mo": 2.2, "ls_ratio": 98.5, "range": "$200K-$650K", "lot": 5200, "type": "Multifamily / Small Lots", "units_pipeline": 800, "absorption": 92},
        "demo": {"pop": 62000, "income": 25000, "age": 38, "owner": 22, "renter": 78, "vacancy": 5.8, "college": 14, "foreign": 72},
        "scores": {"walk": 85, "transit": 62, "bike": 68},
        "zoning": {"primary": "T5-O / T4-R", "max_far": 3.0, "max_height": "56 ft", "min_lot": "5,000 sqft", "parking": "0.5 per unit (TOD)", "setbacks": "0ft front / 0ft side", "allowed_uses": "Mixed-Use, Multifamily, Retail, Office"},
        "oz": True, "flood": "X / AE (partial)", "school": "C", "crime": 48,
        "last_sales": [
            {"addr": "1520 SW 1st St", "price": 395000, "date": "2024-11", "sqft": 1100, "type": "SFR"},
            {"addr": "844 SW 6th St", "price": 680000, "date": "2024-10", "sqft": 2400, "type": "Triplex"},
        ],
        "vacant_lots": [
            {"addr": "SW 4th St (Vacant)", "lot_sf": 6000, "zoning": "T5-O", "price": 520000, "potential_units": 8, "far": 3.0},
        ],
        "highlights": ["Opportunity Zone + highest yield", "800m to Brickell", "Calle Ocho tourism", "22 days avg DOM"],
        "risks": ["Displacement concerns", "Low income limits rent ceiling", "Higher crime in select tracts"],
    },
    "Wynwood": {
        "zip": "33127", "lat": 25.8010, "lon": -80.1990,
        "tagline": "From warehouse district to global creative capital",
        "desc": "One of the world's most recognized arts districts. NRD-1 zoning, global brand recognition, tech and creative tenants.",
        "mkt": {"med_price": 620000, "psf": 520, "rent": 3200, "yield": 5.0, "yoy": 6.5, "dom": 35, "inv_mo": 3.5, "ls_ratio": 96.5, "range": "$400K-$1.5M", "lot": 4500, "type": "Condo / Mixed-Use", "units_pipeline": 2500, "absorption": 68},
        "demo": {"pop": 12000, "income": 42000, "age": 33, "owner": 30, "renter": 70, "vacancy": 9.5, "college": 48, "foreign": 40},
        "scores": {"walk": 88, "transit": 60, "bike": 78},
        "zoning": {"primary": "T5-O / T6-O (NRD-1)", "max_far": 5.0, "max_height": "85 ft", "min_lot": "5,000 sqft", "parking": "0.75 per unit", "setbacks": "0ft front / 0ft side", "allowed_uses": "Mixed-Use, Residential, Art Gallery, Restaurant, Retail, Office, Hotel"},
        "oz": True, "flood": "X / AE (partial)", "school": "B-", "crime": 38,
        "last_sales": [
            {"addr": "2700 NW 2nd Ave #PH", "price": 1250000, "date": "2024-11", "sqft": 2200, "type": "Condo"},
            {"addr": "50 NW 24th St #501", "price": 680000, "date": "2024-10", "sqft": 1100, "type": "Condo"},
        ],
        "vacant_lots": [
            {"addr": "NW 2nd Ave (Vacant)", "lot_sf": 8000, "zoning": "T6-O NRD-1", "price": 3200000, "potential_units": 20, "far": 5.0},
        ],
        "highlights": ["Global brand recognition", "NRD-1 high density", "2M+ annual visitors", "Tech/creative tenant base"],
        "risks": ["Elevated new construction vacancy", "Peak pricing in core blocks", "Tourism demand seasonality"],
    },
    "Brickell": {
        "zip": "33131", "lat": 25.7617, "lon": -80.1918,
        "tagline": "The financial district of the Americas",
        "desc": "Miami's Wall Street - luxury towers, Fortune 500 offices, Brickell City Centre. Highest density in Florida.",
        "mkt": {"med_price": 580000, "psf": 480, "rent": 3400, "yield": 4.8, "yoy": 5.2, "dom": 42, "inv_mo": 5.0, "ls_ratio": 94.5, "range": "$350K-$3M+", "lot": 0, "type": "High-Rise Condo", "units_pipeline": 4000, "absorption": 62},
        "demo": {"pop": 35000, "income": 75000, "age": 35, "owner": 35, "renter": 65, "vacancy": 10.2, "college": 68, "foreign": 55},
        "scores": {"walk": 94, "transit": 82, "bike": 72},
        "zoning": {"primary": "T6-36 / T6-80", "max_far": 25.0, "max_height": "850 ft", "min_lot": "20,000 sqft", "parking": "1.5 per unit", "setbacks": "Per UDRB review", "allowed_uses": "Residential, Office, Hotel, Retail, Mixed-Use"},
        "oz": False, "flood": "AE / VE (coastal)", "school": "B+", "crime": 32,
        "last_sales": [
            {"addr": "1300 Brickell Bay Dr #4201", "price": 1850000, "date": "2024-11", "sqft": 2100, "type": "Condo"},
            {"addr": "801 S Miami Ave #2305", "price": 620000, "date": "2024-10", "sqft": 1050, "type": "Condo"},
        ],
        "vacant_lots": [],
        "highlights": ["94 Walk Score - highest in Miami", "Brickell City Centre anchor", "Fortune 500 relocations", "Metromover connectivity"],
        "risks": ["4,000 units in pipeline", "10%+ vacancy in older towers", "Coastal flood insurance costs"],
    },
    "Overtown": {
        "zip": "33136", "lat": 25.7862, "lon": -80.2020,
        "tagline": "Historic gateway positioned for transformative growth",
        "desc": "Adjacent to Health District and Brightline station. Triple-stacked incentives (OZ + CRA + LIHTC) make this Miami's strongest incentive zone.",
        "mkt": {"med_price": 310000, "psf": 240, "rent": 1800, "yield": 7.5, "yoy": 9.2, "dom": 18, "inv_mo": 1.8, "ls_ratio": 99.0, "range": "$150K-$500K", "lot": 6000, "type": "Multifamily / Mixed-Use", "units_pipeline": 1500, "absorption": 88},
        "demo": {"pop": 10000, "income": 18000, "age": 36, "owner": 12, "renter": 88, "vacancy": 7.5, "college": 10, "foreign": 45},
        "scores": {"walk": 78, "transit": 72, "bike": 58},
        "zoning": {"primary": "T5-O / T6-O", "max_far": 4.0, "max_height": "75 ft", "min_lot": "5,000 sqft", "parking": "0.5 per unit", "setbacks": "0ft front / 0ft side", "allowed_uses": "Mixed-Use, Multifamily, Retail, Office, Community"},
        "oz": True, "flood": "X / AE (partial)", "school": "C-", "crime": 55,
        "last_sales": [
            {"addr": "1601 NW 1st Ct", "price": 280000, "date": "2024-10", "sqft": 1200, "type": "SFR"},
            {"addr": "1450 NW 3rd Ave", "price": 350000, "date": "2024-09", "sqft": 1500, "type": "Duplex"},
        ],
        "vacant_lots": [
            {"addr": "NW 1st Ct (Vacant)", "lot_sf": 10000, "zoning": "T6-O", "price": 650000, "potential_units": 12, "far": 4.0},
        ],
        "highlights": ["Strongest incentive stacking in Florida", "Brightline station adjacency", "Health District employment base", "Lowest land cost in urban core"],
        "risks": ["Highest crime rate in dataset", "Income disparity challenges", "Community displacement concerns"],
    },
    "Coral Gables": {
        "zip": "33146", "lat": 25.7490, "lon": -80.2595,
        "tagline": "The City Beautiful - premier commercial and office submarket",
        "desc": "South Florida's most prestigious office submarket. Home to multinational HQs, consulates, and Class A office towers along Ponce de Leon and Alhambra corridors.",
        "mkt": {"med_price": 750000, "psf": 420, "rent": 3600, "yield": 4.8, "yoy": 4.5, "dom": 55, "inv_mo": 5.5, "ls_ratio": 94.0, "range": "$450K-$3M+", "lot": 7000, "type": "Office / Mixed-Use / Luxury Residential", "units_pipeline": 600, "absorption": 70},
        "demo": {"pop": 51000, "income": 92000, "age": 44, "owner": 55, "renter": 45, "vacancy": 6.5, "college": 68, "foreign": 42},
        "scores": {"walk": 72, "transit": 55, "bike": 60},
        "zoning": {"primary": "MX-2 / C (Commercial)", "max_far": 4.5, "max_height": "190 ft (varies by corridor)", "min_lot": "5,000 sqft", "parking": "3.3/1,000 RSF (office)", "setbacks": "Per Coral Gables Zoning Code", "allowed_uses": "Office, Retail, Restaurant, Hotel, Mixed-Use, Medical, Professional Services"},
        "oz": False, "flood": "X / AE (partial)", "school": "A", "crime": 18,
        "last_sales": [
            {"addr": "4000 Ponce de Leon Blvd", "price": 28500000, "date": "2024-06", "sqft": 120000, "type": "Office Building"},
            {"addr": "2600 Douglas Rd", "price": 15200000, "date": "2024-03", "sqft": 65000, "type": "Office Building"},
        ],
        "vacant_lots": [],
        "highlights": ["Premier Class A office submarket", "Multinational HQ concentration", "University of Miami anchor", "Low crime, A-rated schools", "Strong commercial tenant base"],
        "risks": ["High entry cost limits yield", "Coral Gables has own strict zoning code", "Limited new supply increases competition"],
    },
    "Edgewater": {
        "zip": "33137", "lat": 25.7950, "lon": -80.1880,
        "tagline": "Bay views at Brickell-adjacent pricing",
        "desc": "Bayfront corridor between Wynwood and Downtown. Panoramic bay views, walkable to Design District.",
        "mkt": {"med_price": 720000, "psf": 550, "rent": 3500, "yield": 4.5, "yoy": 6.0, "dom": 38, "inv_mo": 4.0, "ls_ratio": 95.8, "range": "$400K-$2.5M", "lot": 5000, "type": "High-Rise Condo", "units_pipeline": 3000, "absorption": 65},
        "demo": {"pop": 25000, "income": 62000, "age": 34, "owner": 32, "renter": 68, "vacancy": 9.0, "college": 55, "foreign": 48},
        "scores": {"walk": 82, "transit": 58, "bike": 70},
        "zoning": {"primary": "T6-24 / T6-36", "max_far": 12.0, "max_height": "400 ft", "min_lot": "10,000 sqft", "parking": "1.5 per unit", "setbacks": "Per UDRB review", "allowed_uses": "Residential, Mixed-Use, Retail, Office, Hotel"},
        "oz": False, "flood": "AE / VE (coastal)", "school": "B", "crime": 35,
        "last_sales": [
            {"addr": "420 NE 31st St #PH", "price": 1650000, "date": "2024-11", "sqft": 2400, "type": "Condo"},
            {"addr": "501 NE 31st St #1208", "price": 580000, "date": "2024-10", "sqft": 1100, "type": "Condo"},
        ],
        "vacant_lots": [
            {"addr": "NE 31st St (Vacant)", "lot_sf": 12000, "zoning": "T6-24", "price": 7200000, "potential_units": 50, "far": 12.0},
        ],
        "highlights": ["Panoramic bay views", "Design District walkable", "Lower PSF than Brickell", "Strong international demand"],
        "risks": ["3,000+ units in pipeline", "Coastal exposure", "Limited ground-floor retail activation"],
    },
    # ── COMMERCIAL / OFFICE CORRIDORS ──────────────────────
    "Doral": {
        "zip": "33122", "lat": 25.8195, "lon": -80.3390,
        "tagline": "Miami's corporate powerhouse and logistics hub",
        "desc": "Doral is the commercial engine of Miami-Dade, home to major corporate HQs, the Free Trade Zone, and direct access to MIA and major highways.",
        "mkt": {"med_price": 480000, "psf": 320, "rent": 2600, "yield": 5.8, "yoy": 5.5, "dom": 32, "inv_mo": 3.2, "ls_ratio": 96.5, "range": "$300K-$1.2M", "lot": 5500, "type": "Office / Industrial / Residential", "units_pipeline": 1800, "absorption": 80},
        "demo": {"pop": 82000, "income": 65000, "age": 38, "owner": 48, "renter": 52, "vacancy": 5.0, "college": 42, "foreign": 68},
        "scores": {"walk": 45, "transit": 28, "bike": 38},
        "zoning": {"primary": "BU-1 / BU-2 (Commercial)", "max_far": 2.5, "max_height": "120 ft (varies)", "min_lot": "5,000 sqft", "parking": "4/1,000 RSF (office)", "setbacks": "25ft front / 10ft side", "allowed_uses": "Office, Retail, Industrial, Warehouse, Mixed-Use, Hotel"},
        "oz": False, "flood": "X (minimal)", "school": "A-", "crime": 22,
        "last_sales": [
            {"addr": "8550 NW 33rd St", "price": 12500000, "date": "2024-08", "sqft": 51620, "type": "Office Building"},
            {"addr": "8200 NW 41st St", "price": 18000000, "date": "2024-05", "sqft": 85000, "type": "Office Building"},
        ],
        "vacant_lots": [],
        "highlights": ["MIA airport 5 min", "Free Trade Zone", "Corporate HQ concentration", "Turnpike/826/836 interchange", "Low flood risk Zone X"],
        "risks": ["Car-dependent suburb", "Limited transit", "Industrial adjacency"],
    },
    "Airport West": {
        "zip": "33126", "lat": 25.7903, "lon": -80.3167,
        "tagline": "Miami's office park corridor near MIA",
        "desc": "The Waterford, Blue Lagoon, and Doral Gateway districts anchor this major office submarket adjacent to Miami International Airport.",
        "mkt": {"med_price": 420000, "psf": 280, "rent": 2300, "yield": 6.0, "yoy": 4.8, "dom": 35, "inv_mo": 3.5, "ls_ratio": 95.5, "range": "$250K-$900K", "lot": 6000, "type": "Office / Industrial / Mixed-Use", "units_pipeline": 500, "absorption": 75},
        "demo": {"pop": 45000, "income": 52000, "age": 40, "owner": 38, "renter": 62, "vacancy": 8.0, "college": 35, "foreign": 60},
        "scores": {"walk": 42, "transit": 35, "bike": 30},
        "zoning": {"primary": "BU-2 / IU-1 (Commercial/Industrial)", "max_far": 2.0, "max_height": "75 ft", "min_lot": "7,500 sqft", "parking": "4/1,000 RSF", "setbacks": "25ft front / 10ft side", "allowed_uses": "Office, Warehouse, Industrial, Retail, Hotel, Mixed-Use"},
        "oz": False, "flood": "X (minimal)", "school": "B", "crime": 28,
        "last_sales": [
            {"addr": "6205 Blue Lagoon Dr", "price": 22000000, "date": "2024-07", "sqft": 90000, "type": "Office Building"},
            {"addr": "7795 NW 46th St", "price": 8500000, "date": "2024-04", "sqft": 42000, "type": "Office Building"},
        ],
        "vacant_lots": [],
        "highlights": ["Direct MIA access", "Waterford Business District", "Blue Lagoon office cluster", "Major highway connectivity"],
        "risks": ["Aging office stock", "Airport noise", "Car-dependent"],
    },
    "Downtown Miami": {
        "zip": "33132", "lat": 25.7751, "lon": -80.1947,
        "tagline": "Miami's urban core - government, courts, and rising towers",
        "desc": "The civic and commercial center of Miami. Home to government offices, federal courthouse, Bayside, AmericanAirlines Arena, and a boom of new residential towers.",
        "mkt": {"med_price": 480000, "psf": 420, "rent": 2800, "yield": 5.2, "yoy": 5.8, "dom": 40, "inv_mo": 4.5, "ls_ratio": 95.0, "range": "$250K-$2M", "lot": 0, "type": "High-Rise Condo / Office", "units_pipeline": 5000, "absorption": 60},
        "demo": {"pop": 95000, "income": 45000, "age": 36, "owner": 25, "renter": 75, "vacancy": 11.0, "college": 42, "foreign": 52},
        "scores": {"walk": 92, "transit": 85, "bike": 68},
        "zoning": {"primary": "T6-36 / T6-48 / T6-80", "max_far": 20.0, "max_height": "850 ft", "min_lot": "10,000 sqft", "parking": "1/unit", "setbacks": "Per UDRB review", "allowed_uses": "Office, Residential, Hotel, Retail, Government, Mixed-Use, Entertainment"},
        "oz": True, "flood": "AE / VE (coastal)", "school": "B-", "crime": 45,
        "last_sales": [
            {"addr": "200 S Biscayne Blvd #4505", "price": 1250000, "date": "2024-10", "sqft": 1800, "type": "Condo"},
            {"addr": "50 Biscayne Blvd #3702", "price": 680000, "date": "2024-08", "sqft": 1100, "type": "Condo"},
        ],
        "vacant_lots": [],
        "highlights": ["Highest transit score in Miami", "Brightline station", "Government anchor tenants", "Metromover free transit"],
        "risks": ["High vacancy in older towers", "Street-level safety concerns", "Oversupply risk"],
    },
    "Design District": {
        "zip": "33137", "lat": 25.8120, "lon": -80.1920,
        "tagline": "Luxury retail and creative offices in Miami's fashion capital",
        "desc": "Curated luxury enclave with Louis Vuitton, Dior, Prada flagships. High-end office and showroom space attracts fashion, design, and tech tenants.",
        "mkt": {"med_price": 850000, "psf": 620, "rent": 4200, "yield": 4.0, "yoy": 5.5, "dom": 50, "inv_mo": 5.0, "ls_ratio": 94.0, "range": "$500K-$3M+", "lot": 4000, "type": "Luxury Retail / Office / Condo", "units_pipeline": 800, "absorption": 60},
        "demo": {"pop": 8000, "income": 55000, "age": 35, "owner": 25, "renter": 75, "vacancy": 8.5, "college": 52, "foreign": 45},
        "scores": {"walk": 85, "transit": 55, "bike": 72},
        "zoning": {"primary": "T5-O / T6-O (NRD-1)", "max_far": 5.0, "max_height": "85 ft", "min_lot": "5,000 sqft", "parking": "0.75/unit", "setbacks": "0ft", "allowed_uses": "Luxury Retail, Showroom, Office, Gallery, Restaurant, Mixed-Use"},
        "oz": False, "flood": "X", "school": "B", "crime": 30,
        "last_sales": [
            {"addr": "3841 NE 2nd Ave #PH", "price": 2200000, "date": "2024-09", "sqft": 2800, "type": "Condo"},
        ],
        "vacant_lots": [],
        "highlights": ["Global luxury brand anchor", "Craig Robins master plan", "ICA museum", "High foot traffic"],
        "risks": ["Ultra-premium pricing", "Niche tenant pool", "Seasonal tourism dependency"],
    },
    "Midtown": {
        "zip": "33137", "lat": 25.8050, "lon": -80.1910,
        "tagline": "Urban living between Wynwood and the Design District",
        "desc": "Master-planned urban neighborhood with Midtown Miami shops, restaurants, and mid-rise residential. Popular with young professionals.",
        "mkt": {"med_price": 550000, "psf": 450, "rent": 2900, "yield": 5.0, "yoy": 5.5, "dom": 35, "inv_mo": 3.8, "ls_ratio": 95.5, "range": "$350K-$1.5M", "lot": 0, "type": "Condo / Mixed-Use", "units_pipeline": 1500, "absorption": 70},
        "demo": {"pop": 15000, "income": 58000, "age": 33, "owner": 30, "renter": 70, "vacancy": 7.5, "college": 55, "foreign": 42},
        "scores": {"walk": 88, "transit": 58, "bike": 75},
        "zoning": {"primary": "T5-O / T6-O", "max_far": 5.0, "max_height": "85 ft", "min_lot": "5,000 sqft", "parking": "1/unit", "setbacks": "0ft", "allowed_uses": "Mixed-Use, Residential, Retail, Office, Restaurant"},
        "oz": False, "flood": "X", "school": "B", "crime": 32,
        "last_sales": [
            {"addr": "3301 NE 1st Ave #H2010", "price": 520000, "date": "2024-10", "sqft": 1050, "type": "Condo"},
        ],
        "vacant_lots": [],
        "highlights": ["Master-planned walkable community", "Target, Ross, dining anchors", "Between Wynwood & Design District"],
        "risks": ["Traffic congestion on Midtown Blvd", "Aging first-gen condo stock"],
    },
    "Miami Beach": {
        "zip": "33139", "lat": 25.7907, "lon": -80.1300,
        "tagline": "Iconic beachfront living and hospitality capital",
        "desc": "World-famous barrier island destination. Art Deco Historic District, luxury condos, five-star hotels, and a thriving hospitality economy.",
        "mkt": {"med_price": 680000, "psf": 650, "rent": 3800, "yield": 4.2, "yoy": 4.0, "dom": 55, "inv_mo": 6.0, "ls_ratio": 92.0, "range": "$350K-$10M+", "lot": 0, "type": "Condo / Hotel / Mixed-Use", "units_pipeline": 2000, "absorption": 55},
        "demo": {"pop": 92000, "income": 52000, "age": 42, "owner": 32, "renter": 68, "vacancy": 12.0, "college": 48, "foreign": 55},
        "scores": {"walk": 90, "transit": 62, "bike": 82},
        "zoning": {"primary": "RM-3 / CD-3 (Miami Beach Code)", "max_far": 3.5, "max_height": "200 ft (varies by district)", "min_lot": "5,000 sqft", "parking": "1.5/unit", "setbacks": "Varies", "allowed_uses": "Residential, Hotel, Retail, Restaurant, Office, Entertainment, Mixed-Use"},
        "oz": False, "flood": "AE / VE (coastal)", "school": "B+", "crime": 38,
        "last_sales": [
            {"addr": "1000 S Pointe Dr #2601", "price": 4500000, "date": "2024-11", "sqft": 3200, "type": "Condo"},
            {"addr": "1500 Ocean Dr #305", "price": 750000, "date": "2024-09", "sqft": 900, "type": "Condo"},
        ],
        "vacant_lots": [],
        "highlights": ["World-class beachfront", "Art Deco historic charm", "Tourism-driven economy", "International brand recognition"],
        "risks": ["Sea level rise exposure", "High insurance costs", "Seasonal vacancy", "Short-term rental regulations"],
    },
    "Aventura": {
        "zip": "33180", "lat": 25.9565, "lon": -80.1392,
        "tagline": "Upscale suburban living anchored by Aventura Mall",
        "desc": "Affluent city in North Miami-Dade anchored by Aventura Mall, the 5th largest mall in the US. High-rise condos and excellent schools.",
        "mkt": {"med_price": 620000, "psf": 380, "rent": 3200, "yield": 4.5, "yoy": 4.8, "dom": 48, "inv_mo": 5.0, "ls_ratio": 94.5, "range": "$300K-$4M+", "lot": 0, "type": "High-Rise Condo / Retail", "units_pipeline": 800, "absorption": 65},
        "demo": {"pop": 40000, "income": 72000, "age": 45, "owner": 45, "renter": 55, "vacancy": 8.0, "college": 52, "foreign": 58},
        "scores": {"walk": 68, "transit": 42, "bike": 55},
        "zoning": {"primary": "B2 / TC-2 (Aventura Code)", "max_far": 3.0, "max_height": "250 ft (varies)", "min_lot": "10,000 sqft", "parking": "3/1,000 RSF", "setbacks": "Varies", "allowed_uses": "Retail, Office, Hotel, Residential, Mixed-Use"},
        "oz": False, "flood": "AE (coastal)", "school": "A", "crime": 15,
        "last_sales": [
            {"addr": "19501 W Country Club Dr #2408", "price": 1850000, "date": "2024-10", "sqft": 2200, "type": "Condo"},
        ],
        "vacant_lots": [],
        "highlights": ["Aventura Mall anchor", "Top-rated schools", "Lowest crime in dataset", "Brightline planned station"],
        "risks": ["Premium pricing limits yield", "Limited development land", "Car-dependent"],
    },
    "Kendall": {
        "zip": "33176", "lat": 25.6790, "lon": -80.3550,
        "tagline": "Miami's largest suburban corridor with steady growth",
        "desc": "Sprawling suburban community in South Miami-Dade. Major retail centers, Baptist Health campus, and strong family-oriented residential base.",
        "mkt": {"med_price": 520000, "psf": 280, "rent": 2400, "yield": 5.5, "yoy": 5.2, "dom": 30, "inv_mo": 3.0, "ls_ratio": 97.0, "range": "$350K-$1M", "lot": 7500, "type": "Single Family / Townhouse / Office", "units_pipeline": 400, "absorption": 85},
        "demo": {"pop": 80000, "income": 62000, "age": 42, "owner": 65, "renter": 35, "vacancy": 4.0, "college": 42, "foreign": 55},
        "scores": {"walk": 45, "transit": 30, "bike": 35},
        "zoning": {"primary": "BU-1 / EU-M (County)", "max_far": 1.5, "max_height": "55 ft", "min_lot": "6,500 sqft", "parking": "4/1,000 RSF", "setbacks": "25ft front / 10ft side", "allowed_uses": "Residential, Retail, Office, Medical, Restaurant"},
        "oz": False, "flood": "X / AE (partial)", "school": "A-", "crime": 20,
        "last_sales": [
            {"addr": "8700 SW 117th Ave", "price": 545000, "date": "2024-10", "sqft": 2000, "type": "SFR"},
            {"addr": "12550 SW 88th St", "price": 480000, "date": "2024-08", "sqft": 1700, "type": "Townhouse"},
        ],
        "vacant_lots": [],
        "highlights": ["Baptist Health campus", "Dadeland Mall proximity", "Strong school ratings", "Low crime"],
        "risks": ["Car-dependent suburban", "Limited transit", "Flood risk in southern areas"],
    },
    "Hialeah": {
        "zip": "33012", "lat": 25.8576, "lon": -80.2781,
        "tagline": "Working-class industrial powerhouse of Miami-Dade",
        "desc": "6th largest city in Florida. Dense, working-class, Hispanic-majority city with massive industrial/warehouse inventory and affordable housing.",
        "mkt": {"med_price": 420000, "psf": 260, "rent": 2100, "yield": 6.2, "yoy": 6.5, "dom": 25, "inv_mo": 2.5, "ls_ratio": 97.5, "range": "$250K-$650K", "lot": 5000, "type": "Single Family / Industrial / Warehouse", "units_pipeline": 600, "absorption": 90},
        "demo": {"pop": 240000, "income": 35000, "age": 40, "owner": 45, "renter": 55, "vacancy": 4.5, "college": 18, "foreign": 72},
        "scores": {"walk": 65, "transit": 42, "bike": 48},
        "zoning": {"primary": "C-2 / I-1 (Hialeah Code)", "max_far": 2.0, "max_height": "75 ft (varies)", "min_lot": "5,000 sqft", "parking": "4/1,000 RSF", "setbacks": "20ft front / 5ft side", "allowed_uses": "Industrial, Warehouse, Retail, Office, Mixed-Use, Manufacturing"},
        "oz": False, "flood": "X (minimal)", "school": "B-", "crime": 35,
        "last_sales": [
            {"addr": "1065 E 25th St", "price": 385000, "date": "2024-10", "sqft": 1400, "type": "SFR"},
            {"addr": "780 W 29th St", "price": 2800000, "date": "2024-07", "sqft": 15000, "type": "Warehouse"},
        ],
        "vacant_lots": [],
        "highlights": ["Largest Hispanic market in US", "Affordable entry point", "Industrial tenant demand", "Metrorail connection"],
        "risks": ["Low income limits rents", "Aging infrastructure", "Limited upside in residential"],
    },
    "North Miami": {
        "zip": "33161", "lat": 25.8900, "lon": -80.1860,
        "tagline": "Emerging waterfront opportunity in North Miami-Dade",
        "desc": "Growing city between Aventura and Miami Shores. Museum of Contemporary Art, FIU Biscayne Bay campus, and waterfront redevelopment.",
        "mkt": {"med_price": 420000, "psf": 300, "rent": 2200, "yield": 5.8, "yoy": 6.0, "dom": 30, "inv_mo": 3.0, "ls_ratio": 96.0, "range": "$250K-$800K", "lot": 6000, "type": "Single Family / Multifamily / Mixed-Use", "units_pipeline": 1000, "absorption": 78},
        "demo": {"pop": 62000, "income": 35000, "age": 36, "owner": 30, "renter": 70, "vacancy": 6.5, "college": 22, "foreign": 55},
        "scores": {"walk": 62, "transit": 40, "bike": 50},
        "zoning": {"primary": "BU-2 / RU-4 (City Code)", "max_far": 2.5, "max_height": "100 ft (varies)", "min_lot": "5,000 sqft", "parking": "1.5/unit", "setbacks": "25ft front / 10ft side", "allowed_uses": "Residential, Office, Retail, Mixed-Use, Institutional"},
        "oz": True, "flood": "AE (coastal)", "school": "C+", "crime": 42,
        "last_sales": [
            {"addr": "12550 NE 7th Ave", "price": 395000, "date": "2024-09", "sqft": 1300, "type": "SFR"},
        ],
        "vacant_lots": [],
        "highlights": ["Opportunity Zone", "FIU Biscayne campus", "MOCA museum", "Waterfront potential"],
        "risks": ["Higher crime areas", "Scattered development pattern", "Limited premium tenant base"],
    },
    "Sunny Isles Beach": {
        "zip": "33160", "lat": 25.9406, "lon": -80.1225,
        "tagline": "Luxury beachfront towers - 'Little Moscow' of Miami",
        "desc": "Ultra-luxury oceanfront condo corridor with Porsche, Ritz-Carlton, Armani-branded towers. Strong international buyer base.",
        "mkt": {"med_price": 750000, "psf": 580, "rent": 3800, "yield": 3.8, "yoy": 3.5, "dom": 65, "inv_mo": 7.0, "ls_ratio": 91.0, "range": "$400K-$15M+", "lot": 0, "type": "Luxury High-Rise Condo", "units_pipeline": 1200, "absorption": 50},
        "demo": {"pop": 23000, "income": 65000, "age": 48, "owner": 40, "renter": 60, "vacancy": 15.0, "college": 45, "foreign": 68},
        "scores": {"walk": 72, "transit": 35, "bike": 60},
        "zoning": {"primary": "RM-3 / TC-3 (City Code)", "max_far": 5.0, "max_height": "500 ft+", "min_lot": "20,000 sqft", "parking": "1.5/unit", "setbacks": "Varies", "allowed_uses": "Residential, Hotel, Retail, Restaurant"},
        "oz": False, "flood": "VE / AE (coastal)", "school": "A-", "crime": 12,
        "last_sales": [
            {"addr": "18975 Collins Ave #4505", "price": 3200000, "date": "2024-11", "sqft": 2800, "type": "Condo"},
        ],
        "vacant_lots": [],
        "highlights": ["Ultra-luxury branded residences", "Direct oceanfront", "Low crime", "International buyer pool"],
        "risks": ["High vacancy", "Sea level rise", "Foreign buyer dependency", "Insurance costs"],
    },
    "Key Biscayne": {
        "zip": "33149", "lat": 25.6937, "lon": -80.1628,
        "tagline": "Exclusive island paradise for Miami's elite",
        "desc": "Barrier island accessible via Rickenbacker Causeway. Ultra-exclusive residential community with Crandon Park and Bill Baggs State Park.",
        "mkt": {"med_price": 1800000, "psf": 780, "rent": 5500, "yield": 3.2, "yoy": 3.0, "dom": 75, "inv_mo": 8.0, "ls_ratio": 90.0, "range": "$800K-$25M+", "lot": 10000, "type": "Luxury SFR / Condo", "units_pipeline": 100, "absorption": 45},
        "demo": {"pop": 14000, "income": 125000, "age": 48, "owner": 65, "renter": 35, "vacancy": 12.0, "college": 75, "foreign": 50},
        "scores": {"walk": 55, "transit": 18, "bike": 65},
        "zoning": {"primary": "RS-1 / RS-2 (Village Code)", "max_far": 0.5, "max_height": "35 ft", "min_lot": "10,000 sqft", "parking": "2/unit", "setbacks": "25ft front / 10ft side", "allowed_uses": "Single Family Residential, Limited Retail"},
        "oz": False, "flood": "VE / AE (coastal)", "school": "A+", "crime": 8,
        "last_sales": [
            {"addr": "455 Grand Bay Dr #PH", "price": 12500000, "date": "2024-10", "sqft": 5500, "type": "Condo"},
        ],
        "vacant_lots": [],
        "highlights": ["Most exclusive address in Miami", "A+ schools", "Lowest crime", "Crandon Park beaches"],
        "risks": ["Causeway-dependent access", "Extreme hurricane exposure", "Insurance costs prohibitive"],
    },
    "South Miami": {
        "zip": "33143", "lat": 25.7080, "lon": -80.2930,
        "tagline": "Walkable downtown village near UM and Dadeland",
        "desc": "Charming small city with walkable downtown, proximity to University of Miami and Dadeland Mall. Metrorail connected.",
        "mkt": {"med_price": 650000, "psf": 380, "rent": 2800, "yield": 4.8, "yoy": 4.5, "dom": 42, "inv_mo": 4.2, "ls_ratio": 95.0, "range": "$400K-$1.5M", "lot": 7000, "type": "SFR / Condo / Office", "units_pipeline": 300, "absorption": 72},
        "demo": {"pop": 13000, "income": 58000, "age": 40, "owner": 48, "renter": 52, "vacancy": 6.0, "college": 55, "foreign": 40},
        "scores": {"walk": 72, "transit": 55, "bike": 58},
        "zoning": {"primary": "MX / NB (City Code)", "max_far": 2.5, "max_height": "100 ft (varies)", "min_lot": "5,000 sqft", "parking": "3/1,000 RSF", "setbacks": "10ft front", "allowed_uses": "Office, Retail, Restaurant, Residential, Mixed-Use, Medical"},
        "oz": False, "flood": "X", "school": "A", "crime": 18,
        "last_sales": [
            {"addr": "5801 SW 73rd St", "price": 620000, "date": "2024-09", "sqft": 1800, "type": "SFR"},
        ],
        "vacant_lots": [],
        "highlights": ["Metrorail South Miami station", "Walkable downtown", "UM proximity", "Low flood risk"],
        "risks": ["Small market limits inventory", "Premium pricing", "Limited large-scale development"],
    },
    "Pinecrest": {
        "zip": "33156", "lat": 25.6650, "lon": -80.3080,
        "tagline": "Premier family enclave with top-rated schools",
        "desc": "Affluent residential village known for top public schools, large lots, and estate homes. Minimal commercial - purely residential character.",
        "mkt": {"med_price": 1200000, "psf": 450, "rent": 4200, "yield": 3.5, "yoy": 3.8, "dom": 60, "inv_mo": 6.5, "ls_ratio": 93.0, "range": "$700K-$8M+", "lot": 15000, "type": "Luxury Single Family", "units_pipeline": 50, "absorption": 55},
        "demo": {"pop": 19000, "income": 115000, "age": 45, "owner": 82, "renter": 18, "vacancy": 4.0, "college": 72, "foreign": 35},
        "scores": {"walk": 35, "transit": 22, "bike": 42},
        "zoning": {"primary": "E-1 / E-2 (Village Code)", "max_far": 0.35, "max_height": "35 ft", "min_lot": "15,000 sqft", "parking": "2/unit", "setbacks": "35ft front / 15ft side", "allowed_uses": "Single Family Residential"},
        "oz": False, "flood": "X", "school": "A+", "crime": 8,
        "last_sales": [
            {"addr": "12000 SW 63rd Ave", "price": 1450000, "date": "2024-10", "sqft": 3200, "type": "SFR"},
        ],
        "vacant_lots": [],
        "highlights": ["A+ rated schools", "Large estate lots", "Lowest crime", "Pinecrest Gardens"],
        "risks": ["Purely residential - no commercial", "Ultra-premium entry", "Car-dependent"],
    },
    "Miami Springs": {
        "zip": "33166", "lat": 25.8222, "lon": -80.2892,
        "tagline": "Historic charm adjacent to MIA with stable values",
        "desc": "Small city adjacent to Miami International Airport with charming historic homes, golf course, and stable residential neighborhoods.",
        "mkt": {"med_price": 550000, "psf": 310, "rent": 2500, "yield": 5.5, "yoy": 5.0, "dom": 28, "inv_mo": 2.8, "ls_ratio": 97.0, "range": "$350K-$900K", "lot": 7500, "type": "Single Family / Townhouse", "units_pipeline": 100, "absorption": 88},
        "demo": {"pop": 14000, "income": 55000, "age": 42, "owner": 60, "renter": 40, "vacancy": 4.5, "college": 35, "foreign": 58},
        "scores": {"walk": 55, "transit": 35, "bike": 48},
        "zoning": {"primary": "RS / C-1 (City Code)", "max_far": 1.0, "max_height": "45 ft", "min_lot": "7,500 sqft", "parking": "2/unit", "setbacks": "25ft front / 10ft side", "allowed_uses": "Residential, Limited Retail, Office, Restaurant"},
        "oz": False, "flood": "X", "school": "B+", "crime": 22,
        "last_sales": [
            {"addr": "345 Oriole Ave", "price": 525000, "date": "2024-09", "sqft": 1650, "type": "SFR"},
        ],
        "vacant_lots": [],
        "highlights": ["Historic charm", "MIA proximity", "Golf course community", "Low flood risk"],
        "risks": ["Airport noise", "Small inventory", "Limited upside"],
    },
    "Homestead": {
        "zip": "33030", "lat": 25.4687, "lon": -80.4776,
        "tagline": "South Miami-Dade's affordable frontier with growth potential",
        "desc": "Southernmost urban area in Miami-Dade. Gateway to the Florida Keys and Everglades. Fastest growing area with most affordable housing.",
        "mkt": {"med_price": 380000, "psf": 220, "rent": 2000, "yield": 6.5, "yoy": 7.0, "dom": 22, "inv_mo": 2.0, "ls_ratio": 98.0, "range": "$250K-$550K", "lot": 6000, "type": "Single Family / Townhouse", "units_pipeline": 2000, "absorption": 92},
        "demo": {"pop": 82000, "income": 38000, "age": 34, "owner": 45, "renter": 55, "vacancy": 5.0, "college": 18, "foreign": 60},
        "scores": {"walk": 42, "transit": 15, "bike": 35},
        "zoning": {"primary": "GU / BU-1 (County)", "max_far": 1.0, "max_height": "45 ft", "min_lot": "5,000 sqft", "parking": "2/unit", "setbacks": "25ft front / 7.5ft side", "allowed_uses": "Residential, Retail, Office, Agriculture"},
        "oz": True, "flood": "AE / X", "school": "C+", "crime": 40,
        "last_sales": [
            {"addr": "1250 NE 8th St", "price": 365000, "date": "2024-10", "sqft": 1500, "type": "SFR"},
        ],
        "vacant_lots": [
            {"addr": "SW 344th St (Vacant)", "lot_sf": 10000, "zoning": "GU", "price": 180000, "potential_units": 2, "far": 1.0},
        ],
        "highlights": ["Most affordable in Miami-Dade", "Fastest population growth", "Keys/Everglades gateway", "OZ eligible"],
        "risks": ["Remote location", "Hurricane exposure", "Limited employment base", "No transit"],
    },
    "Dadeland": {
        "zip": "33156", "lat": 25.6900, "lon": -80.3140,
        "tagline": "Miami's premier suburban commercial and retail hub",
        "desc": "Major commercial node anchored by Dadeland Mall. Dense office and medical corridor with Metrorail connectivity. Strong retail foot traffic.",
        "mkt": {"med_price": 480000, "psf": 350, "rent": 2800, "yield": 5.2, "yoy": 4.5, "dom": 38, "inv_mo": 4.0, "ls_ratio": 95.5, "range": "$300K-$1.2M", "lot": 0, "type": "Office / Retail / Condo", "units_pipeline": 600, "absorption": 72},
        "demo": {"pop": 25000, "income": 65000, "age": 40, "owner": 40, "renter": 60, "vacancy": 6.0, "college": 52, "foreign": 48},
        "scores": {"walk": 75, "transit": 65, "bike": 48},
        "zoning": {"primary": "BU-3 / OPD (County)", "max_far": 3.5, "max_height": "200 ft (varies)", "min_lot": "10,000 sqft", "parking": "3.5/1,000 RSF", "setbacks": "Varies", "allowed_uses": "Office, Retail, Restaurant, Medical, Hotel, Residential, Mixed-Use"},
        "oz": False, "flood": "X", "school": "A", "crime": 18,
        "last_sales": [
            {"addr": "9155 S Dadeland Blvd #1805", "price": 520000, "date": "2024-10", "sqft": 1200, "type": "Condo"},
        ],
        "vacant_lots": [],
        "highlights": ["Dadeland Mall anchor", "Metrorail Dadeland stations", "Strong office tenant base", "Baptist Health nearby"],
        "risks": ["Traffic congestion", "Aging office inventory", "Premium retail rents"],
    },
    "Surfside": {
        "zip": "33154", "lat": 25.8785, "lon": -80.1255,
        "tagline": "Quiet beachfront village between Miami Beach and Bal Harbour",
        "desc": "Small oceanfront town known for its quiet residential character, family-friendly atmosphere, and proximity to Bal Harbour Shops.",
        "mkt": {"med_price": 850000, "psf": 620, "rent": 3800, "yield": 3.8, "yoy": 3.5, "dom": 55, "inv_mo": 5.5, "ls_ratio": 93.0, "range": "$400K-$5M+", "lot": 0, "type": "Condo / SFR", "units_pipeline": 200, "absorption": 55},
        "demo": {"pop": 5700, "income": 72000, "age": 45, "owner": 48, "renter": 52, "vacancy": 10.0, "college": 55, "foreign": 52},
        "scores": {"walk": 82, "transit": 38, "bike": 72},
        "zoning": {"primary": "RS / TS-2 (Town Code)", "max_far": 2.0, "max_height": "100 ft (varies)", "min_lot": "5,000 sqft", "parking": "1.5/unit", "setbacks": "Varies", "allowed_uses": "Residential, Limited Retail, Restaurant, Hotel"},
        "oz": False, "flood": "AE / VE (coastal)", "school": "A", "crime": 12,
        "last_sales": [
            {"addr": "9001 Collins Ave #S-805", "price": 1250000, "date": "2024-10", "sqft": 1800, "type": "Condo"},
        ],
        "vacant_lots": [],
        "highlights": ["Quiet oceanfront", "Bal Harbour Shops proximity", "Low crime", "Top schools"],
        "risks": ["Champlain Towers legacy concerns", "Coastal exposure", "Small market"],
    },
    "Sweetwater": {
        "zip": "33174", "lat": 25.7630, "lon": -80.3730,
        "tagline": "FIU-adjacent affordable corridor with student demand",
        "desc": "Small city adjacent to FIU main campus. Strong student rental market and affordable residential options. Growing commercial presence.",
        "mkt": {"med_price": 380000, "psf": 250, "rent": 2000, "yield": 6.2, "yoy": 6.0, "dom": 25, "inv_mo": 2.5, "ls_ratio": 97.5, "range": "$250K-$600K", "lot": 5500, "type": "SFR / Condo / Student Housing", "units_pipeline": 400, "absorption": 88},
        "demo": {"pop": 22000, "income": 32000, "age": 32, "owner": 35, "renter": 65, "vacancy": 5.5, "college": 28, "foreign": 65},
        "scores": {"walk": 55, "transit": 30, "bike": 42},
        "zoning": {"primary": "C-1 / R-3 (City Code)", "max_far": 1.5, "max_height": "55 ft", "min_lot": "5,000 sqft", "parking": "1.5/unit", "setbacks": "20ft front / 5ft side", "allowed_uses": "Residential, Retail, Office, Student Housing, Restaurant"},
        "oz": False, "flood": "X", "school": "B-", "crime": 32,
        "last_sales": [
            {"addr": "10600 SW 8th St", "price": 365000, "date": "2024-09", "sqft": 1300, "type": "Condo"},
        ],
        "vacant_lots": [],
        "highlights": ["FIU campus adjacency", "Affordable entry", "Student demand", "Low flood risk"],
        "risks": ["Low income area", "Limited amenities", "Car-dependent"],
    },
}

_NB_KEYWORDS = {
    "Coral Gables": ["CORAL GABLES", "PONCE DE LEON", "ALHAMBRA", "MIRACLE MILE", "DOUGLAS RD", "33134", "33146", "GALIANO"],
    "Coconut Grove": ["COCONUT GROVE", "COCOWALK", "MAIN HWY", "33133"],
    "Brickell": ["BRICKELL", "33131", "S MIAMI AVE"],
    "Wynwood": ["WYNWOOD", "33127", "NW 2ND AVE"],
    "Little Havana": ["LITTLE HAVANA", "CALLE OCHO", "33135", "SW 8TH ST"],
    "Overtown": ["OVERTOWN", "33136"],
    "Edgewater": ["EDGEWATER", "NE 31ST", "NE 32ND", "BISCAYNE BLVD 3"],
    "Allapattah": ["ALLAPATTAH", "33142", "NW 20TH ST", "NW 36TH ST"],
    "Westchester": ["WESTCHESTER", "33165", "SW 8TH ST 9", "BIRD RD 9"],
    "Doral": ["DORAL", "33122", "33178", "NW 33RD ST", "NW 41ST ST", "NW 36TH ST 8", "NW 87TH", "NW 107TH"],
    "Airport West": ["WATERFORD", "BLUE LAGOON", "33126", "NW 25TH ST 7", "LE JEUNE"],
    "Downtown Miami": ["DOWNTOWN", "FLAGLER", "BISCAYNE BLVD 1", "BISCAYNE BLVD 2", "33132", "NE 1ST AVE", "NW 1ST AVE"],
    "Design District": ["DESIGN DISTRICT", "NE 40TH ST", "NE 41ST ST", "NE 2ND AVE 38", "NE 2ND AVE 39", "NE 2ND AVE 40"],
    "Midtown": ["MIDTOWN", "NE 34TH ST", "NE 36TH ST"],
    "Miami Beach": ["MIAMI BEACH", "SOUTH BEACH", "COLLINS AVE", "OCEAN DR", "WASHINGTON AVE", "33139", "33140", "33141"],
    "Aventura": ["AVENTURA", "33180", "COUNTRY CLUB DR"],
    "Kendall": ["KENDALL", "33176", "33183", "33186", "SW 88TH ST", "SW 104TH ST", "SW 117TH AVE"],
    "Hialeah": ["HIALEAH", "33012", "33010", "33013", "33014", "33015", "W 49TH ST", "PALM AVE"],
    "North Miami": ["NORTH MIAMI", "33161", "33162", "33168", "NE 125TH ST", "NE 6TH AVE 1"],
    "Sunny Isles Beach": ["SUNNY ISLES", "33160", "COLLINS AVE 17", "COLLINS AVE 18", "COLLINS AVE 19"],
    "Key Biscayne": ["KEY BISCAYNE", "33149", "CRANDON", "RICKENBACKER"],
    "South Miami": ["SOUTH MIAMI", "33143", "SUNSET DR", "SW 57TH AVE"],
    "Pinecrest": ["PINECREST", "33156", "SW 67TH AVE 1"],
    "Miami Springs": ["MIAMI SPRINGS", "33166", "CURTISS PKWY"],
    "Homestead": ["HOMESTEAD", "33030", "33033", "33034", "FLORIDA CITY"],
    "Dadeland": ["DADELAND", "S DADELAND BLVD"],
    "Surfside": ["SURFSIDE", "33154", "COLLINS AVE 9"],
    "Sweetwater": ["SWEETWATER", "33174", "SW 109TH AVE", "FIU"],
}

def match_neighborhood(addr, geo=None):
    addr_up = addr.upper() if addr else ""
    # Check keyword hints first (more specific matches)
    for name, keywords in _NB_KEYWORDS.items():
        for kw in keywords:
            if kw in addr_up:
                return name, NB[name]
    # Fallback: name match
    for name, d in NB.items():
        kw = name.upper().replace(" ", "")
        if kw in addr_up.replace(" ", ""):
            return name, d
    if geo and geo.get("lat"):
        lat, lon = geo["lat"], geo["lon"]
        best, best_d = None, 999
        for name, d in NB.items():
            dist = abs(lat - d["lat"]) + abs(lon - d["lon"])
            if dist < best_d:
                best_d = dist
                best = name
        if best and best_d < 0.12:
            return best, NB[best]
    return None, None

def lookup_parcel(addr):
    try:
        from parcels_data import ADDR_DATA
    except ImportError:
        return None
    clean = addr.upper().split(",")[0].strip()
    if clean in ADDR_DATA:
        return ADDR_DATA[clean]
    for k, v in ADDR_DATA.items():
        if clean in k or k in clean:
            return v
    return None

def lookup_buildings(submarket=None):
    try:
        from buildings_data import BUILDINGS
    except ImportError:
        return []
    if submarket:
        return [b for b in BUILDINGS if b.get("submarket", "").lower() == submarket.lower()]
    return BUILDINGS

@st.cache_data(ttl=86400, show_spinner=False)
def get_submarket_addresses():
    addresses = {}
    for name, d in NB.items():
        addrs = []
        for s in d.get("last_sales", []):
            a = s.get("addr", "")
            if a and "Vacant" not in a:
                addrs.append(a + ", Miami, FL")
        for lot in d.get("vacant_lots", []):
            a = lot.get("addr", "")
            if a and "Vacant" not in a:
                addrs.append(a + ", Miami, FL")
        addresses[name] = addrs

    try:
        from buildings_data import BUILDINGS
        sub_map = {
            "Coral Gables": "Coral Gables",
            "Coral Way Corridor": "Brickell",
            "West Miami": "Westchester",
        }
        for b in BUILDINGS:
            sub = b.get("submarket", "")
            addr = b.get("address", "")
            if not addr:
                continue
            target = sub_map.get(sub, sub)
            if target not in addresses:
                addresses[target] = []
            addresses[target].append(addr)
    except ImportError:
        pass

    try:
        from parcels_data import ADDR_DATA
        for key, v in ADDR_DATA.items():
            addr = v.get("Address", "")
            city = v.get("City", "Miami")
            state = v.get("State", "FL")
            if not addr:
                continue
            full = "{}, {}, {}".format(addr, city, state)
            lat = float(v.get("Latitude", 0) or 0)
            lon = float(v.get("Longitude", 0) or 0)
            best_nb = None
            best_dist = 999
            for name, d in NB.items():
                dist = abs(lat - d["lat"]) + abs(lon - d["lon"])
                if dist < best_dist:
                    best_dist = dist
                    best_nb = name
            if best_nb and best_dist < 0.06:
                if best_nb not in addresses:
                    addresses[best_nb] = []
                addresses[best_nb].append(full)
    except ImportError:
        pass

    for k in addresses:
        seen = set()
        unique = []
        for a in addresses[k]:
            norm = a.upper().split(",")[0].strip()
            if norm not in seen:
                seen.add(norm)
                unique.append(a)
        addresses[k] = unique

    return addresses

def random_address(submarket):
    import random
    addrs = get_submarket_addresses()
    pool = addrs.get(submarket, [])
    if not pool:
        return None
    return random.choice(pool)

ALL_SUBMARKETS = list(NB.keys())

def format_currency(v):
    if v is None:
        return "N/A"
    try:
        v = float(str(v).replace(",", ""))
    except (ValueError, TypeError):
        return "N/A"
    if v >= 1_000_000:
        return "${:,.1f}M".format(v / 1_000_000)
    if v >= 1000:
        return "${:,.0f}".format(v)
    return "${:.0f}".format(v)

def format_number(v):
    if v is None:
        return "N/A"
    try:
        v = float(str(v).replace(",", ""))
    except (ValueError, TypeError):
        return "N/A"
    return "{:,.0f}".format(v)
