# ⚡ QuickMart — Django Quick Commerce Platform

Full-stack quick commerce platform (like Blinkit/Zepto) built with Django + HTML/CSS/JS.

## 🚀 Quick Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install django Pillow

# 3. Run migrations
python manage.py makemigrations users
python manage.py makemigrations store
python manage.py makemigrations cart
python manage.py makemigrations orders
python manage.py makemigrations payments
python manage.py makemigrations delivery
python manage.py migrate

# 4. Seed demo data (products, categories, admin user)
python manage.py seed_data

# 5. Run server
python manage.py runserver
```

## 🔑 Demo Credentials

| Role  | Email                  | Password |
|-------|------------------------|----------|
| Admin | admin@quickmart.com    | admin123 |
| User  | demo@quickmart.com     | demo123  |

## 📂 URLs

| Page            | URL                        |
|-----------------|----------------------------|
| Home            | http://127.0.0.1:8000/     |
| Products        | /products/                 |
| Cart            | /cart/                     |
| Checkout        | /orders/checkout/          |
| My Orders       | /orders/                   |
| Account         | /users/profile/            |
| Spin Wheel      | /users/spin/               |
| Admin Panel     | /admin-panel/              |
| Django Admin    | /django-admin/             |

## 🏗️ Project Structure

```
quickmart/
├── quickmart/          # Project settings & URLs
├── store/              # Products, categories, search
├── users/              # Auth, profiles, addresses, wishlist
├── cart/               # Shopping cart
├── orders/             # Order management & tracking
├── payments/           # Razorpay integration & refunds
├── delivery/           # Delivery tracking
├── admin_panel/        # Custom admin dashboard
├── static/             # CSS, JS, images
│   ├── css/main.css
│   └── js/main.js
└── templates/          # Base template
```

## ✨ Features

- ✅ User auth (email/password + OTP ready + Google OAuth ready)
- ✅ Product catalog with variants, images, ratings
- ✅ Category & brand filtering + search autocomplete
- ✅ Shopping cart with coupon codes
- ✅ Full checkout flow with address management
- ✅ Order tracking with status timeline
- ✅ Wishlist system
- ✅ Review & rating system
- ✅ Spin wheel gamification with coins
- ✅ Admin panel: dashboard, products CRUD, orders management
- ✅ Inventory management with low-stock alerts
- ✅ Analytics with revenue charts
- ✅ Coupon management
- ✅ Responsive design (mobile-first)

## 🖼️ Adding Real Images

Product images are loaded from Unsplash URLs in the seed data.
To use local images: upload via Admin Panel → Products → Edit → Upload Image.

## 🔧 Production Checklist

1. Set `DEBUG = False` in settings.py
2. Set `SECRET_KEY` from environment variable
3. Configure PostgreSQL instead of SQLite
4. Set `ALLOWED_HOSTS` to your domain
5. Configure Razorpay keys for real payments
6. Set up static file serving (whitenoise or nginx)
