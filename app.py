import os
from flask import Flask, render_template, request, redirect, url_for, abort
from models import db, Category, Product

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "change-this-secret"

    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_if_empty()

    @app.route("/")
    def index():
        q = request.args.get("q", "").strip()
        featured = Product.query.filter_by(is_featured=True).limit(8).all()
        categories = Category.query.order_by(Category.name.asc()).all()
        latest = Product.query.order_by(Product.id.desc()).limit(12).all()
        return render_template("index.html", featured=featured, categories=categories, latest=latest, q=q)

    @app.route("/search")
    def search():
        q = request.args.get("q", "").strip()
        products = []
        if q:
            like = f"%{q}%"
            products = Product.query.filter(
                (Product.name.ilike(like)) | (Product.description.ilike(like))
            ).order_by(Product.id.desc()).all()
        categories = Category.query.order_by(Category.name.asc()).all()
        return render_template("search.html", q=q, products=products, categories=categories)

    @app.route("/category/<slug>")
    def category(slug):
        cat = Category.query.filter_by(slug=slug).first_or_404()
        products = Product.query.filter_by(category=cat).order_by(Product.id.desc()).all()
        categories = Category.query.order_by(Category.name.asc()).all()
        return render_template("category.html", category=cat, products=products, categories=categories)

    @app.route("/product/<slug>")
    def product_detail(slug):
        product = Product.query.filter_by(slug=slug).first_or_404()
        categories = Category.query.order_by(Category.name.asc()).all()
        # simple "related": same category, exclude same id
        related = Product.query.filter(Product.category_id==product.category_id, Product.id != product.id).limit(6).all()
        return render_template("product_detail.html", product=product, categories=categories, related=related)

    return app

def seed_if_empty():
    if Category.query.count() > 0:
        return

    # Create categories
    electronics = Category("إلكترونيات", "هواتف، حواسيب، سماعات، وإكسسوارات.")
    fashion = Category("أزياء", "ملابس وأحذية وإكسسوارات.")
    home = Category("منزل ومطبخ", "أدوات منزلية ومطبخ.")
    beauty = Category("جمال وعناية", "مستحضرات العناية الشخصية.")
    sports = Category("رياضة", "معدات وأدوات رياضية.")
    db.session.add_all([electronics, fashion, home, beauty, sports])
    db.session.commit()

    # Helper to add product
    def add_prod(name, desc, price, img, url, cat, feat=False):
        p = Product(name, desc, price, img, url, cat, feat)
        db.session.add(p)
        db.session.flush()  # get id
        p.ensure_unique_slug()
        db.session.add(p)
        return p

    # Sample products (you can replace affiliate_url with your own referral links)
    add_prod(
        "هاتف ذكي 6.5\" 128GB 5G",
        "هاتف قوي بشاشة كبيرة، بطارية 5000mAh وكاميرا ثلاثية.",
        299.99,
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=1200&auto=format&fit=crop",
        "https://example.com/aff/phone",
        electronics,
        True
    )
    add_prod(
        "سماعات لاسلكية عزل ضجيج",
        "صوت نقي مع ميكروفون مدمج وشحن سريع.",
        89.90,
        "https://images.unsplash.com/photo-1518443895914-9ef6d8d3f1a5?q=80&w=1200&auto=format&fit=crop",
        "https://example.com/aff/earbuds",
        electronics,
        True
    )
    add_prod(
        "حاسوب محمول 15\" i7",
        "حاسوب للأعمال والدراسة مع SSD سريع وذاكرة 16GB.",
        999.00,
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=1200&auto=format&fit=crop",
        "https://example.com/aff/laptop",
        electronics
    )
    add_prod(
        "حذاء رياضي خفيف",
        "مريح للجري والمشي اليومي، تهوية ممتازة.",
        55.00,
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1200&auto=format&fit=crop",
        "https://example.com/aff/shoes",
        fashion,
        True
    )
    add_prod(
        "آلة صنع القهوة المنزلية",
        "تحضير القهوة بضغطة زر مع فلتر قابل لإعادة الاستخدام.",
        120.00,
        "https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?q=80&w=1200&auto=format&fit=crop",
        "https://example.com/aff/coffee",
        home
    )
    add_prod(
        "مقلاة هوائية 5 لتر",
        "طهي صحي بأقل زيت، تحكم رقمي وبرامج جاهزة.",
        149.00,
        "https://images.unsplash.com/photo-1603048297172-c92544798b66?q=80&w=1200&auto=format&fit=crop",
        "https://example.com/aff/airfryer",
        home,
        True
    )
    add_prod(
        "مجفف شعر احترافي",
        "تقنية أيونية لتقليل التجعد، درجات حرارة متعددة.",
        39.99,
        "https://images.unsplash.com/photo-1596464716121-f8b9257eaf0b?q=80&w=1200&auto=format&fit=crop",
        "https://example.com/aff/hairdryer",
        beauty
    )
    add_prod(
        "ساعة ذكية مقاومة للماء",
        "تتبع معدل ضربات القلب، الخطوات، والنوم، إشعارات الهاتف.",
        69.00,
        "https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?q=80&w=1200&auto=format&fit=crop",
        "https://example.com/aff/smartwatch",
        electronics
    )
    add_prod(
        "دمبلز قابلة للتعديل 20كغ",
        "مجموعة تدريب منزلية لتقوية العضلات بمساحة صغيرة.",
        89.00,
        "https://images.unsplash.com/photo-1583454155181-c5f6c7f4b366?q=80&w=1200&auto=format&fit=crop",
        "https://example.com/aff/dumbbells",
        sports
    )
    add_prod(
        "خلاط يدوي متعدد السرعات",
        "تصميم مريح مع شفرات فولاذ مقاوم للصدأ.",
        24.50,
        "https://images.unsplash.com/photo-1586201375761-83865001e31b?q=80&w=1200&auto=format&fit=crop",
        "https://example.com/aff/handblender",
        home
    )

    db.session.commit()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
open(os.path.join(project_root, "app.py"), "w").write(app_py.strip()+"\n")
