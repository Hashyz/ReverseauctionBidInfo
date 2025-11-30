import js
from pyodide.ffi import create_proxy, to_js
from collections import Counter
from datetime import datetime
import asyncio

PRODUCTS_API = "/api/products"
BID_HISTORY_API = "/api/bid-history"

products_data = []

def format_price(price):
    """Format price with commas"""
    return f"{price:,} MMK"

def format_datetime(dt_string):
    """Format datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_string

def get_status_text(start_time, end_time):
    """Determine product status based on time"""
    now = datetime.now()
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00')).replace(tzinfo=None)
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00')).replace(tzinfo=None)
        
        if now < start:
            return ("upcoming", "Upcoming")
        elif now > end:
            return ("ended", "Ended")
        else:
            return ("active", "Active Now")
    except:
        return ("unknown", "Unknown")

async def js_fetch(url):
    """Fetch using JavaScript's native fetch API"""
    response = await js.window.fetch(url)
    data = await response.json()
    return data.to_py()

async def fetch_products():
    """Fetch products from API"""
    try:
        data = await js_fetch(PRODUCTS_API)
        return data.get("data", [])
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

async def fetch_bid_history(cp_id):
    """Fetch bid history for a product"""
    try:
        url = f"{BID_HISTORY_API}?cp_id={cp_id}&pageSize=100000&current=1&sort=desc"
        data = await js_fetch(url)
        return data.get("data", [])
    except Exception as e:
        print(f"Error fetching bid history: {e}")
        return []

def render_products(products):
    """Render products to the page"""
    global products_data
    products_data = products
    
    container = js.document.getElementById("products-container")
    container.innerHTML = ""
    
    if not products:
        container.innerHTML = "<p style='color: #8892b0; text-align: center;'>No products found</p>"
        return
    
    for product in products:
        status_class, status_text = get_status_text(
            product.get("start_time", ""),
            product.get("end_time", "")
        )
        
        images = product.get("product_image", "").split(",")
        first_image = images[0] if images else ""
        
        card = js.document.createElement("div")
        card.className = f"product-card {status_class}"
        card.setAttribute("data-cpid", str(product.get("cp_id", "")))
        
        card.innerHTML = f"""
            <div class="product-image">
                <img src="{first_image}" alt="{product.get('product_name', '')}" onerror="this.src='https://via.placeholder.com/200?text=No+Image'">
                <span class="status-badge {status_class}">{status_text}</span>
            </div>
            <div class="product-info">
                <h3 class="product-name">{product.get('product_name', 'Unknown')}</h3>
                <p class="product-code">Code: {product.get('product_code', 'N/A')}</p>
                <p class="product-price">{format_price(product.get('product_price', 0))}</p>
                <div class="product-times">
                    <p><strong>Start:</strong> {format_datetime(product.get('start_time', ''))}</p>
                    <p><strong>End:</strong> {format_datetime(product.get('end_time', ''))}</p>
                </div>
                <p class="bid-count">Bidders: {product.get('count_user', 0)}</p>
                <button class="view-bids-btn" onclick="window.showBidDetails({product.get('cp_id', 0)})">View Bid Details</button>
            </div>
        """
        
        container.appendChild(card)

def analyze_bids(bids):
    """Analyze bid data and return statistics"""
    if not bids:
        return {
            "total_bids": 0,
            "unique_bidders": 0,
            "top_bidders": []
        }
    
    phone_numbers = [bid.get("isdn", "Unknown") for bid in bids]
    counter = Counter(phone_numbers)
    
    top_bidders = counter.most_common(10)
    
    return {
        "total_bids": len(bids),
        "unique_bidders": len(counter),
        "top_bidders": top_bidders
    }

def render_bid_details(product, stats):
    """Render bid details section"""
    details_container = js.document.getElementById("bid-details")
    
    rows = ""
    for i, (number, count) in enumerate(stats["top_bidders"], 1):
        rows += f"""
            <tr>
                <td>{i}</td>
                <td>{number}</td>
                <td>{count}</td>
            </tr>
        """
    
    if not rows:
        rows = "<tr><td colspan='3' class='no-data'>No bid data available</td></tr>"
    
    details_container.innerHTML = f"""
        <div class="stats-summary">
            <div class="stat-card">
                <span class="stat-value">{stats['total_bids']:,}</span>
                <span class="stat-label">Total Bids</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{stats['unique_bidders']:,}</span>
                <span class="stat-label">Unique Bidders</span>
            </div>
        </div>
        
        <h3>Top 10 Bidders</h3>
        <table class="bid-table">
            <thead>
                <tr>
                    <th>No</th>
                    <th>Phone Number</th>
                    <th>Bid Count</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    """

async def show_bid_details(cp_id):
    """Show bid details for selected product"""
    global products_data
    
    product = None
    for p in products_data:
        if p.get("cp_id") == cp_id:
            product = p
            break
    
    if not product:
        return
    
    bid_section = js.document.getElementById("bid-section")
    bid_loading = js.document.getElementById("bid-loading")
    bid_details = js.document.getElementById("bid-details")
    product_name = js.document.getElementById("selected-product-name")
    
    product_name.textContent = product.get("product_name", "Bid Details")
    bid_section.style.display = "block"
    bid_loading.style.display = "flex"
    bid_details.innerHTML = ""
    
    bid_section.scrollIntoView(to_js({"behavior": "smooth"}))
    
    bids = await fetch_bid_history(cp_id)
    stats = analyze_bids(bids)
    
    bid_loading.style.display = "none"
    render_bid_details(product, stats)

def close_bid_section(event):
    """Close the bid details section"""
    bid_section = js.document.getElementById("bid-section")
    bid_section.style.display = "none"

async def main():
    """Main function to initialize the app"""
    try:
        print("Starting app...")
        loading = js.document.getElementById("loading")
        main_content = js.document.getElementById("main-content")
        
        print("Fetching products...")
        products = await fetch_products()
        print(f"Got {len(products)} products")
        
        print("Hiding loading, showing main content...")
        loading.style.display = "none"
        main_content.style.display = "block"
        print(f"main_content display is now: {main_content.style.display}")
        
        print("Rendering products...")
        render_products(products)
        print("Products rendered!")
        close_btn = js.document.getElementById("close-bid")
        close_btn.addEventListener("click", create_proxy(close_bid_section))
        
        async def wrapper(cp_id):
            await show_bid_details(cp_id)
        
        def trigger_show_bid(cp_id):
            asyncio.ensure_future(wrapper(cp_id))
        
        js.window.showBidDetails = create_proxy(trigger_show_bid)
        print("App initialized!")
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

asyncio.ensure_future(main())
