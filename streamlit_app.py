import streamlit as st
import requests
from datetime import datetime
from collections import Counter

st.set_page_config(
    page_title="Reverse Auction Products",
    page_icon="🏷️",
    layout="wide"
)

PRODUCTS_API = "http://reverseauction.com.mm/api/front/product/bid"
BID_HISTORY_API = "http://www.reverseauction.com.mm/api/front/bid/history"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Origin": "http://www.reverseauction.com.mm",
    "Referer": "http://www.reverseauction.com.mm/up-next",
}

@st.cache_data(ttl=60)
def fetch_products():
    try:
        response = requests.get(PRODUCTS_API, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_bid_history(cp_id):
    try:
        url = f"{BID_HISTORY_API}?pageSize=100000&current=1&sort=desc&cp_ids={cp_id}"
        response = requests.get(url, headers=HEADERS, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])
    except Exception as e:
        st.error(f"Error fetching bid history: {e}")
        return []

def get_status(start_time, end_time):
    now = datetime.now()
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00').replace('+00:00', ''))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00').replace('+00:00', ''))
        
        if now < start:
            return "upcoming", "Upcoming"
        elif now > end:
            return "ended", "Ended"
        else:
            return "active", "Active Now"
    except:
        return "unknown", "Unknown"

def format_price(price):
    return f"{price:,} MMK"

def analyze_bids(bids):
    if not bids:
        return {"total": 0, "unique": 0, "top_bidders": []}
    
    phone_numbers = [bid.get('isdn', 'Unknown') for bid in bids]
    counter = Counter(phone_numbers)
    top_10 = counter.most_common(10)
    
    return {
        "total": len(bids),
        "unique": len(counter),
        "top_bidders": top_10
    }

st.markdown("""
<style>
    .product-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .price {
        color: #00ff88;
        font-size: 1.3rem;
        font-weight: bold;
    }
    .status-active {
        background: #00ff88;
        color: black;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.8rem;
    }
    .status-upcoming {
        background: #ffd700;
        color: black;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.8rem;
    }
    .status-ended {
        background: #ff6b6b;
        color: white;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏷️ Reverse Auction Products")
st.caption("Click on a product to view bid details")

products = fetch_products()

filter_option = st.radio(
    "Filter by status:",
    ["Active Now", "All", "Upcoming", "Ended"],
    horizontal=True
)

now = datetime.now()
filtered_products = []

for p in products:
    status_key, status_text = get_status(p.get('start_time', ''), p.get('end_time', ''))
    p['status_key'] = status_key
    p['status_text'] = status_text
    
    if filter_option == "All":
        filtered_products.append(p)
    elif filter_option == "Active Now" and status_key == "active":
        filtered_products.append(p)
    elif filter_option == "Upcoming" and status_key == "upcoming":
        filtered_products.append(p)
    elif filter_option == "Ended" and status_key == "ended":
        filtered_products.append(p)

if not filtered_products:
    st.info(f"No {filter_option.lower()} products found.")
else:
    cols = st.columns(3)
    
    for idx, product in enumerate(filtered_products):
        with cols[idx % 3]:
            with st.container():
                images = (product.get('product_image', '') or '').split(',')
                first_image = images[0] if images else ''
                
                status_class = f"status-{product['status_key']}"
                
                st.markdown(f"<span class='{status_class}'>{product['status_text']}</span>", unsafe_allow_html=True)
                
                if first_image:
                    st.image(first_image, use_container_width=True)
                
                st.subheader(product.get('product_name', 'Unknown'))
                st.caption(f"Code: {product.get('product_code', 'N/A')}")
                
                description = product.get('description', '')
                if description:
                    st.text(description[:100] + '...' if len(description) > 100 else description)
                
                st.markdown(f"<p class='price'>{format_price(product.get('product_price', 0))}</p>", unsafe_allow_html=True)
                
                st.text(f"Start: {product.get('start_time', 'N/A')}")
                st.text(f"End: {product.get('end_time', 'N/A')}")
                st.text(f"Bidders: {product.get('count_user', 0)}")
                
                if st.button("View Bid Details", key=f"btn_{product.get('cp_id')}"):
                    st.session_state['selected_product'] = product
                
                st.divider()

if 'selected_product' in st.session_state and st.session_state['selected_product']:
    product = st.session_state['selected_product']
    
    st.header(f"📊 Bid Details: {product.get('product_name', '')}")
    
    if st.button("Close"):
        del st.session_state['selected_product']
        st.rerun()
    
    with st.spinner("Loading bid history..."):
        bids = fetch_bid_history(product.get('cp_id'))
        stats = analyze_bids(bids)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Bids", f"{stats['total']:,}")
    with col2:
        st.metric("Unique Bidders", f"{stats['unique']:,}")
    
    st.subheader("Top 10 Bidders")
    if stats['top_bidders']:
        for i, (phone, count) in enumerate(stats['top_bidders'], 1):
            st.text(f"{i}. {phone}: {count} bids")
    else:
        st.info("No bid data available")
