import qrcode
from PIL import Image

def generate_qr(data, filename, color):
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    # Customizing colors: Background dark (to match readme), Foreground colored
    img = qr.make_image(fill_color=color, back_color="#0e1019").convert('RGB')
    
    # Resize for consistency
    img = img.resize((300, 300))
    
    img.save(filename)
    print(f"Saved {filename}")

# User Addresses
btc_addr = "bc1qg4he7nyq4j5r8mzq23e8shqvtvuymtmq5fur5k"
eth_addr = "0x21C8864A17324e907A7DCB8d70cD2C5030c5b765"
sol_addr = "BS3Nze14rdkPQQ8UkQZP4SU8uSc6de3UaVmv8gqh52e4"

# Generate
# BTC: Orange
generate_qr(btc_addr, "assets/btc-qr.png", "#f7931a")
# ETH: Blue/Purple
generate_qr(eth_addr, "assets/eth-qr.png", "#627eea")
# SOL: Green/Purple Gradient (Using solid purple for simplicity/readability)
generate_qr(sol_addr, "assets/sol-qr.png", "#14F195") # Solana Green

print("All QR codes generated.")
