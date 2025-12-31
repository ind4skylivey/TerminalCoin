#!/bin/bash
# TerminalCoin Demo Recording Script
# Records terminal session with asciinema

CAST_FILE="terminalcoin_demo.cast"

clear
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           🎬 TerminalCoin Demo Recorder                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 What will happen:"
echo "   1. Recording starts"
echo "   2. App launches AUTOMATICALLY inside the recording"
echo "   3. You interact with the app (all recorded)"
echo "   4. Press 'q' to quit app → then 'exit' to stop recording"
echo ""
echo "🎮 Demo actions to show:"
echo "   • Arrow keys: Navigate coins"
echo "   • Enter: Select a coin (shows details)"
echo "   • Ctrl+P: Open command palette → type theme name"
echo "   • Show 2-3 different themes"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Press ENTER when ready to start recording... "

echo ""
echo "Starting in..."
for i in 3 2 1; do
    echo "  $i..."
    sleep 1
done
echo "  🔴 RECORDING!"
echo ""

# Start interactive recording (YOU control when it stops)
echo "💡 Type: ./venv/bin/python app.py"
echo "💡 When done with demo, type: exit"
echo ""
asciinema rec "$CAST_FILE" --overwrite

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Recording saved to: $CAST_FILE"
echo ""
echo "📤 To convert to GIF:"
echo ""
echo "   Option A - Online (easy):"
echo "     1. asciinema upload $CAST_FILE"
echo "     2. Go to https://dstein64.github.io/gifcast/"
echo ""
echo "   Option B - Local with agg:"
echo "     cargo install --git https://github.com/asciinema/agg"
echo "     agg $CAST_FILE demo.gif --font-size 14"
echo ""
