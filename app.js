const PRODUCTS_API = '/api/products';
const BID_HISTORY_API = '/api/bid-history';

let productsData = [];

function formatPrice(price) {
    return price.toLocaleString() + ' MMK';
}

function formatDateTime(dtString) {
    try {
        const dt = new Date(dtString);
        return dt.toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return dtString;
    }
}

function getStatusText(startTime, endTime) {
    const now = new Date();
    try {
        const start = new Date(startTime);
        const end = new Date(endTime);
        
        if (now < start) {
            return { class: 'upcoming', text: 'Upcoming' };
        } else if (now > end) {
            return { class: 'ended', text: 'Ended' };
        } else {
            return { class: 'active', text: 'Active Now' };
        }
    } catch {
        return { class: 'unknown', text: 'Unknown' };
    }
}

async function fetchProducts() {
    try {
        const response = await fetch(PRODUCTS_API);
        const data = await response.json();
        return data.data || [];
    } catch (e) {
        console.error('Error fetching products:', e);
        return [];
    }
}

async function fetchBidHistory(cpId) {
    try {
        const url = `${BID_HISTORY_API}?cp_id=${cpId}&pageSize=100000&current=1&sort=desc`;
        const response = await fetch(url);
        const data = await response.json();
        return data.data || [];
    } catch (e) {
        console.error('Error fetching bid history:', e);
        return [];
    }
}

function renderProducts(products) {
    productsData = products;
    const container = document.getElementById('products-container');
    container.innerHTML = '';
    
    if (!products || products.length === 0) {
        container.innerHTML = '<p style="color: #8892b0; text-align: center;">No products found</p>';
        return;
    }
    
    products.forEach(product => {
        const status = getStatusText(product.start_time, product.end_time);
        const images = (product.product_image || '').split(',');
        let firstImage = images[0] || '';
        if (firstImage.startsWith('http://reverseauction.com.mm')) {
            firstImage = '/api/image?url=' + encodeURIComponent(firstImage);
        }
        
        const card = document.createElement('div');
        card.className = `product-card ${status.class}`;
        card.setAttribute('data-cpid', product.cp_id);
        
        const description = product.description || '';
        const truncatedDesc = description.length > 100 ? description.substring(0, 100) + '...' : description;
        
        card.innerHTML = `
            <div class="product-image">
                <img src="${firstImage}" alt="${product.product_name || ''}" onerror="this.src='https://via.placeholder.com/200?text=No+Image'">
                <span class="status-badge ${status.class}">${status.text}</span>
            </div>
            <div class="product-info">
                <h3 class="product-name">${product.product_name || 'Unknown'}</h3>
                <p class="product-code">Code: ${product.product_code || 'N/A'}</p>
                ${truncatedDesc ? `<p class="product-description">${truncatedDesc}</p>` : ''}
                <p class="product-price">${formatPrice(product.product_price || 0)}</p>
                <div class="product-times">
                    <p><strong>Start:</strong> ${formatDateTime(product.start_time)}</p>
                    <p><strong>End:</strong> ${formatDateTime(product.end_time)}</p>
                </div>
                <p class="bid-count">Bidders: ${product.count_user || 0}</p>
                <button class="view-bids-btn" onclick="showBidDetails(${product.cp_id})">View Bid Details</button>
            </div>
        `;
        
        container.appendChild(card);
    });
}

function analyzeBids(bids) {
    if (!bids || bids.length === 0) {
        return {
            totalBids: 0,
            uniqueBidders: 0,
            topBidders: []
        };
    }
    
    const phoneNumbers = bids.map(bid => bid.isdn || 'Unknown');
    const counter = {};
    
    phoneNumbers.forEach(num => {
        counter[num] = (counter[num] || 0) + 1;
    });
    
    const sorted = Object.entries(counter)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    return {
        totalBids: bids.length,
        uniqueBidders: Object.keys(counter).length,
        topBidders: sorted
    };
}

function renderBidDetails(product, stats) {
    const detailsContainer = document.getElementById('bid-details');
    
    let rows = '';
    stats.topBidders.forEach(([number, count], index) => {
        rows += `
            <tr>
                <td>${index + 1}</td>
                <td>${number}</td>
                <td>${count}</td>
            </tr>
        `;
    });
    
    if (!rows) {
        rows = '<tr><td colspan="3" class="no-data">No bid data available</td></tr>';
    }
    
    detailsContainer.innerHTML = `
        <div class="stats-summary">
            <div class="stat-card">
                <span class="stat-value">${stats.totalBids.toLocaleString()}</span>
                <span class="stat-label">Total Bids</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.uniqueBidders.toLocaleString()}</span>
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
                ${rows}
            </tbody>
        </table>
    `;
}

async function showBidDetails(cpId) {
    const product = productsData.find(p => p.cp_id === cpId);
    if (!product) return;
    
    const bidSection = document.getElementById('bid-section');
    const bidLoading = document.getElementById('bid-loading');
    const bidDetails = document.getElementById('bid-details');
    const productName = document.getElementById('selected-product-name');
    
    productName.textContent = product.product_name || 'Bid Details';
    bidSection.style.display = 'block';
    bidLoading.style.display = 'flex';
    bidDetails.innerHTML = '';
    
    bidSection.scrollIntoView({ behavior: 'smooth' });
    
    const bids = await fetchBidHistory(cpId);
    const stats = analyzeBids(bids);
    
    bidLoading.style.display = 'none';
    renderBidDetails(product, stats);
}

function closeBidSection() {
    document.getElementById('bid-section').style.display = 'none';
}

let allProducts = [];
let currentFilter = 'active';

function filterProducts(filter) {
    currentFilter = filter;
    const now = new Date();
    
    let filtered = allProducts;
    if (filter === 'active') {
        filtered = allProducts.filter(p => {
            const start = new Date(p.start_time);
            const end = new Date(p.end_time);
            return now >= start && now <= end;
        });
    } else if (filter === 'upcoming') {
        filtered = allProducts.filter(p => {
            const start = new Date(p.start_time);
            return now < start;
        });
    } else if (filter === 'ended') {
        filtered = allProducts.filter(p => {
            const end = new Date(p.end_time);
            return now > end;
        });
    }
    
    renderProducts(filtered);
    updateFilterButtons(filter);
}

function updateFilterButtons(activeFilter) {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.filter === activeFilter) {
            btn.classList.add('active');
        }
    });
}

async function init() {
    const loading = document.getElementById('loading');
    const mainContent = document.getElementById('main-content');
    
    allProducts = await fetchProducts();
    
    loading.style.display = 'none';
    mainContent.style.display = 'block';
    
    filterProducts('active');
    
    document.getElementById('close-bid').addEventListener('click', closeBidSection);
    
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => filterProducts(btn.dataset.filter));
    });
}

document.addEventListener('DOMContentLoaded', init);
