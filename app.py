from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # В реальном проекте используйте надежный ключ
app.json.ensure_ascii = False  # <-- this line saves the day
app.json.mimetype = "application/json; charset=utf-8"  # <-- this could be also useful

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Модели данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    carts = db.relationship('Cart', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade="all, delete-orphan")

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product')

# API Endpoints

# Аутентификация
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400
    
    user = User(username=data['username'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    
    cart = Cart(user_id=user.id)
    db.session.add(cart)
    db.session.commit()
    
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token), 200

# Товары
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'quantity': p.quantity,
        'category': p.category
    } for p in products], )
# Корзина
@app.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    current_user =int(get_jwt_identity())
    cart = Cart.query.filter_by(user_id=current_user).first()
    
    items = [{
        'id': item.id,
        'product_id': item.product_id,
        'name': item.product.name,
        'price': item.product.price,
        'quantity': item.quantity,
        'subtotal': item.product.price * item.quantity
    } for item in cart.items]
    
    total = sum(item['subtotal'] for item in items)
    return jsonify({'items': items, 'total': total})

@app.route('/cart/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    print('123')
    current_user = int(get_jwt_identity())
    data = request.get_json()
    print(data)
    cart = Cart.query.filter_by(user_id=current_user).first()
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({"message": "Product not found"}), 404
        
    existing_item = next((item for item in cart.items if item.product_id == product.id), None)
    
    if existing_item:
        existing_item.quantity += data.get('quantity', 1)
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=data.get('quantity', 1)
        )
        db.session.add(new_item)
    
    db.session.commit()
    return jsonify({"message": "Item added to cart"}), 200

@app.route('/cart/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    current_user = int(get_jwt_identity())
    cart = Cart.query.filter_by(user_id=current_user).first()
    print(f"item_id: {item_id}")
    item = next((item for item in cart.items if item.id == item_id), None)
    if not item:
        return jsonify({"message": "Item not found in cart"}), 404
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed from cart"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)