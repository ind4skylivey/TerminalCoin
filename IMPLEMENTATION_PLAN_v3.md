# TerminalCoin v3.0 "The Analyst" - Implementation Plan

## 🎯 Objective

Transform TerminalCoin from a monitoring dashboard into a comprehensive **Technical Analysis & Portfolio Management Tool**, maintaining the Clean Code and Security standards established in v2.0.

## 🛠️ Tech Stack Additions

| Component                | Library                 | Purpose                                                            |
| ------------------------ | ----------------------- | ------------------------------------------------------------------ |
| **Data Analysis**        | `pandas`                | efficient time-series data manipulation                            |
| **Technical Indicators** | `pandas_ta`             | Calculation of RSI, MACD, EMA, Bollinger Bands                     |
| **Charting**             | `textual-plotext`       | Rendering professional plots (candlesticks) inside Textual         |
| **Database**             | `sqlite3` + `aiosqlite` | Local storage for portfolio data                                   |
| **Security**             | `cryptography`          | Encryption for sensitive portfolio data (optional but recommended) |

---

## 📅 Phased Implementation

### Phase 1: The Engine (Data & Analysis)

**Goal:** Enable historical data fetching and technical indicator calculation.

1.  **Update `api_client.py`**:
    - Add method `get_historical_data(coin_id, days)` to fetch OHLC (Open, High, Low, Close) data.
2.  **Create `analysis_engine.py`**:
    - New module responsible for processing data with Pandas.
    - Implement methods: `calculate_rsi()`, `calculate_macd()`, `calculate_ema()`.
3.  **Update `models.py`**:
    - Add `OHLCData` model.
    - Add `TechnicalIndicators` model.

### Phase 2: The Visuals (Advanced Charting)

**Goal:** Replace simple sparklines with interactive terminal charts.

1.  **New Widget `CryptoChart`**:
    - Integrate `textual-plotext`.
    - Support switching between "Line" and "Candlestick" views.
    - Overlay indicators (e.g., SMA line on top of price).
2.  **UI Layout Update**:
    - Expand the detail view to accommodate the larger chart.
    - Add controls to toggle indicators (e.g., "Show RSI").

### Phase 3: The Vault (Portfolio Management)

**Goal:** Track personal holdings and performance.

1.  **Database Layer `database.py`**:
    - SQLite setup with schema for `Holdings` and `Transactions`.
2.  **Portfolio Logic `portfolio_manager.py`**:
    - Add/Remove transactions.
    - Calculate P&L (Profit and Loss) based on current prices.
3.  **New Tab/View `PortfolioView`**:
    - Table showing owned assets, average buy price, current value, and % gain/loss.

---

## 🏗️ Architecture Update

```
TerminalCoin/
├── Core/
│   ├── ... (existing)
│   └── database.py        # 🆕 SQLite handler
├── Business Logic/
│   ├── ... (existing)
│   ├── analysis_engine.py # 🆕 Pandas & TA logic
│   └── portfolio_mgr.py   # 🆕 Portfolio logic
├── Presentation/
│   ├── ... (existing)
│   ├── widgets/
│   │   ├── chart.py       # 🆕 Advanced charting widget
│   │   └── portfolio.py   # 🆕 Portfolio UI
│   └── app.py
```

## 📝 Next Steps

1.  Update `requirements.txt` with new dependencies.
2.  Implement **Phase 1: The Engine**.
3.  Verify data calculation with tests.
