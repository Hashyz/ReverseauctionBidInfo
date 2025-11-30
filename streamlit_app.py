import streamlit as st
import requests
from collections import Counter
from datetime import datetime
import os

st.set_page_config(
    page_title="Reverse Auction Products",
    page_icon="🛒",
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

@st.cache_data(ttl=30)
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
            return "upcoming", "🟡 Upcoming"
        elif now > end:
            return "ended", "🔴 Ended"
        else:
            return "active", "🟢 Active Now"
    except:
        return "unknown", "❓ Unknown"

def format_price(price):
    return f"{price:,} MMK"

def analyze_bids(bids):
    if not bids:
        return 0, 0, []
    
    phone_numbers = [bid.get('isdn', 'Unknown') for bid in bids]
    counter = Counter(phone_numbers)
    top_10 = counter.most_common(10)
    
    return len(bids), len(counter), top_10

st.title("🛒 Reverse Auction Products")
st.caption("Click on a product to view bid details")

products = fetch_products()

if not products:
    st.warning("No products found")
    st.stop()

filter_options = ["Active Now", "All", "Upcoming", "Ended"]
selected_filter = st.selectbox("Filter Products", filter_options, index=0)

now = datetime.now()
filtered_products = []

for p in products:
    status_key, _ = get_status(p.get('start_time', ''), p.get('end_time', ''))
    
    if selected_filter == "All":
        filtered_products.append(p)
    elif selected_filter == "Active Now" and status_key == "active":
        filtered_products.append(p)
    elif selected_filter == "Upcoming" and status_key == "upcoming":
        filtered_products.append(p)
    elif selected_filter == "Ended" and status_key == "ended":
        filtered_products.append(p)

if not filtered_products:
    st.info(f"No {selected_filter.lower()} products found")
else:
    cols = st.columns(3)
    
    for idx, product in enumerate(filtered_products):
        col = cols[idx % 3]
        
        with col:
            status_key, status_text = get_status(product.get('start_time', ''), product.get('end_time', ''))
            
            images = (product.get('product_image', '') or '').split(',')
            first_image = images[0] if images else ''
            
            with st.container(border=True):
                st.markdown(f"**{status_text}**")
                
                if first_image:
                    st.image(first_image, use_container_width=True)
                
                st.subheader(product.get('product_name', 'Unknown'))
                st.caption(f"Code: {product.get('product_code', 'N/A')}")
                
                description = product.get('description', '')
                if description:
                    st.text(description[:100] + '...' if len(description) > 100 else description)
                
                st.markdown(f"### :green[{format_price(product.get('product_price', 0))}]")
                
                st.text(f"Start: {product.get('start_time', 'N/A')}")
                st.text(f"End: {product.get('end_time', 'N/A')}")
                st.text(f"Bidders: {product.get('count_user', 0)}")
                
                if st.button("View Bid Details", key=f"btn_{product.get('cp_id')}"):
                    st.session_state.selected_product = product

if 'selected_product' in st.session_state and st.session_state.selected_product:
    product = st.session_state.selected_product
    
    st.divider()
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.header(f"📊 Bid Details: {product.get('product_name', 'Unknown')}")
    with col2:
        if st.button("Close"):
            st.session_state.selected_product = None
            st.rerun()
    
    with st.spinner("Loading bid history..."):
        bids = fetch_bid_history(product.get('cp_id'))
        total_bids, unique_bidders, top_bidders = analyze_bids(bids)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Bids", f"{total_bids:,}")
    
    with col2:
        st.metric("Unique Bidders", f"{unique_bidders:,}")
    
    st.subheader("Top 10 Bidders")
    
    if top_bidders:
        import pandas as pd
        df = pd.DataFrame(top_bidders, columns=["Phone Number", "Bid Count"])
        df.index = df.index + 1
        df.index.name = "Rank"
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No bid data available")
