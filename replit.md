# Reverse Auction Viewer

A web application that displays active products from reverseauction.com.mm API and shows detailed bid statistics when users select a product.

## Overview
- **Purpose**: Display reverse auction products with bid analysis capabilities
- **Current State**: Fully functional with product display and bid statistics

## Architecture

### Frontend
- `index.html` - Main HTML structure
- `app.js` - JavaScript application logic (product display, bid analysis)
- `style.css` - Modern dark theme styling

### Backend
- `server.py` - Flask proxy server that handles CORS-restricted API calls
  - `/api/products` - Fetches active products
  - `/api/bid-history` - Fetches bid history for a specific product

### API Endpoints Used
- Products: `https://reverseauction.com.mm/gateway/campaignproduct/active`
- Bid History: `https://reverseauction.com.mm/gateway/bid/bidhistory-web`

## Features
1. Product grid display with:
   - Product images from API
   - Product names and descriptions
   - Prices in MMK
   - Status badges (Upcoming/Active/Ended)
   - Bidder counts
2. Bid details panel with:
   - Total bids count
   - Unique bidders count
   - Top 10 bidders frequency table

## Running the App
The Flask server runs on port 5000 and serves both static files and proxied API endpoints.

## Recent Changes
- 2025-11-30: Migrated from PyScript to JavaScript for better performance and reliability
- 2025-11-30: Implemented bid analysis similar to user's Python Counter code
