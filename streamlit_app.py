import streamlit as st
import requests
from collections import Counter
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="Reverse Auction Products",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d9ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .product-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(0, 217, 255, 0.2);
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 217, 255, 0.15);
    }
    .status-active {
        background: linear-gradient(90deg, #00ff88, #00d9ff);
        color: #000;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-upcoming {
        background: linear-gradient(90deg, #ffd700, #ffaa00);
        color: #000;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-ended {
        background: linear-gradient(90deg, #ff6b6b, #ff4757);
        color: #fff;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .price-tag {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00ff88;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(0, 217, 255, 0.3);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00d9ff;
    }
    .metric-label {
        color: #8892b0;
        font-size: 0.9rem;
    }
    .bid-table {
        border-radius: 12px;
        overflow: hidden;
    }
    .stDataFrame {
        border-radius: 12px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #00d9ff;
    }
    .time-info {
        color: #8892b0;
        font-size: 0.85rem;
    }
    .bidder-count {
        color: #00d9ff;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

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
            return "upcoming", "🟡 UPCOMING", "status-upcoming"
        elif now > end:
            return "ended", "🔴 ENDED", "status-ended"
        else:
            return "active", "🟢 ACTIVE NOW", "status-active"
    except:
        return "unknown", "❓ UNKNOWN", ""

def format_price(price):
    return f"{price:,} MMK"

def get_relative_time(dt_string):
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00').replace('+00:00', ''))
        now = datetime.now()
        diff = dt - now
        
        if diff.total_seconds() < 0:
            diff = now - dt
            if diff.days > 0:
                return f"{diff.days} days ago"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600} hours ago"
            else:
                return f"{diff.seconds // 60} mins ago"
        else:
            if diff.days > 0:
                return f"in {diff.days} days"
            elif diff.seconds > 3600:
                return f"in {diff.seconds // 3600} hours"
            else:
                return f"in {diff.seconds // 60} mins"
    except:
        return ""

def analyze_bids(bids):
    if not bids:
        return 0, 0, []
    
    phone_numbers = [bid.get('isdn', 'Unknown') for bid in bids]
    counter = Counter(phone_numbers)
    top_10 = counter.most_common(10)
    
    return len(bids), len(counter), top_10

with st.sidebar:
    st.markdown("### 🎯 Filters")
    st.markdown("---")
    
    filter_options = ["🟢 Active Now", "📋 All Products", "🟡 Upcoming", "🔴 Ended"]
    selected_filter = st.radio(
        "Show products:",
        filter_options,
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    
    products = fetch_products()
    if products:
        now = datetime.now()
        active_count = sum(1 for p in products if get_status(p.get('start_time', ''), p.get('end_time', ''))[0] == "active")
        upcoming_count = sum(1 for p in products if get_status(p.get('start_time', ''), p.get('end_time', ''))[0] == "upcoming")
        ended_count = sum(1 for p in products if get_status(p.get('start_time', ''), p.get('end_time', ''))[0] == "ended")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active", active_count)
            st.metric("Ended", ended_count)
        with col2:
            st.metric("Upcoming", upcoming_count)
            st.metric("Total", len(products))
    
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown('<h1 class="main-header">🛒 Reverse Auction Products</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Real-time auction monitoring with bid analytics</p>', unsafe_allow_html=True)

if not products:
    st.warning("⚠️ No products found. Please try refreshing.")
    st.stop()

filter_map = {
    "🟢 Active Now": "active",
    "📋 All Products": "all",
    "🟡 Upcoming": "upcoming",
    "🔴 Ended": "ended"
}
filter_key = filter_map.get(selected_filter, "active")

filtered_products = []
for p in products:
    status_key, _, _ = get_status(p.get('start_time', ''), p.get('end_time', ''))
    
    if filter_key == "all":
        filtered_products.append(p)
    elif filter_key == status_key:
        filtered_products.append(p)

if not filtered_products:
    st.info(f"📭 No {selected_filter.split(' ', 1)[1].lower()} products at the moment.")
else:
    st.markdown(f"### Showing {len(filtered_products)} product(s)")
    
    cols = st.columns(3)
    
    for idx, product in enumerate(filtered_products):
        col = cols[idx % 3]
        
        with col:
            status_key, status_text, status_class = get_status(
                product.get('start_time', ''), 
                product.get('end_time', '')
            )
            
            images = (product.get('product_image', '') or '').split(',')
            first_image = images[0] if images else ''
            
            with st.container(border=True):
                st.markdown(f'<span class="{status_class}">{status_text}</span>', unsafe_allow_html=True)
                
                if first_image:
                    st.image(first_image, use_container_width=True)
                
                st.markdown(f"#### {product.get('product_name', 'Unknown')}")
                
                st.caption(f"📦 Code: `{product.get('product_code', 'N/A')}`")
                
                description = product.get('description', '')
                if description:
                    with st.expander("📝 Description"):
                        st.write(description)
                
                st.markdown(f'<p class="price-tag">💰 {format_price(product.get("product_price", 0))}</p>', unsafe_allow_html=True)
                
                start_rel = get_relative_time(product.get('start_time', ''))
                end_rel = get_relative_time(product.get('end_time', ''))
                
                time_col1, time_col2 = st.columns(2)
                with time_col1:
                    st.markdown(f"🟢 **Start**")
                    st.caption(f"{start_rel}")
                with time_col2:
                    st.markdown(f"🔴 **End**")
                    st.caption(f"{end_rel}")
                
                bidder_count = product.get('count_user', 0)
                st.markdown(f'<p class="bidder-count">👥 {bidder_count:,} Bidders</p>', unsafe_allow_html=True)
                
                if st.button("📊 View Bid Analysis", key=f"btn_{product.get('cp_id')}", use_container_width=True):
                    st.session_state.selected_product = product

if 'selected_product' in st.session_state and st.session_state.selected_product:
    product = st.session_state.selected_product
    
    st.markdown("---")
    
    header_col1, header_col2 = st.columns([5, 1])
    with header_col1:
        st.markdown(f"## 📊 Bid Analysis: {product.get('product_name', 'Unknown')}")
    with header_col2:
        if st.button("✖️ Close", use_container_width=True):
            st.session_state.selected_product = None
            st.rerun()
    
    with st.spinner("🔄 Loading bid history..."):
        bids = fetch_bid_history(product.get('cp_id'))
        total_bids, unique_bidders, top_bidders = analyze_bids(bids)
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(
            label="📈 Total Bids",
            value=f"{total_bids:,}",
            delta=None
        )
    
    with metric_col2:
        st.metric(
            label="👥 Unique Bidders",
            value=f"{unique_bidders:,}",
            delta=None
        )
    
    with metric_col3:
        avg_bids = round(total_bids / unique_bidders, 1) if unique_bidders > 0 else 0
        st.metric(
            label="📊 Avg Bids/Person",
            value=f"{avg_bids}",
            delta=None
        )
    
    st.markdown("### 🏆 Top 10 Most Active Bidders")
    
    if top_bidders:
        df = pd.DataFrame(top_bidders, columns=["📱 Phone Number", "🎯 Bid Count"])
        df.index = range(1, len(df) + 1)
        df.index.name = "🏅 Rank"
        
        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )
        
        st.markdown("### 📈 Bid Distribution")
        chart_df = pd.DataFrame(top_bidders, columns=["Bidder", "Bids"])
        st.bar_chart(chart_df.set_index("Bidder"))
    else:
        st.info("📭 No bid data available for this product yet.")

st.markdown("---")
st.caption("🔄 Data refreshes every 60 seconds | Built with Streamlit")
