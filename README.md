# 🪙 Crypto Tracker

A simple Python script that scrapes the latest cryptocurrency prices, market caps, and 24h changes from [CoinMarketCap](https://coinmarketcap.com/) using **Selenium**.

## 📌 Features
- Scrapes top N cryptocurrencies (default: 10)
- Extracts:
  - Name
  - Current Price
  - 24h Change %
  - Market Cap
- Saves data with timestamp to **CSV file** (`crypto_prices.csv`)
- Headless mode (runs without opening browser window)

## 🚀 Installation & Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/crypto-tracker.git
   cd crypto-tracker
