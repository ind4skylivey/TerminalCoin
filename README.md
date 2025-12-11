# TerminalCoin 🪙

> **Crypto Dashboard CLI/TUI** - Precios, tendencias y datos de mercado en tiempo real, directamente en tu terminal.

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)

## 🖥️ Descripción

TerminalCoin es un dashboard de criptomonedas con una interfaz estilo **cyberpunk/hacker**. Diseñado para desarrolladores y entusiastas de la terminal que necesitan visualizar el mercado sin abrir un navegador pesado.

### ✨ Características Principales

*   **Live Ticker:** Precios en tiempo real de las top 100 criptomonedas.
*   **Diseño TUI:** Interfaz rica en terminal usando `Textual` (soporte para mouse y teclado).
*   **Ligero:** Bajo consumo de recursos.
*   **Estética Hacker:** Colores neón, gráficos ASCII y diseño minimalista.

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/TerminalCoin.git
cd TerminalCoin

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## 🎮 Uso

Para iniciar el dashboard:

```bash
python app.py
```

### Controles
*   `Click`: Seleccionar moneda para ver detalles.
*   `q`: Salir de la aplicación.
*   `r`: Refrescar datos manualmente.

## 🛠️ Tecnologías

*   [Python](https://www.python.org/)
*   [Textual](https://textual.textualize.io/) (TUI Framework)
*   [CoinGecko API](https://www.coingecko.com/en/api) (Datos de mercado)

---
*Created for the terminal enthusiast.*
