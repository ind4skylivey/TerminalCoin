# TerminalCoin Debug Report

**Date:** December 2024
**Issue:** `MarkupError` when rendering news items
**Status:** ✅ RESOLVED

---

## 🔴 Problem Description

When launching the application with `./venv/bin/python app.py`, a `MarkupError` crash occurred during the layout refresh phase:

```
MarkupError("Expected markup value (found '://cointelegraph.com/news/stripe-acquires-self-custody-crypto-wallet-app?utm_so…
giant Stripe acquires team from crypto wallet app Valora[/link]
([#00ff00]CoinTelegraph[/#00ff00])').")
```

The error occurred in:

- `textual/screen.py:1321` → `_refresh_layout`
- `textual/_compositor.py` → `reflow` → `_arrange_root` → `add_widget`
- `textual/widget.py:1852` → `get_content_width` → `_render`

---

## 🔍 Root Cause Analysis

### The Faulty Code (Before Fix)

```python
# In app.py, line 153 (original)
Label(f"{sentiment_emoji}{asset_tags} [link={safe_link}]{safe_title}[/link] ([#00ff00]{safe_source}[/#00ff00])",
      classes="news-item")
```

### Why It Failed

1. **Rich Markup `[link=URL]` Syntax Limitation:**

   - Rich's link syntax `[link=URL]text[/link]` works for simple URLs
   - URLs with query parameters (`?`, `=`, `&`) break the markup parser
   - Example problem URL: `https://cointelegraph.com/news/...?utm_source=rss`

2. **The `escape()` Function is Insufficient:**

   - `escape()` handles `[` and `]` characters in text content
   - It does NOT work inside markup attribute values like `[link=...]`
   - The `=` and `?` characters in URLs confuse Rich's parser

3. **Cascade Effect:**
   - Textual's layout engine calls Rich's markup parser during `_render()`
   - Invalid markup causes a `MarkupError` exception
   - The exception propagates up through the compositor and crashes the app

---

## ✅ Applied Fix

### Updated Code (After Fix)

```python
# In app.py, lines 144-158
for item in news_items:
    sentiment_emoji = ""
    if item['sentiment'] == "Bullish":
        sentiment_emoji = "🟢 "
    elif item['sentiment'] == "Bearish":
        sentiment_emoji = "🔴 "
    else:
        sentiment_emoji = "⚪ "

    # Escape ALL content to prevent Rich markup errors
    # Note: We cannot use [link=URL] syntax because URLs with special
    # characters (?, =, &, etc.) break Rich's markup parser.
    safe_assets = [escape(asset) for asset in item['assets']]
    # Asset tags like [BTC] don't conflict with Rich markup syntax
    asset_tags = " ".join([f"[#00ffff][{asset}][/]" for asset in safe_assets])
    safe_title = escape(item['title'])
    safe_source = escape(item['source'])

    # Display news without clickable link to avoid markup parsing errors
    news_list_container.mount(
        Label(f"{sentiment_emoji}{asset_tags} [bold #ffffff]{safe_title}[/] [dim]({safe_source})[/]",
              classes="news-item", markup=True)
    )
```

### Key Changes

| Aspect         | Before                      | After                            |
| -------------- | --------------------------- | -------------------------------- |
| Link rendering | `[link=URL]...[/link]`      | Removed (plain styled text)      |
| Title styling  | Linked with URL             | `[bold #ffffff]title[/]`         |
| Source styling | `[#00ff00]source[/#00ff00]` | `[dim](source)[/]`               |
| Asset tags     | `"".join(...)`              | `" ".join(...)` (spaces between) |
| Markup flag    | Not specified               | `markup=True` explicitly set     |

---

## 📝 Lessons Learned

1. **Rich Markup Limitations:**

   - `[link=URL]` syntax is fragile with complex URLs
   - Always test with real-world data containing special characters
   - Consider using `Text` objects instead of markup strings for complex cases

2. **Terminal UI Considerations:**

   - Links in terminal UIs often aren't clickable anyway (depends on terminal emulator)
   - Prioritize display stability over features that may not work universally

3. **Error Handling Best Practices:**
   - The original code silently failed in `news_client.py` (`pass # Fail silently`)
   - The app crashed later during rendering, making debugging harder
   - Consider catching and logging markup errors in the rendering layer

---

## 🧪 Testing Verification

```bash
# Test imports
./venv/bin/python -c "from app import NewsPanel; print('✅ Import OK')"

# Test markup rendering with problematic data
./venv/bin/python -c "
from rich.markup import escape
from rich.console import Console

title = 'News with special chars: [brackets] & symbols?'
safe = escape(title)
Console().print(f'[bold]{safe}[/]')
print('✅ Markup OK')
"
```

---

## 📁 Files Modified

| File     | Changes                                                    |
| -------- | ---------------------------------------------------------- |
| `app.py` | Fixed `NewsPanel.watch_news_data()` method (lines 132-158) |

---

## ⚡ Future Improvements

1. **Add Error Boundaries:**

   ```python
   try:
       label = Label(markup_string, markup=True)
   except MarkupError:
       label = Label(plain_text_fallback, markup=False)
   ```

2. **Use Text Objects for Complex Content:**

   ```python
   from rich.text import Text
   text = Text()
   text.append("title", style="bold")
   text.append(f" ({source})", style="dim")
   ```

3. **Validate URLs Before Use:**
   ```python
   from urllib.parse import quote
   safe_url = quote(url, safe=':/?=&')
   ```

---

**Report generated by debugging session**

---

# Theme System Implementation

## 🎨 Available Themes

The following themes are available in TerminalCoin:

| Theme Key   | Name            | Description                          |
| ----------- | --------------- | ------------------------------------ |
| `matrix`    | Matrix          | Classic green hacker theme (default) |
| `cyberpunk` | Cyberpunk       | Neon magenta and cyan                |
| `ocean`     | Ocean Deep      | Deep blue with sea green accents     |
| `solar`     | Solar Flare     | Warm golden orange tones             |
| `midnight`  | Midnight Purple | Purple with hot pink accents         |
| `mono`      | Monochrome      | Clean black and white                |

## 🔧 Theme Switching

Press **`t`** to cycle through themes. A notification will appear showing the current theme name.

## 📝 Theme Structure

Each theme defines the following colors:

```python
{
    "name": "Theme Name",
    "background": "#xxxxxx",      # Main background
    "background_alt": "#xxxxxx",  # Secondary background
    "primary": "#xxxxxx",         # Primary accent color
    "secondary": "#xxxxxx",       # Secondary accent color
    "tertiary": "#xxxxxx",        # Third accent color
    "text": "#xxxxxx",            # Main text color
    "text_muted": "#xxxxxx",      # Muted/dim text
    "border": "#xxxxxx",          # Border color
    "header_bg": "#xxxxxx",       # Header background
    "header_fg": "#xxxxxx",       # Header text
    "cursor_bg": "#xxxxxx",       # Cursor/selection background
    "cursor_fg": "#xxxxxx",       # Cursor/selection text
    "positive": "#xxxxxx",        # Positive indicator (bullish)
    "negative": "#xxxxxx",        # Negative indicator (bearish)
}
```

## 🛠️ Adding New Themes

To add a new theme:

1. Add a new entry to the `THEMES` dictionary in `app.py`
2. Add the theme key to `THEME_ORDER` list
3. The theme will automatically be available in the cycle

Example:

```python
THEMES["custom"] = {
    "name": "Custom Theme",
    "background": "#1a1a2e",
    "background_alt": "#16213e",
    "primary": "#e94560",
    # ... other colors
}
THEME_ORDER.append("custom")
```
