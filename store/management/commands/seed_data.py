from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **kwargs):
        from store.models import Category, Brand, Product, ProductVariant, Banner, Coupon
        from users.models import User

        self.stdout.write('Seeding data...')

        # Categories
        cats_data = [
            ('Dairy & Eggs','dairy-eggs','🥛',1),
            ('Fruits','fruits','🍎',2),
            ('Vegetables','vegetables','🥦',3),
            ('Snacks','snacks','🍿',4),
            ('Beverages','beverages','🥤',5),
            ('Bread & Bakery','bread-bakery','🍞',6),
            ('Personal Care','personal-care','🧴',7),
            ('Cleaning','cleaning','🧹',8),
            ('Frozen Foods','frozen-foods','🧊',9),
            ('Baby Care','baby-care','👶',10),
            ('Pet Care','pet-care','🐾',11),
            ('Medicines','medicines','💊',12),
        ]
        cats = {}
        for name, slug, icon, order in cats_data:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name':name,'icon':icon,'sort_order':order,'is_active':True})
            cats[slug] = cat
        self.stdout.write('  ✓ Categories')

        # Brands
        brands_data = ['Amul','Britannia','Nestle','HUL','P&G','Dabur','Parle','ITC','Epigamia','Farm Fresh']
        brands = {}
        for b in brands_data:
            from django.utils.text import slugify
            brand, _ = Brand.objects.get_or_create(slug=slugify(b), defaults={'name':b,'is_active':True})
            brands[b] = brand
        self.stdout.write('  ✓ Brands')

        # Products
        products_data = [
            ('Amul Full Cream Milk','amul-full-cream-milk','dairy-eggs','Amul',
             'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400',
             [(  '500ml',32,36,200),('1 Liter',62,68,150),('2 Liter',120,135,80)],True,True),
            ('Farm Fresh Eggs','farm-fresh-eggs','dairy-eggs','Farm Fresh',
             'https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=400',
             [('6 pcs',48,55,180),('12 pcs',89,99,120),('30 pcs',220,250,60)],True,False),
            ('Amul Butter Salted','amul-butter-salted','dairy-eggs','Amul',
             'https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=400',
             [('100g',55,60,200),('500g',265,290,80)],True,False),
            ('Britannia Brown Bread','britannia-brown-bread','bread-bakery','Britannia',
             'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400',
             [('400g',45,52,300),('750g',82,95,150)],False,False),
            ('Shimla Apple Premium','shimla-apple-premium','fruits','Farm Fresh',
             'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400',
             [('500g',75,90,200),('1 kg',149,179,100)],True,True),
            ('Robusta Bananas','robusta-bananas','fruits','Farm Fresh',
             'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400',
             [('6 pcs',35,45,300),('1 kg',49,59,200)],True,False),
            ('Fresh Tomatoes','fresh-tomatoes','vegetables','Farm Fresh',
             'https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400',
             [('500g',29,39,400),('1 kg',55,75,200)],False,False),
            ('Baby Spinach Leaves','baby-spinach','vegetables','Farm Fresh',
             'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400',
             [('200g',45,60,150)],True,True),
            ("Lays Classic Salted",'lays-classic','snacks','ITC',
             'https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400',
             [('52g',20,20,500),('164g',60,60,300)],False,True),
            ('Oreo Original','oreo-original','snacks','Britannia',
             'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400',
             [('120g',30,35,400),('300g',72,82,200)],False,True),
            ('Bisleri Water','bisleri-water','beverages','Farm Fresh',
             'https://images.unsplash.com/photo-1559839914-17aae19cec71?w=400',
             [('500ml',15,15,600),('1 Liter',20,20,400)],False,False),
            ('Real Mango Juice','real-mango-juice','beverages','Dabur',
             'https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400',
             [('200ml',25,30,300),('1 Liter',70,85,150)],True,True),
            ('Amul Paneer','amul-paneer','dairy-eggs','Amul',
             'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400',
             [('200g',85,95,150),('500g',200,230,80)],True,False),
            ('Epigamia Greek Yogurt','epigamia-greek-yogurt','dairy-eggs','Epigamia',
             'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400',
             [('90g',30,35,200),('400g',99,115,100)],True,True),
            ('Dove Beauty Bar Soap','dove-beauty-bar','personal-care','HUL',
             'https://images.unsplash.com/photo-1607006344380-b6775a0824a7?w=400',
             [('100g',48,56,300),('Pack of 3',135,165,150)],False,False),
            ('Surf Excel Matic','surf-excel-matic','cleaning','HUL',
             'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400',
             [('500g',150,175,200),('1 kg',280,320,100)],False,False),
            ('Quaker Oats','quaker-oats','snacks','Parle',
             'https://images.unsplash.com/photo-1495214783159-3503fd1b572d?w=400',
             [('500g',115,140,200),('1 kg',215,260,100)],False,False),
            ('Dabur Honey','dabur-honey','snacks','Dabur',
             'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400',
             [('250g',90,110,150),('500g',179,220,80)],False,True),
            ('Nestle Munch','nestle-munch','snacks','Nestle',
             'https://images.unsplash.com/photo-1606312619070-d48b4c652a52?w=400',
             [('Single',10,10,800),('Pack of 5',48,50,400)],False,True),
            ('Amul Dahi Curd','amul-dahi','dairy-eggs','Amul',
             'https://images.unsplash.com/photo-1571047406947-a7c12b3d4e3d?w=400',
             [('200g',28,32,300),('400g',54,60,200)],False,False),
        ]

        import uuid as _uuid
        from django.utils.text import slugify
        for name, slug, cat_slug, brand_name, img_url, variants, featured, flash in products_data:
            cat = cats.get(cat_slug)
            brand = brands.get(brand_name)
            if not cat: continue
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name, 'category': cat, 'brand': brand,
                    'image_url': img_url, 'is_active': True,
                    'is_featured': featured, 'is_flash_sale': flash,
                    'sku': 'SKU-' + slug[:15].upper().replace('-',''),
                    'average_rating': 4.5, 'total_reviews': 120, 'total_sold': 500,
                }
            )
            if created:
                for i, (vname, price, mrp, stock) in enumerate(variants):
                    ProductVariant.objects.create(
                        product=product, name=vname,
                        sku=f"{product.sku}-{i+1}",
                        price=price, mrp=mrp, stock=stock, is_active=True
                    )
        self.stdout.write('  ✓ Products')

        # Banners
        Banner.objects.get_or_create(title='Flat 40% OFF',defaults={'subtitle':'On your first order','emoji':'🛒','link_url':'/products/','button_text':'Shop Now','bg_color':'linear-gradient(135deg,#1a1a2e,#16213e)','sort_order':1,'is_active':True})
        Banner.objects.get_or_create(title='Farm Fresh Veggies',defaults={'subtitle':'Organic & pesticide-free','emoji':'🥦','link_url':'/category/vegetables/','button_text':'Explore','bg_color':'linear-gradient(135deg,#2d6a4f,#1b4332)','sort_order':2,'is_active':True})
        Banner.objects.get_or_create(title='Dairy Delivered',defaults={'subtitle':'Fresh every morning','emoji':'🥛','link_url':'/category/dairy-eggs/','button_text':'Subscribe','bg_color':'linear-gradient(135deg,#7b2d8b,#4a1942)','sort_order':3,'is_active':True})
        self.stdout.write('  ✓ Banners')

        # Coupons
        now = timezone.now()
        Coupon.objects.get_or_create(code='FIRST40',defaults={'description':'40% off first order','discount_type':'percentage','discount_value':40,'max_discount':100,'min_order_amount':0,'valid_from':now,'valid_until':now+timedelta(days=365),'is_active':True})
        Coupon.objects.get_or_create(code='SAVE20',defaults={'description':'₹20 off on ₹199+','discount_type':'flat','discount_value':20,'min_order_amount':199,'valid_from':now,'valid_until':now+timedelta(days=90),'is_active':True})
        Coupon.objects.get_or_create(code='QMART',defaults={'description':'10% off sitewide','discount_type':'percentage','discount_value':10,'max_discount':50,'min_order_amount':99,'valid_from':now,'valid_until':now+timedelta(days=180),'is_active':True})
        self.stdout.write('  ✓ Coupons')

        # Admin user
        if not User.objects.filter(email='admin@quickmart.com').exists():
            User.objects.create_superuser(email='admin@quickmart.com', password='admin123', full_name='Admin User')
            self.stdout.write('  ✓ Admin user: admin@quickmart.com / admin123')

        # Demo user
        if not User.objects.filter(email='demo@quickmart.com').exists():
            u = User.objects.create_user(email='demo@quickmart.com', password='demo123', full_name='Rohan Sharma', phone='+91 98765 43210')
            from users.models import Address
            Address.objects.create(user=u, label='home', full_name='Rohan Sharma', phone='+91 98765 43210',
                address_line1='B-12, Civil Lines', city='Nagpur', state='Maharashtra', pincode='440001', is_default=True)
            self.stdout.write('  ✓ Demo user: demo@quickmart.com / demo123')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write('\nAdmin: admin@quickmart.com / admin123')
        self.stdout.write('Demo:  demo@quickmart.com / demo123')
        self.stdout.write('\nRun: python manage.py runserver')
