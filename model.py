import pandas as pd
import random
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─────────────────────────────────────────
# API KEYS
# ─────────────────────────────────────────
RAPIDAPI_KEY  = "0b37ca8586msha2ee99c09d025d9p16cb27jsn0f8a9e417d5f"

# ASOS API
ASOS_HOST     = "asos10.p.rapidapi.com"
ASOS_BASE_URL = "https://asos10.p.rapidapi.com"
RAPIDAPI_HEADERS = {
    "x-rapidapi-key":  RAPIDAPI_KEY,
    "x-rapidapi-host": ASOS_HOST,
    "Content-Type":    "application/json"
}

# Real-Time Product Search API
REALTIME_HOST     = "real-time-product-search.p.rapidapi.com"
REALTIME_BASE_URL = "https://real-time-product-search.p.rapidapi.com"
REALTIME_HEADERS  = {
    "x-rapidapi-key":  RAPIDAPI_KEY,
    "x-rapidapi-host": REALTIME_HOST,
    "Content-Type":    "application/json"
}

# ─────────────────────────────────────────
# RETAILER SHOP LINKS
# ─────────────────────────────────────────
RETAILER_LINKS = {
    'H&M':              'https://www.hm.com/en_us/search-results.html?q=',
    'Zara':             'https://www.zara.com/us/en/search?searchTerm=',
    'ASOS':             'https://www.asos.com/search/?q=',
    'Puma':             'https://us.puma.com/us/en/search?q=',
    'Nike':             'https://www.nike.com/search?q=',
    'Adidas':           'https://www.adidas.com/us/search?q=',
    'Levis':            'https://www.levi.com/US/en_US/search?keywords=',
    'Shein':            'https://www.shein.com/search?q=',
    'Urban Outfitters': 'https://www.urbanoutfitters.com/search?search=',
    'Nordstrom':        'https://www.nordstrom.com/sr?keyword=',
    'FitPic Pick':      'https://www.asos.com/search/?q=',
}

def get_shop_link(brand, product_name):
    base = RETAILER_LINKS.get(brand, 'https://www.asos.com/search/?q=')
    return base + product_name.replace(' ', '+')

# ─────────────────────────────────────────
# LOAD LOCAL CSV DATA (fallback)
# ─────────────────────────────────────────
def load_data():
    possible_paths = [
        'styles.csv',
        'Data/styles.csv',
        os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs/FitPic/Data/styles.csv'),
        os.path.expanduser('~/Documents/FitPic/Data/styles.csv'),
        os.path.expanduser('~/Desktop/FitPic/Data/styles.csv'),
    ]
    csv_path = None
    for path in possible_paths:
        if os.path.isfile(path):
            csv_path = path
            break
    if csv_path is None:
        raise FileNotFoundError("Could not find styles.csv")
    df = pd.read_csv(csv_path, on_bad_lines='skip')
    df = df.dropna(subset=['usage', 'subCategory', 'articleType', 'baseColour'])
    return df

# ─────────────────────────────────────────
# STYLE MAPS
# ─────────────────────────────────────────
STYLE_MAP = {
    'casual':          ['Casual'],
    'streetwear':      ['Casual'],
    'business_casual': ['Smart Casual', 'Formal'],
    'formal':          ['Formal'],
    'athleisure':      ['Sports'],
    'bohemian':        ['Casual'],
    'minimalist':      ['Casual', 'Smart Casual'],
}

ASOS_STYLE_QUERIES = {
    'casual':          'casual outfit',
    'streetwear':      'streetwear urban',
    'business_casual': 'smart casual office',
    'formal':          'formal dress suit',
    'athleisure':      'sportswear athleisure',
    'bohemian':        'boho flowy',
    'minimalist':      'minimal clean basics',
}

# Per-category search terms for each style
OUTFIT_SLOT_QUERIES = {
    'casual':          {'top': 'casual t-shirt',      'bottom': 'casual jeans',          'shoes': 'casual sneakers',       'accessory': 'casual cap'},
    'streetwear':      {'top': 'streetwear hoodie',   'bottom': 'streetwear cargo pants', 'shoes': 'streetwear sneakers',   'accessory': 'streetwear chain'},
    'business_casual': {'top': 'dress shirt',          'bottom': 'chino trousers',         'shoes': 'loafers dress shoes',   'accessory': 'leather belt'},
    'formal':          {'top': 'formal blazer shirt',  'bottom': 'formal trousers',        'shoes': 'formal oxford shoes',   'accessory': 'tie'},
    'athleisure':      {'top': 'athletic t-shirt',     'bottom': 'jogger sweatpants',      'shoes': 'running sneakers',      'accessory': 'gym bag'},
    'bohemian':        {'top': 'boho flowy blouse',    'bottom': 'flowy wide leg pants',   'shoes': 'sandals',               'accessory': 'layered necklace'},
    'minimalist':      {'top': 'minimalist clean tee', 'bottom': 'slim straight pants',    'shoes': 'white clean sneakers',  'accessory': 'simple watch'},
}

SKIN_TONE_COLORS = {
    'fair':        ['Navy Blue', 'Black', 'White', 'Purple', 'Blue'],
    'light':       ['Pink', 'Blue', 'Lavender', 'Beige', 'Olive'],
    'medium':      ['Orange', 'Yellow', 'Green', 'Teal', 'Brown'],
    'medium_warm': ['Brown', 'Beige', 'Olive', 'Orange'],
    'tan':         ['White', 'Coral', 'Gold', 'Red'],
    'deep':        ['White', 'Blue', 'Green', 'Yellow', 'Red'],
}

OCCASION_MAP = {
    '1': 'everyday', '2': 'work',   '3': 'night_out',
    '4': 'date',     '5': 'campus', '6': 'workout', '7': 'travel',
}

GENDER_MAP = {'1': 'Women', '2': 'Men', '3': None}

STYLE_MAP_MENU = {
    '1': ('casual',          ['Casual']),
    '2': ('streetwear',      ['Casual']),
    '3': ('business_casual', ['Smart Casual', 'Formal']),
    '4': ('formal',          ['Formal']),
    '5': ('athleisure',      ['Sports']),
    '6': ('bohemian',        ['Casual']),
    '7': ('minimalist',      ['Casual', 'Smart Casual']),
}

SKIN_MAP_MENU = {
    '1': ('fair',        ['Navy Blue', 'Black', 'White', 'Purple', 'Blue']),
    '2': ('light',       ['Pink', 'Blue', 'Lavender', 'Beige', 'Olive']),
    '3': ('medium',      ['Orange', 'Yellow', 'Green', 'Teal', 'Brown']),
    '4': ('medium_warm', ['Brown', 'Beige', 'Olive', 'Orange']),
    '5': ('tan',         ['White', 'Coral', 'Gold', 'Red']),
    '6': ('deep',        ['White', 'Blue', 'Green', 'Yellow', 'Red']),
}

# ─────────────────────────────────────────
# ASOS API 
# ─────────────────────────────────────────
def search_asos(query, gender=None, limit=20):
    """
    Search ASOS using the correct api.
    Returns list of product dicts or empty list on failure.
    """
    try:
        # women = store 1, men = store 2
        store = '2' if gender == 'Men' else '1'

        params = {
            "currency":      "USD",
            "country":       "US",
            "store":         store,
            "languageShort": "en",
            "sizeSchema":    "US",
            "limit":         str(limit),
            "offset":        "0",
            "sort":          "recommended",
            "q":             query,
        }

        response = requests.get(
            f"{ASOS_BASE_URL}/api/v1/getProductList",
            headers=RAPIDAPI_HEADERS,
            params=params,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            # Try  possible key the API might use
            products = (
                data.get('products') or
                data.get('items') or
                data.get('productResults') or
                data.get('data', {}).get('products') or
                []
            )

            print(f"  ✅ ASOS API returned {len(products)} products for '{query}'")

            if not products:
                print(f"  ℹ️  Top-level keys in response: {list(data.keys())}")
                # Print first 300 chars 
                import json
                print(f"  ℹ️  Raw sample: {json.dumps(data)[:300]}")

            return products

        else:
            print(f"  ⚠️  ASOS API status {response.status_code}")
            print(f"  ℹ️  Response: {response.text[:300]}")
            return []

    except Exception as e:
        print(f"  ⚠️  ASOS API error: {e}")
        return []

# ─────────────────────────────────────────
# PARSE ASOS RESPONSE INTO FITPIC FORMAT
# ─────────────────────────────────────────
def parse_asos_products(products, style, occasion, good_colors=None):
    results = []
    for p in products[:10]:
        # Handle different name fields
        name = (
            p.get('name') or
            p.get('title') or
            p.get('productName') or
            'ASOS Item'
        )

        # Handle different price structures
        price_val = 0
        price = p.get('price', {})
        if isinstance(price, dict):
            price_val = (
                price.get('current', {}).get('value') or
                price.get('value') or
                price.get('amount') or
                0
            )
        elif isinstance(price, (int, float)):
            price_val = price

        # Handle color
        color = p.get('colour') or p.get('color') or p.get('baseColour') or 'N/A'

        # Handle image
        image_url = ''
        images = p.get('imageUrl') or p.get('images') or p.get('image') or []
        if isinstance(images, list) and images:
            image_url = images[0].get('url', '') if isinstance(images[0], dict) else str(images[0])
        elif isinstance(images, str):
            image_url = images

        # Handle product URL
        product_url = p.get('url') or p.get('productUrl') or p.get('link') or ''
        if product_url and not product_url.startswith('http'):
            product_url = 'https://www.asos.com' + product_url

        # Score based on color match
        score = 75
        if good_colors and color != 'N/A':
            if any(c.lower() in color.lower() for c in good_colors):
                score += 15
        score += random.randint(0, 9)
        score = min(score, 99)

        # Handle category
        cat = p.get('category', {})
        category = cat.get('name', 'Clothing') if isinstance(cat, dict) else str(cat or 'Clothing')

        pt = p.get('productType', {})
        article_type = pt.get('name', 'Item') if isinstance(pt, dict) else str(pt or 'Item')

        results.append({
            'id':           str(p.get('id', '')),
            'name':         name,
            'brand':        'ASOS',
            'color':        color,
            'category':     category,
            'article_type': article_type,
            'gender':       p.get('gender', 'N/A'),
            'season':       'All Season',
            'usage':        style,
            'match_score':  score,
            'style':        style,
            'price':        round(float(price_val), 2) if price_val else round(random.uniform(25, 120), 2),
            'image_url':    image_url,
            'shop_url':     product_url or f"https://www.asos.com/search/?q={name.replace(' ','+')}",
            'retailer':     'ASOS',
        })

    return results

# ─────────────────────────────────────────
# SCORE CSV ITEM
# ─────────────────────────────────────────
def score_item(item, good_colors=None, gender=None):
    score = 60
    if good_colors:
        item_color = str(item.get('baseColour', ''))
        if any(c.lower() in item_color.lower() for c in good_colors):
            score += 20
    if gender:
        item_gender = str(item.get('gender', '')).lower()
        if item_gender == gender.lower() or item_gender == 'unisex':
            score += 10
    score += random.randint(0, 9)
    return min(score, 99)

# ─────────────────────────────────────────
# REAL-TIME PRODUCT SEARCH API
# ─────────────────────────────────────────
def search_realtime_products(query, gender=None, limit=10):
    """
    Search using the Real-Time Product Search API.
    Returns list of product dicts or empty list on failure.
    """
    try:
        # Prepend gender so results are gender-specific
        if gender:
            query = f"{gender.lower()} {query}"

        params = {
            "q":                 query,
            "country":           "us",
            "language":          "en",
            "page":              "1",
            "limit":             str(limit),
            "sort_by":           "BEST_MATCH",
            "product_condition": "ANY",
            "return_filters":    "true",
        }

        response = requests.get(
            f"{REALTIME_BASE_URL}/search-v2",
            headers=REALTIME_HEADERS,
            params=params,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            products = (
                data.get('data', {}).get('products') or
                data.get('products') or
                data.get('items') or
                []
            )
            print(f"  ✅ Real-Time Search returned {len(products)} products for '{query}'")
            return products
        else:
            print(f"  ⚠️  Real-Time Search status {response.status_code}")
            return []

    except Exception as e:
        print(f"  ⚠️  Real-Time Search error: {e}")
        return []


def parse_realtime_products(products, style, good_colors=None):
    """Parse Real-Time Product Search results into FitPic format."""
    results = []
    for p in products[:10]:
        name = p.get('product_title') or p.get('title') or p.get('name') or 'Item'

        # Price — prefer offer.price, fall back to typical_price_range
        offer     = p.get('offer') or {}
        price_val = 0
        for price_src in [offer.get('price'), offer.get('original_price'),
                          (p.get('typical_price_range') or [None])[0]]:
            if price_src:
                try:
                    price_val = float(str(price_src).replace('$', '').replace(',', '').strip())
                    break
                except Exception:
                    continue

        # Image
        photos    = p.get('product_photos') or []
        image_url = photos[0] if photos else ''

        # URL — prefer offer page, fall back to product page
        product_url = offer.get('offer_page_url') or p.get('product_page_url') or ''

        # Brand / store
        brand = offer.get('store_name') or p.get('brand') or 'FitPic Pick'

        # Color
        color = p.get('color') or 'N/A'

        # Score
        score = 78
        if good_colors and color != 'N/A':
            if any(c.lower() in color.lower() for c in good_colors):
                score += 12
        score += random.randint(0, 9)
        score = min(score, 99)

        results.append({
            'id':           str(p.get('product_id', '')),
            'name':         name,
            'brand':        brand,
            'color':        color,
            'category':     'Clothing',
            'article_type': 'Item',
            'gender':       'N/A',
            'season':       'All Season',
            'usage':        style,
            'match_score':  score,
            'style':        style,
            'price':        round(price_val, 2) if price_val else round(random.uniform(25, 120), 2),
            'image_url':    image_url,
            'shop_url':     product_url or f"https://www.google.com/shopping/search?q={name.replace(' ','+')}",
            'retailer':     'Real-Time Search',
        })

    return results


# ─────────────────────────────────────────
# CSV FALLBACK
# ─────────────────────────────────────────
def get_csv_recommendations(style='casual', usage_tags=None,
                             good_colors=None, gender=None, top_n=5):
    df = load_data()
    if usage_tags is None:
        usage_tags = ['Casual']

    filtered = df[df['usage'].isin(usage_tags)]

    if gender:
        filtered = filtered[
            (filtered['gender'].str.lower() == gender.lower()) |
            (filtered['gender'].str.lower() == 'unisex')
        ]

    wearable = ['Topwear', 'Bottomwear', 'Shoes', 'Dress', 'Apparel Set']
    filtered = filtered[filtered['subCategory'].isin(wearable)]

    if len(filtered) == 0:
        filtered = df[df['usage'] == 'Casual'].head(200)

    filtered = filtered.copy()
    filtered['match_score'] = filtered.apply(
        lambda row: score_item(row, good_colors, gender), axis=1
    )

    tops    = filtered[filtered['subCategory'] == 'Topwear'].nlargest(2, 'match_score')
    bottoms = filtered[filtered['subCategory'] == 'Bottomwear'].nlargest(2, 'match_score')
    shoes   = filtered[filtered['subCategory'] == 'Shoes'].nlargest(1, 'match_score')
    top_5   = pd.concat([tops, bottoms, shoes]).head(top_n)

    results = []
    for _, item in top_5.iterrows():
        name  = str(item.get('productDisplayName', 'Unknown'))
        brand = name.split()[0] if name != 'Unknown' else 'FitPic Pick'
        results.append({
            'id':           str(item.get('id', '')),
            'name':         name,
            'brand':        brand,
            'color':        str(item.get('baseColour', 'N/A')),
            'category':     str(item.get('subCategory', 'N/A')),
            'article_type': str(item.get('articleType', 'N/A')),
            'gender':       str(item.get('gender', 'N/A')),
            'season':       str(item.get('season', 'N/A')),
            'usage':        str(item.get('usage', 'N/A')),
            'match_score':  int(item.get('match_score', 75)),
            'style':        style,
            'price':        round(random.uniform(25, 120), 2),
            'image_url':    '',
            'shop_url':     get_shop_link(brand, name),
            'retailer':     'styles.csv',
        })
    return results

# ─────────────────────────────────────────
# URL VERIFICATION
# ─────────────────────────────────────────
def is_url_alive(url, timeout=5):
    """Return True if the URL responds with a non-404/410 status."""
    if not url or not url.startswith('http'):
        return False
    try:
        # Try HEAD first (faster, no body download)
        r = requests.head(url, timeout=timeout, allow_redirects=True,
                          headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code in (404, 410, 400):
            return False
        if r.status_code < 400:
            return True
        # Some servers reject HEAD — fall back to GET with stream
        r = requests.get(url, timeout=timeout, allow_redirects=True, stream=True,
                         headers={'User-Agent': 'Mozilla/5.0'})
        return r.status_code < 400
    except Exception:
        return False


def filter_live_links(items, max_workers=8):
    """
    Check every item's shop_url concurrently.
    Returns items whose links are alive. Falls back to all items
    if none pass (e.g. network blocked) so we never return empty.
    """
    if not items:
        return items

    print(f"  🔗 Verifying {len(items)} product links...")

    alive = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_idx = {
            pool.submit(is_url_alive, item['shop_url']): i
            for i, item in enumerate(items)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            alive[idx] = future.result()

    valid = [items[i] for i in range(len(items)) if alive.get(i, False)]
    dead  = len(items) - len(valid)

    if dead:
        print(f"  ⚠️  Removed {dead} dead link(s)")

    # If everything failed (network issue / all blocked), return originals
    return valid if valid else items


# ─────────────────────────────────────────
# MAIN RECOMMENDATION FUNCTION
# Tries ASOS API first, falls back to CSV
# ─────────────────────────────────────────
def get_recommendations(style='casual', occasion=None,
                         skin_tone=None, gender=None,
                         usage_tags=None, good_colors=None, top_n=5):

    if good_colors is None and skin_tone:
        good_colors = SKIN_TONE_COLORS.get(skin_tone, [])

    if usage_tags is None:
        usage_tags = STYLE_MAP.get(style, ['Casual'])

    query = ASOS_STYLE_QUERIES.get(style, style)

    # Step 1: Try Real-Time Product Search API — one query per outfit slot
    print(f"\n  🔍 Searching Real-Time Products for '{style}' outfit pieces...")
    slots = OUTFIT_SLOT_QUERIES.get(style, OUTFIT_SLOT_QUERIES['casual'])
    slot_labels = {
        'top':       'Topwear',
        'bottom':    'Bottomwear',
        'shoes':     'Shoes',
        'accessory': 'Accessories',
    }
    outfit_pieces = []
    for slot, slot_query in slots.items():
        products = search_realtime_products(slot_query, gender=gender, limit=8)
        if not products:
            continue
        parsed = parse_realtime_products(products, style, good_colors)
        # Try each candidate until one has a live URL
        picked = None
        for candidate in parsed:
            candidate['category']     = slot_labels[slot]
            candidate['article_type'] = slot.capitalize()
            if is_url_alive(candidate['shop_url']):
                picked = candidate
                break
        if picked:
            outfit_pieces.append(picked)
            print(f"  ✅ [{slot_labels[slot]}] {picked['name'][:45]}")
        else:
            print(f"  ⚠️  No live URL found for slot: {slot}")

    if len(outfit_pieces) >= 3:
        print(f"  ✅ Using Real-Time Search results ({len(outfit_pieces)} pieces)")
        return outfit_pieces[:top_n]

    # Step 2: Try ASOS API
    print(f"  🔍 Trying ASOS for '{query}'...")
    products = search_asos(query, gender=gender, limit=20)
    if products:
        results = parse_asos_products(products, style, occasion, good_colors)
        results = filter_live_links(results)
        if len(results) >= 3:
            print(f"  ✅ Using ASOS API results")
            return results[:top_n]

    # Step 3: Fall back to local CSV
    print("  📁 Falling back to local styles.csv dataset...")
    return get_csv_recommendations(
        style=style,
        usage_tags=usage_tags,
        good_colors=good_colors,
        gender=gender,
        top_n=top_n
    )

# CLI HELPERS
def ask(question, options):
    print(f"\n{question}")
    for key, label in options.items():
        print(f"  {key}. {label}")
    while True:
        choice = input("\nEnter number: ").strip()
        if choice in options:
            return choice
        print(f"  Please enter a number between 1 and {len(options)}")

def print_results(results, style, occasion):
    print("\n" + "="*60)
    print(f"  YOUR TOP 5 FITPIC RECOMMENDATIONS")
    print(f"  Style: {style.upper()} | Occasion: {occasion.upper()}")
    print("="*60)

    icons = {
        'Topwear': '👕', 'Bottomwear': '👖', 'Shoes': '👟',
        'Dress': '👗', 'Clothing': '👔', 'Apparel Set': '🧥',
    }

    for i, item in enumerate(results, 1):
        icon      = icons.get(item['category'], '🛍️')
        price_str = f"${item['price']:.2f}" if item.get('price') else 'N/A'
        source    = '🛒 ASOS' if item.get('retailer') == 'ASOS' else '📁 Local Data'
        print(f"\n  {i}. {icon} [{item['match_score']}% Match] {source}")
        print(f"     {item['name']}")
        print(f"     Color: {item['color']} | Type: {item['article_type']} | Price: {price_str}")
        if item.get('shop_url'):
            print(f"     🔗 {item['shop_url'][:70]}")

    print("\n" + "="*60)


# INTERACTIVE CLI
def main():
    print("\n" + "="*60)
    print("  WELCOME TO FITPIC")
    print("  AI-Powered Outfit Recommendations")
    print("  Powered by ASOS API + 44,000 item dataset")
    print("="*60)

    name = input("\nWhat's your name? ").strip() or "Friend"
    print(f"\n  Hey {name}! Let's find your perfect outfit.")

    gender_choice = ask(
        "What would you like to shop for?",
        {'1': 'Women', '2': 'Men', '3': 'No preference'}
    )
    gender = GENDER_MAP[gender_choice]

    style_choice = ask(
        "What style are you going for?",
        {
            '1': 'Casual — Relaxed everyday looks',
            '2': 'Streetwear — Bold, urban, trendy',
            '3': 'Business Casual — Smart but comfortable',
            '4': 'Formal — Polished and professional',
            '5': 'Athleisure — Sporty meets stylish',
            '6': 'Bohemian — Flowy, earthy, artistic',
            '7': 'Minimalist — Clean, simple, timeless',
        }
    )
    style_name, usage_tags = STYLE_MAP_MENU[style_choice]

    occasion_choice = ask(
        "What's the occasion?",
        {
            '1': 'Everyday / General',
            '2': 'Work / Office',
            '3': 'Night Out',
            '4': 'Date',
            '5': 'Campus / School',
            '6': 'Workout',
            '7': 'Travel',
        }
    )
    occasion = OCCASION_MAP[occasion_choice]

    skin_choice = ask(
        "What's your skin tone?",
        {
            '1': 'Fair',
            '2': 'Light',
            '3': 'Medium',
            '4': 'Medium Warm',
            '5': 'Tan',
            '6': 'Deep',
        }
    )
    skin_name, good_colors = SKIN_MAP_MENU[skin_choice]

    season_choice = ask(
        "What season are you dressing for?",
        {'1': 'Summer', '2': 'Winter', '3': 'Spring', '4': 'Fall', '5': 'No preference'}
    )
    season_labels = {'1': 'Summer', '2': 'Winter', '3': 'Spring', '4': 'Fall', '5': None}
    season = season_labels[season_choice]

    print(f"\n  Finding your top 5 {style_name} outfits for {name}...")

    results = get_recommendations(
        style=style_name,
        occasion=occasion,
        good_colors=good_colors,
        gender=gender,
        usage_tags=usage_tags,
        top_n=5
    )

    if season:
        season_filtered = [r for r in results if r.get('season') == season]
        if len(season_filtered) >= 3:
            results = season_filtered

    print_results(results, style_name, occasion)

    again = input("\n  Want to search again? (y/n): ").strip().lower()
    if again == 'y':
        main()
    else:
        print(f"\n  Thanks for using FitPic, {name}! 👗✨\n")

if __name__ == '__main__':
    main()
