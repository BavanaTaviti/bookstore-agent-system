from flask import Flask, render_template, request, session, redirect, url_for
import json
import threading
import webbrowser
import time
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from agents.buyer import BuyerAgent
from agents.seller import SellerAgent
from agents.trust import calculate_trust

app = Flask(__name__)
app.secret_key = "secret123"


def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000/")


# 🏠 HOME
@app.route('/')
def home():
    with open('data/books.json') as f:
        books = json.load(f)

    return render_template('index.html', books=books)


# 📘 BOOK DETAILS (UPDATED)
@app.route('/book/<title>')
def book_detail(title):
    with open('data/books.json') as f:
        books = json.load(f)

    book = next(b for b in books if b['title'] == title)

    # LOAD REVIEWS
    try:
        with open('data/reviews.json') as f:
            all_reviews = json.load(f)
    except:
        all_reviews = []

    sellers = []

    for s in book['sellers']:

        # FILTER REVIEWS PER SELLER
        seller_reviews = [
            r for r in all_reviews
            if r['title'] == title and r['seller'] == s['name']
        ]

        # AVG RATING
        if seller_reviews:
            avg_rating = sum(r['rating'] for r in seller_reviews) / len(seller_reviews)
        else:
            avg_rating = 0

        # TRUST CALCULATION
        trust = calculate_trust(s['reputation'], avg_rating)

        sellers.append({
            "name": s['name'],
            "trust": round(trust, 2),
            "reputation": s['reputation'],
            "base_price": book['base_price'],
            "avg_rating": round(avg_rating, 1),
            "reviews": seller_reviews
        })

    return render_template('book.html',
                           book=book,
                           sellers=sellers)


# ⭐ ADD REVIEW (PER SELLER)
@app.route('/add-review', methods=['POST'])
def add_review():
    title = request.form['title']
    seller = request.form['seller']
    rating = int(request.form['rating'])
    review = request.form.get('review', '').strip()

    try:
        with open('data/reviews.json') as f:
            reviews = json.load(f)
    except:
        reviews = []

    reviews.append({
        "title": title,
        "seller": seller,
        "rating": rating,
        "review": review if review else "No comment"
    })

    with open('data/reviews.json', 'w') as f:
        json.dump(reviews, f, indent=4)

    return redirect(url_for('book_detail', title=title))


# 🤝 NEGOTIATION
@app.route('/negotiate', methods=['POST'])
def negotiate():
    seller_name = request.form['seller']
    base_price = int(request.form['price'])
    reputation = float(request.form['reputation'])

    buyer = BuyerAgent()
    seller = SellerAgent(seller_name, reputation, base_price)

    rounds = []

    for i in range(5):
        buyer_offer = buyer.make_offer(seller.current_price)
        seller_price = seller.negotiate(buyer_offer)

        rounds.append({
            "round": i + 1,
            "buyer_offer": buyer_offer,
            "seller_price": seller_price
        })

    trust = calculate_trust(reputation)
    decision = buyer.final_decision(seller_price, trust)

    return render_template('negotiation.html',
                           rounds=rounds,
                           final_price=seller_price,
                           decision=decision)


# 🛒 CART
@app.route('/add-to-cart/<title>')
def add_to_cart(title):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(title)
    session.modified = True

    return redirect(url_for('home'))


@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])

    with open('data/books.json') as f:
        books = json.load(f)

    cart_items = [b for b in books if b['title'] in cart]
    total = sum(item['base_price'] for item in cart_items)

    return render_template('cart.html',
                           items=cart_items,
                           total=total)


@app.route('/remove-from-cart/<title>')
def remove_from_cart(title):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item != title]
        session.modified = True

    return redirect(url_for('view_cart'))


# 🚀 RUN
if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app.run(debug=True)