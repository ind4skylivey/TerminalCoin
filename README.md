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

> _"Don't trust, verify. Don't browse, curl."_

## 💎 Features

### Core Features

- **🚀 Real-Time Ticker:** Live price feeds for the top 100 cryptocurrencies via CoinGecko API
- **📉 ASCII Sparklines:** Visualize 7-day price trends directly in your terminal using character-based micro-charts
- **📰 Crypto News Feed:** Real-time news with sentiment analysis (Bullish/Bearish/Neutral)
- **🎨 Multiple Themes:** 6 beautiful themes (Matrix, Cyberpunk, Ocean Deep, Solar Flare, Midnight Purple, Monochrome)
- **⚡ Zero Latency UX:** Keyboard-driven navigation. No mouse required (but supported)
- **🐧 Linux Native:** Built for the ecosystem. Pipes, virtual environments, and raw speed

### Version 2.0 - Clean Code & Security 🔒

- **✅ Clean Architecture:** Modular design with separation of concerns
- **✅ Type Safety:** Full type hints and Pydantic validation
- **✅ Security First:** Input validation, output sanitization, rate limiting
- **✅ Error Handling:** Comprehensive exception handling and logging
- **✅ Testing:** Unit tests and test infrastructure
- **✅ Documentation:** Extensive docs (ARCHITECTURE.md, SECURITY.md, REFACTORING.md)

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

<div align="center">

![TerminalCoin Live Demo](assets/terminalcoin_demo.gif)

<br>
<i>Live Market Data. Zero Latency. Pure Terminal.</i>
</div>

## 🛠️ Installation

Get up and running in seconds.

```bash
# 1. Clone the repository
git clone https://github.com/ind4skylivey/TerminalCoin.git
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

| Key      | Action                             |
| :------- | :--------------------------------- |
| `q`      | **Quit** the application           |
| `r`      | **Refresh** data immediately       |
| `Ctrl+P` | **Command palette** (change theme) |
| `Click`  | Select a coin to view details      |
| `↑/↓`    | Navigate the coin list             |

### Changing Themes

1. Press `Ctrl+P` to open the command palette
2. Type "theme" and select "Change theme"
3. Choose from: Matrix, Cyberpunk, Ocean Deep, Solar Flare, Midnight Purple, or Monochrome

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Code architecture and design patterns
- **[SECURITY.md](SECURITY.md)** - Security policy and best practices
- **[REFACTORING.md](REFACTORING.md)** - Version 2.0 refactoring details

## 🗺️ Roadmap

- [x] MVP Release (Live Prices)
- [x] Sparkline Charts
- [x] 📰 **Crypto News Feed** (RSS Integration)
- [x] 🎨 **Themes** (Matrix, Cyberpunk, Ocean, etc.)
- [ ] 👛 **Portfolio Tracker** (Local storage)
- [ ] 🔔 **Price Alerts** (Desktop notifications)

## 🤝 Contributing

Contributions are welcome. Fork the repo, create a branch, and push your code.
**Style Guide:** Keep it dark, keep it fast.

## 💸 Sovereignty Fund

If this tool helped you snipe a gem, consider feeding the developer's caffeine addiction.

<div align="center">

[![BTC](https://img.shields.io/badge/Bitcoin-bc1q...fur5k-f7931a?style=flat-square&logo=bitcoin)](https://mempool.space/address/bc1qg4he7nyq4j5r8mzq23e8shqvtvuymtmq5fur5k)
[![ETH](https://img.shields.io/badge/Ethereum-0x21...b765-627eea?style=flat-square&logo=ethereum)](https://etherscan.io/address/0x21C8864A17324e907A7DCB8d70cD2C5030c5b765)
[![SOL](https://img.shields.io/badge/Solana-BS3N...2e4-9945FF?style=flat-square&logo=solana)](https://solscan.io/account/BS3Nze14rdkPQQ8UkQZP4SU8uSc6de3UaVmv8gqh52e4)
[![Monero](https://img.shields.io/badge/Monero-86dX...FJs-ff6600?style=flat-square&logo=monero&logoColor=white)](https://www.getmonero.org/)

<br>

<img src="assets/btc-qr.png" width="160" alt="BTC QR">
<img src="assets/eth-qr.png" width="160" alt="ETH QR">
<img src="assets/sol-qr.png" width="160" alt="SOL QR">
<img src="assets/xmr-qr.png" width="160" alt="XMR QR">

</div>

---

<div align="center">
Built with 💚 and ₿ by il1v3y
</div>
