from flask import Flask, abort, render_template, redirect, url_for, flash, request, session
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
from flask_bootstrap import Bootstrap5
from sqlalchemy import and_, func, distinct
import stripe
import datetime
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///onlineshop.db'
db = SQLAlchemy()
db.init_app(app)

Bootstrap5(app)

stripe.api_key = 'api_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    cart = db.relationship('UserCart', backref='user', lazy=True)
    order = db.relationship('Orders', backref='user', lazy=True)

class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True)
    product_category = db.Column(db.String(100), nullable=False, unique=True)
    product_category_img_url = db.Column(db.String(250), nullable=False)
    product = db.relationship('Products', backref='product_category', lazy=True)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(250), nullable=False, unique=True)
    product_img_url = db.Column(db.String(250), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    product_original_price = db.Column(db.Float, nullable=False)
    product_model_number = db.Column(db.String(100), nullable=False)
    product_condition = db.Column(db.String(100), nullable=False)
    product_sold = db.Column(db.Integer, nullable=False)
    product_category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'), nullable=False)
    cart = db.relationship('UserCart', backref='product', lazy=True)
    order = db.relationship('Orders', backref='product', lazy=True)

class UserCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_time = db.Column(db.DateTime, nullable=False)
    order_id = db.Column(db.BigInteger, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

with app.app_context():
    db.create_all()

# with app.app_context():
#     product_category = [
#         {"product_category": 'Office',
#          "product_category_img_url": 'https://cdnimg.webstaurantstore.com/uploads/seo_category/2022/10/office-supplies.jpg'
#          },
#         {
#          "product_category": 'Home & Kitchen',
#          "product_category_img_url": 'https://assets.epicurious.com/photos/61b9271ce68653249bcfbfbf/4:3/w_4053,h_3039,c_limit/UtensilCrocks_HERO_120621_24372_V1_final.jpg'
#          },
#         {
#          "product_category": 'Sports & Outdoors',
#             "product_category_img_url": 'https://theabingtonian.com/wp-content/uploads/2022/10/sport.jpg'
#         },
#
#         {
#          "product_category": 'Household',
#             "product_category_img_url": 'https://www.extermpro.com/wp-content/uploads/2022/09/assorted-cleaning-products-stockpack-adobe-stock-scaled.jpg'
#         }
#     ]
#     db.session.bulk_insert_mappings(ProductCategory, product_category)
#     db.session.commit()
#
# with app.app_context():
#     products = [
#         {"product_name": 'Kodak instant photo printer',
#          "product_img_url": 'https://m.media-amazon.com/images/I/812iB2fa4rL.__AC_SX300_SY300_QL70_FMwebp_.jpg',
#          "product_price": 4,
#          "product_original_price": 130,
#          "product_model_number": '38289293874',
#          "product_condition": 'brand new',
#          "product_category_id": 1,
#          "product_sold": 0
#          },
#         {"product_name": 'Dyson V8 Plus Cordless Vacuum, Silver/Nickel',
#          "product_img_url": 'https://m.media-amazon.com/images/I/61eObiB7spL._AC_SX679_.jpg',
#          "product_price": 20,
#          "product_original_price": 300,
#          "product_model_number": '885609034461',
#          "product_condition": '50% new',
#          "product_category_id": 2,
#          "product_sold": 0
#          },
#         {"product_name": 'Amazon Basics Neoprene Dumbbell Hand Weights',
#          "product_img_url": 'https://m.media-amazon.com/images/I/81Y26toqdTL._AC_SX679_.jpg',
#          "product_price": 3,
#          "product_original_price": 20,
#          "product_model_number": 'B01LR5S6HK',
#          "product_condition": '80% new',
#          "product_category_id": 3,
#          "product_sold": 0
#          },
#
#         {"product_name": 'Duracell Rechargeable AA Batteries',
#          "product_img_url": 'https://m.media-amazon.com/images/I/71WJPs2yZAL._AC_SX466_.jpg',
#          "product_price": 5,
#          "product_original_price": 40,
#          "product_model_number": 'B0BJYNCZ3G',
#          "product_condition": 'brand new',
#          "product_category_id": 4,
#          "product_sold": 0
#          },
#         {"product_name": 'Scotch Magic Tape, Invisible',
#          "product_img_url": 'https://m.media-amazon.com/images/I/71UHFqshIPL._AC_SL1500_.jpg',
#          "product_price": 1,
#          "product_original_price": 14,
#          "product_model_number": '021200594816',
#          "product_condition": '50% new',
#          "product_category_id": 1,
#          "product_sold": 0
#          }
#     ]
#     db.session.bulk_insert_mappings(Products, products)
#     db.session.commit()

def display_as_integer_if_rounded(num):
    if num == round(num):
        return int(num)
    else:
        return num

@app.route('/', methods = ['POST', 'GET'])
def home():
    products = db.session.execute(db.select(Products)).scalars().all()
    product_category = db.session.execute(db.select(ProductCategory)).scalars().all()
    for p in products:
        p.product_price = display_as_integer_if_rounded(p.product_price)
    if request.args.get('id') == None:
        product_in_cart_id = None
        return render_template("index.html", products=products, product_category=product_category,
                               product_in_cart_id=product_in_cart_id)
    else:
        product_in_cart_id = int(request.args.get('id'))
        return render_template("index.html", products=products, product_category=product_category,
                               product_in_cart_id=product_in_cart_id), {"Refresh": "3; url=/"}



@app.route('/product/<int:id>', methods = ['POST', 'GET'])
def product(id):
    product_category = db.session.execute(db.select(ProductCategory)).scalars().all()
    product = db.session.execute(db.select(Products).where(Products.id == id)).scalar()
    product.product_condition = product.product_condition.capitalize()
    product.product_price = display_as_integer_if_rounded(product.product_price)
    product.product_original_price = display_as_integer_if_rounded(product.product_original_price)
    return render_template("product_details.html", product= product, product_category=product_category)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    product_category = db.session.execute(db.select(ProductCategory)).scalars().all()
    form = RegisterForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if not user:
            hash_password = generate_password_hash(form.password.data)
            new_user = User(
                email=form.email.data,
                password=hash_password
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('You have successfully logged in.')
            return redirect(url_for('home'))
        else:
            flash('You have registered with this email. Please log in instead.')
            return redirect(url_for('login'))
    return render_template('register.html', form = form, product_category=product_category )

@app.route('/login', methods = ['GET', 'POST'])
def login():
    product_category = db.session.execute(db.select(ProductCategory)).scalars().all()
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Wrong password. Please try again.')
                return redirect(url_for('login'))
        else:
            flash('You have not registered with this email. Please register first.')
            return redirect(url_for('register'))
    return render_template('login.html', form = form, product_category = product_category)


@app.route('/add_to_cart', methods = ['POST', 'GET'])
def add_to_cart():
    product_category = db.session.execute(db.select(ProductCategory)).scalars().all()
    if current_user.is_authenticated:
        if request.method == 'POST':
            item_status = db.session.execute(
                db.select(UserCart).where(and_(UserCart.product_id == request.args.get('id'), UserCart.user_id == current_user.id))).scalar()
            if not item_status:
                item_to_cart = UserCart(
                    product_id = request.args.get('id'),
                    user_id = current_user.id
                )
                db.session.add(item_to_cart)
                db.session.commit()
            else:
                if request.referrer == 'http://127.0.0.1:5000/':
                    flash("This item is already in your cart. We have only 1 available for each item.")
                    return redirect(url_for('home', id = request.args.get('id')))
                else:
                    flash("This item is already in your cart. We have only 1 available for each item.")
                    return redirect(request.referrer )
        all_in_cart = db.session.execute(db.select(UserCart).where(UserCart.user_id == current_user.id)).scalars().all()
        count = len(all_in_cart)
        return render_template("cart.html", all_in_cart = all_in_cart, count = count, product_category= product_category)
    else:
        return redirect(url_for('login'))


@app.route('/remove_from_cart', methods = ['POST', 'GET'])
def remove_from_cart():
    item_id = request.args.get('item_id')
    item_remove = db.session.execute(db.select(UserCart).where(UserCart.id == item_id)).scalar()
    db.session.delete(item_remove)
    db.session.commit()
    return redirect(url_for('add_to_cart'))

@app.route('/logout')
@login_required
def logout():
    session.pop('_flashes', None)
    logout_user()
    return redirect(url_for('home'))

@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    all_in_cart = db.session.execute(db.select(UserCart).where(UserCart.user_id == current_user.id)).scalars().all()
    items = []
    for item in all_in_cart:
        item_detail = {
            'price_data': {
                'product_data': {
                    'name': item.product.product_name,
                },
                'unit_amount': int(item.product.product_price*100),
                'currency': 'usd',
            },
            'quantity': 1,
        }
        items.append(item_detail)

    checkout_session = stripe.checkout.Session.create(
        line_items=items,
        payment_method_types=['card'],
        mode='payment',
        success_url=request.host_url + 'checkout/success',
        cancel_url=request.host_url + 'checkout/cancel',
    )
    return redirect(checkout_session.url)

@app.route('/checkout/success')
def success():
    product_category = db.session.execute(db.select(ProductCategory)).scalars().all()
    all_in_cart = db.session.execute(db.select(UserCart).where(UserCart.user_id == current_user.id)).scalars().all()
    distinct_order_count = db.session.query(func.count(distinct(Orders.order_id))).scalar()
    time = datetime.datetime.now()
    for item in all_in_cart:
        new_order = Orders(
            order_time=time,
            order_id=distinct_order_count + 1,
            user_id=current_user.id,
            product_id=item.product_id
        )
        db.session.add(new_order)
        db.session.commit()
        UserCart.query.filter(UserCart.id == item.id).delete()
        db.session.commit()
        product = db.session.execute(db.select(Products).where(Products.id == item.product_id)).scalar()
        product.product_sold = 1
        db.session.commit()
    return render_template('success.html', product_category=product_category)

@app.route('/checkout/cancel')
def cancel():
    product_category = db.session.execute(db.select(ProductCategory)).scalars().all()
    return render_template('cancel.html', product_category = product_category)

@app.route('/orders', methods=['POST', 'GET'])
def orders():
    product_category = db.session.execute(db.select(ProductCategory)).scalars().all()
    if current_user.is_authenticated:
        orders = db.session.execute(db.select(Orders).where(Orders.user_id == current_user.id)).scalars().all()
        distinct_order_id =db.session.query(Orders.order_id, Orders.order_time).filter(Orders.user_id == current_user.id).distinct().all()
    else:
        return redirect(url_for('login'))

    return render_template('orders.html', orders=orders, distinct_order_id=distinct_order_id, product_category = product_category )






if __name__ == "__main__":
    app.run()