import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from flask_mail import Mail, Message

# --- Telegram Bot ---
TELEGRAM_TOKEN = "8305532022:AAHZbefgG_cOxa0w1FnTMeDD7mPsTE-dc2E"
TELEGRAM_CHAT_ID = "802287154"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=payload)

# --- Flask app setup ---
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# --- Optional email config (for invoice) ---
app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_USE_TLS=str(os.getenv("MAIL_USE_TLS", "true")).lower() == "true",
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER", os.getenv("MAIL_USERNAME")),
)
mail = Mail(app)

# --- Inventory ---
PRODUCTS = [
    {"id": "TS1", "name": "Classic Tee - White", "category": "shirts", "subtype": "t-shirt", "price": 12.99, "image": "/static/193420162-front-pdp.jpg", "desc": "Soft cotton tee in white."},
    {"id": "TS2", "name": "Classic Tee - Black", "category": "shirts", "subtype": "t-shirt", "price": 12.99, "image": "/static/Shirt 2.jpg", "desc": "Soft cotton tee in black."},
    {"id": "TS3", "name": "Graphic Tee - Sunset", "category": "shirts", "subtype": "t-shirt", "price": 16.99, "image": "/static/Shirt3.webp", "desc": "Sunset print graphic tee."},
    {"id": "TS4", "name": "Athletic Tee - DryFit", "category": "shirts", "subtype": "t-shirt", "price": 18.50, "image": "/static/Shirt4.webp", "desc": "Breathable moisture-wicking tee."},
    {"id": "TS5", "name": "Pocket Tee - Navy", "category": "shirts", "subtype": "t-shirt", "price": 14.50, "image": "/static/Shirt5.webp", "desc": "Navy tee with chest pocket."},
    {"id": "LS1", "name": "Long Sleeve - Heather Gray", "category": "shirts", "subtype": "long sleeve", "price": 19.99, "image": "/static/Shirt6.jpg", "desc": "Comfy long sleeve shirt."},
    {"id": "LS2", "name": "Long Sleeve - Forest", "category": "shirts", "subtype": "long sleeve", "price": 19.99, "image": "/static/Shirt7.jpg", "desc": "Forest green long sleeve."},
    {"id": "JK1", "name": "Denim Jacket", "category": "shirts", "subtype": "jacket", "price": 49.99, "image": "/static/Shirt8.webp", "desc": "Classic denim jacket."},
    {"id": "JK2", "name": "Bomber Jacket", "category": "shirts", "subtype": "jacket", "price": 59.99, "image": "/static/Shirt9.webp", "desc": "Lightweight bomber style."},
    {"id": "JK3", "name": "Windbreaker", "category": "shirts", "subtype": "jacket", "price": 39.99, "image": "/static/Shirt10.jpg", "desc": "Packable windbreaker."},
    {"id": "PT1", "name": "Chino Trousers - Khaki", "category": "pants", "subtype": "trousers", "price": 29.99, "image": "/static/Pant1.webp", "desc": "Slim-fit khaki chinos."},
    {"id": "PT2", "name": "Chino Trousers - Navy", "category": "pants", "subtype": "trousers", "price": 29.99, "image": "/static/Pant2.jpg", "desc": "Slim-fit navy chinos."},
    {"id": "PT3", "name": "Stretch Trousers - Black", "category": "pants", "subtype": "trousers", "price": 32.99, "image": "/static/Pant3.webp", "desc": "Stretchy black trousers."},
    {"id": "PT4", "name": "Linen Trousers", "category": "pants", "subtype": "trousers", "price": 34.99, "image": "/static/Pant4.jpg", "desc": "Breathable linen blend."},
    {"id": "PT5", "name": "Cargo Trousers - Olive", "category": "pants", "subtype": "trousers", "price": 35.99, "image": "/static/Pant5.webp", "desc": "Utility cargo trousers."},
    {"id": "PT6", "name": "Tailored Trousers - Gray", "category": "pants", "subtype": "trousers", "price": 39.99, "image": "/static/Pant6.jpg", "desc": "Smart tailored fit."},
    {"id": "SH1", "name": "Sneaker - White Low", "category": "shoes", "subtype": "sneaker", "price": 44.99, "image": "/static/Shoes1.webp", "desc": "Minimal white sneakers."},
    {"id": "SH2", "name": "Sneaker - Black Runner", "category": "shoes", "subtype": "sneaker", "price": 49.99, "image": "/static/Shoes2.webp", "desc": "Lightweight running shoe."},
    {"id": "SH3", "name": "Sneaker - Retro", "category": "shoes", "subtype": "sneaker", "price": 59.99, "image": "/static/Shoes3.webp", "desc": "Retro style sneaker."},
    {"id": "SH4", "name": "Sneaker - Canvas High", "category": "shoes", "subtype": "sneaker", "price": 39.99, "image": "/static/Shoes4.webp", "desc": "Classic high-top canvas."},
    {"id": "SH5", "name": "Sneaker - Trail", "category": "shoes", "subtype": "sneaker", "price": 69.99, "image": "/static/Shoes5.webp", "desc": "Rugged trail sneaker."},
]

def get_product(pid):
    return next((p for p in PRODUCTS if p['id'] == pid), None)

def cart_items():
    cart = session.get("cart", {})
    items, total = [], 0.0
    for pid, qty in cart.items():
        product = get_product(pid)
        if not product:
            continue
        line_total = product["price"] * qty
        items.append({"product": product, "qty": qty, "line_total": line_total})
        total += line_total
    return items, round(total, 2)

# --- Routes ---
@app.route("/")
def home():
    return render_template("home.html", products=PRODUCTS)

@app.route("/products")
def products():
    sections = {
        "Shirts": [p for p in PRODUCTS if p["category"] == "shirts"],
        "Pants":  [p for p in PRODUCTS if p["category"] == "pants"],
        "Shoes":  [p for p in PRODUCTS if p["category"] == "shoes"],
    }
    return render_template("products.html", sections=sections)

@app.route("/about")
def about():
    team = [
        {"name": "Nova Member 1", "role": "Founder", "bio": "Leads vision and quality.", "img": "/static/pro1.jpg"},
        {"name": "Nova Member 2", "role": "Designer", "bio": "Designs fresh looks.", "img": "/static/pro2.jpg"},
        {"name": "Nova Member 3", "role": "Engineer", "bio": "Builds fast web.", "img": "/static/pro3.jpg"},
        {"name": "Nova Member 4", "role": "Support", "bio": "Takes care of customers.", "img": "/static/pro4.jpg"},
    ]
    return render_template("about.html", team=team)

@app.route("/product/<pid>")
def product_detail(pid):
    p = get_product(pid)
    if not p:
        flash("Product not found.", "danger")
        return redirect(url_for("home"))
    return render_template("product.html", p=p)

@app.route("/cart")
def cart():
    items, total = cart_items()
    return render_template("cart.html", items=items, total=total)

@app.route("/cart/add", methods=["POST"])
def cart_add():
    pid = request.form.get("pid")
    qty = int(request.form.get("qty", "1"))
    if qty < 1: qty = 1
    p = get_product(pid)
    if not p:
        flash("Product not found.", "danger")
        return redirect(url_for("home"))
    cart = session.get("cart", {})
    cart[pid] = cart.get(pid, 0) + qty
    session["cart"] = cart
    flash(f"Added {qty} × {p['name']} to cart.", "success")
    return redirect(url_for("cart"))

@app.route("/cart/update", methods=["POST"])
def cart_update():
    pid = request.form.get("pid")
    qty = max(1, int(request.form.get("qty", "1")))
    cart = session.get("cart", {})
    if pid in cart:
        cart[pid] = qty
        session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/cart/remove", methods=["POST"])
def cart_remove():
    pid = request.form.get("pid")
    cart = session.get("cart", {})
    if pid in cart:
        cart.pop(pid)
        session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items, total = cart_items()
    if request.method == "GET":
        if not items:
            flash("Your cart is empty.", "warning")
            return redirect(url_for("home"))
        return render_template("checkout.html", items=items, total=total)

    # POST - payment
    full_name = request.form.get("full_name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    address = request.form.get("address", "").strip()
    payment_method = request.form.get("payment_method", "Cash")
    card_number = request.form.get("card_number", "").strip()

    if not (full_name and phone and address):
        flash("Please fill all required fields.", "danger")
        return redirect(url_for("checkout"))

    order_id = f"ORD{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # Send Telegram
    lines = [f"🧾 Nova Shirt - New Order {order_id}",
             f"👤 {full_name} | 📞 {phone}",
             f"📦 Items:"]
    for it in items:
        lines.append(f" - {it['qty']} × {it['product']['name']} (${it['product']['price']:.2f})")
    lines.append(f"💳 Pay: {payment_method}")
    if card_number:
        safe = '****' + card_number[-4:]
        lines.append(f"Card: {safe}")
    lines.append(f"💰 Total: ${total:.2f}")
    send_telegram_message("\n".join(lines))

    # Optional email invoice
    try:
        if app.config.get("MAIL_USERNAME") and email:
            html = render_template("invoice.html", order={
                "id": order_id,
                "full_name": full_name,
                "phone": phone,
                "email": email,
                "address": address,
                "items": items,
                "total": total,
                "payment_method": payment_method
            })
            msg = Message(subject=f"Invoice {order_id}", recipients=[email], html=html)
            mail.send(msg)
    except Exception as e:
        print("Email error:", e)

    # Clear cart
    session["cart"] = {}
    return render_template("success.html", order_id=order_id, total=total)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
