from flask_sqlalchemy import SQLAlchemy
from slugify import slugify

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    products = db.relationship("Product", backref="category", lazy=True)

    def __init__(self, name, description=""):
        self.name = name
        self.slug = slugify(name)
        self.description = description


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Float, nullable=False, default=0.0)
    image_url = db.Column(db.String(500), default="")
    affiliate_url = db.Column(db.String(500), default="")
    is_featured = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    def __init__(self, name, description, price, image_url, affiliate_url, category, is_featured=False):
        self.name = name
        base_slug = slugify(name)
        self.slug = base_slug
        self.description = description
        self.price = price
        self.image_url = image_url
        self.affiliate_url = affiliate_url
        self.category = category
        self.is_featured = is_featured

    def ensure_unique_slug(self):
        base = slugify(self.name)
        unique_slug = base
        counter = 2
        while Product.query.filter_by(slug=unique_slug).first():
            unique_slug = f"{base}-{counter}"
            counter += 1
        self.slug = unique_slug
