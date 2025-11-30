# Reverse Auction Viewer

A web application that displays active products from reverseauction.com.mm API and shows detailed bid statistics when users select a product.

## Overview
- **Purpose**: Display reverse auction products with bid analysis capabilities
- **Current State**: Fully functional - requires reverseauction.com.mm API to be accessible

## Architecture

### Frontend (Static)
- `index.html` - Main HTML structure
- `app.js` - JavaScript application logic (product display, bid analysis)
- `style.css` - Modern dark theme styling

### Backend (Required for API proxy)
- `server.py` - Minimal Flask proxy server
  - Required because reverseauction.com.mm API doesn't support CORS
  - `/api/products` - Proxies active products request
  - `/api/bid-history` - Proxies bid history request

### Why Backend is Needed
The reverseauction.com.mm API doesn't include CORS headers, which means browsers block direct requests from web pages. The Flask server acts as a relay to bypass this browser security restriction.

## Features
1. Product grid display with images, prices, and status badges (Upcoming/Active/Ended)
2. Bid details panel with:
   - Total bids count
   - Unique bidders count
   - Top 10 bidders frequency table

## Running the App
```
python server.py
```
The Flask server runs on port 5000.

## Recent Changes
- 2025-11-30: Migrated from PyScript to JavaScript for better performance
- 2025-11-30: Simplified Flask backend to minimal proxy server
