<div align="center">

![TerminalCoin Banner](assets/terminal_banner.png)

### The Crypto Terminal Dashboard for the Sovereign Developer

[![Bitcoin Price](https://img.shields.io/badge/dynamic/json?color=orange&label=BTC&query=%24.bitcoin.usd&url=https%3A%2F%2Fapi.coingecko.com%2Fapi%2Fv3%2Fsimple%2Fprice%3Fids%3Dbitcoin%26vs_currencies%3Dusd&style=for-the-badge&logo=bitcoin)](https://coingecko.com)
[![Ethereum Price](https://img.shields.io/badge/dynamic/json?color=blue&label=ETH&query=%24.ethereum.usd&url=https%3A%2F%2Fapi.coingecko.com%2Fapi%2Fv3%2Fsimple%2Fprice%3Fids%3Dethereum%26vs_currencies%3Dusd&style=for-the-badge&logo=ethereum)](https://coingecko.com)

[![Python](https://img.shields.io/badge/Python-3.8+-ffe100?style=for-the-badge&logo=python&logoColor=black)](https://python.org)
[![Textual](https://img.shields.io/badge/TUI-Textual-00ff00?style=for-the-badge&logo=terminal&logoColor=black)](https://textual.textualize.io/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

</div>

---

## ⚡ The Philosophy

**Web browsers are bloated.** Tracking scripts, heavy JavaScript, and distracting ads have no place in a trader's sanctuary.

**TerminalCoin** brings the market back to where it belongs: the Command Line. Fast, resource-efficient, and purely focused on data. It combines the raw power of `ssh` aesthetics with modern reactive UI technology.

> *"Don't trust, verify. Don't browse, curl."*

## 💎 Features

*   **🚀 Real-Time Ticker:** Live price feeds for the top 100 cryptocurrencies via CoinGecko.
*   **📉 ASCII Sparklines:** Visualize 7-day price trends directly in your terminal using character-based micro-charts.
*   **🎨 Cyberpunk UI:** A carefully crafted neon-on-black aesthetic (Green/Cyan) designed for late-night coding sessions.
*   **⚡ Zero Latency UX:** Keyboard-driven navigation. No mouse required (but supported).
*   **🐧 Linux Native:** Built for the ecosystem. Pipes, virtual environments, and raw speed.

## 🔗 Supported Assets

We track the entire market, but we optimize for the kings:

<p align="center">
  <img src="assets/icon_btc.png" width="200" alt="Bitcoin">
  <img src="assets/icon_eth.png" width="200" alt="Ethereum">
</p>

<p align="center">
  <b>BITCOIN [BTC]</b> - The Standard.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <b>ETHEREUM [ETH]</b> - The Computer.
</p>

## 📸 Preview

*(Place a screenshot of your terminal here. For now, imagine a beautiful green glowing grid of data)*

```text
+---------------------+---------------------------------------------------+
| Market Cap Top 50   |  Bitcoin (BTC)                                    |
+---------------------+                                                   |
| 1. BTC   $98,420    |  $98,420.00                                       |
| 2. ETH   $3,890     |                                                   |
| 3. SOL   $145       |  [7 Day Trend]                                    |
| 4. BNB   $620       |   ▂▃▄▅▆▇█                                       |
| ...                 |                                                   |
|                     |  High 24h: $99,100                                |
|                     |  Low 24h:  $97,200                                |
+---------------------+---------------------------------------------------+
```

## 🛠️ Installation

Get up and running in seconds.

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/TerminalCoin.git
cd TerminalCoin

# 2. Create a virtual environment (Recommended)
python3 -m venv venv
source venv/bin/activate  # Or 'source venv/bin/activate.fish' for fish users

# 3. Install dependencies
pip install -r requirements.txt
```

## 🎮 Usage

Launch the dashboard:

```bash
python app.py
```

### Controls

| Key | Action |
| :--- | :--- |
| `q` | **Quit** the application |
| `r` | **Refresh** data immediately |
| `Click` | Select a coin to view details |
| `↑/↓` | Navigate the coin list |

## 🗺️ Roadmap

*   [x] MVP Release (Live Prices)
*   [x] Sparkline Charts
*   [ ] 📰 **Crypto News Feed** (RSS Integration)
*   [ ] 👛 **Portfolio Tracker** (Local storage)
*   [ ] 🔔 **Price Alerts** (Desktop notifications)

## 🤝 Contributing

Contributions are welcome. Fork the repo, create a branch, and push your code.
**Style Guide:** Keep it dark, keep it fast.

## 💸 Sovereignty Fund

If this tool helped you snipe a gem, consider feeding the developer's caffeine addiction.

*   **BTC:** `bc1qg4he7nyq4j5r8mzq23e8shqvtvuymtmq5fur5k`
*   **ETH:** `0x21C8864A17324e907A7DCB8d70cD2C5030c5b765`
*   **SOL:** `BS3Nze14rdkPQQ8UkQZP4SU8uSc6de3UaVmv8gqh52eR`

---

<div align="center">
Built with 💚 and ₿ by il1v3y
</div>