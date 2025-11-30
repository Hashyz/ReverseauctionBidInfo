# Reverse Auction Viewer

A Streamlit web application that displays active products from reverseauction.com.mm API and shows detailed bid statistics when users select a product.

## Overview
- **Purpose**: Display reverse auction products with bid analysis capabilities
- **Current State**: Fully functional with product display, filtering, and bid statistics
- **Framework**: Streamlit (pure Python)

## Architecture

### Main Application
- `streamlit_app.py` - Complete Streamlit application with:
  - Product fetching from API
  - Image loading (server-side to bypass HTTPS restrictions)
  - Bid history analysis
  - Filtering by status (Active/Upcoming/Ended)

### Configuration
- `requirements.txt` - Python dependencies (streamlit, requests, pandas)
- `.streamlit/` - Streamlit configuration

### API Endpoints Used
- Products: `http://reverseauction.com.mm/api/front/product/bid`
- Bid History: `http://www.reverseauction.com.mm/api/front/bid/history`

## Features
1. **Sidebar Controls**:
   - Filter by status (Active Now, All Products, Upcoming, Ended)
   - Quick stats dashboard
   - Refresh button

2. **Product Cards**:
   - Product images (loaded server-side)
   - Product names and descriptions (HTML cleaned)
   - Prices in MMK
   - Status badges (Active/Upcoming/Ended)
   - Relative timestamps
   - Bidder counts

3. **Bid Analysis Panel**:
   - Total bids count
   - Unique bidders count
   - Average bids per person
   - Top 10 bidders table
   - Bar chart visualization

## Running the App
The Streamlit app runs on port 5000 for Replit. For Streamlit Community Cloud, it uses default port 8501.

## Recent Changes
- 2025-11-30: Fixed image loading with server-side fetching (base64)
- 2025-11-30: Added HTML cleaning for product descriptions
- 2025-11-30: Enhanced UI with gradient titles, status badges, metrics
- 2025-11-30: Migrated from Flask+JavaScript to pure Streamlit
