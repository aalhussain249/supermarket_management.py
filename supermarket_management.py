"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Super Market Management System                            ║
║                        نظام إدارة السوبر ماركت                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

المميزات:
- إدارة المنتجات (إضافة، تعديل، حذف، بحث)
- إدارة المخزون
- نقطة البيع (POS)
- إدارة المبيعات والفواتير
- إدارة الموردين والعملاء
- التقارير (مبيعات، مخزون، أرباح)
- إدارة المستخدمين والصلاحيات
- النسخ الاحتياطي
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from datetime import datetime, date
import shutil
from tkinter import filedialog

# ═══════════════════════════════════════════════════════════════════════════════
# قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════

class Database:
    def __init__(self, db_file="supermarket.db"):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'cashier',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP)""",
            """CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT)""",
            """CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                company TEXT)""",
            """CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                name TEXT NOT NULL,
                category_id INTEGER,
                purchase_price REAL DEFAULT 0,
                sale_price REAL DEFAULT 0,
                quantity INTEGER DEFAULT 0,
                min_quantity INTEGER DEFAULT 5,
                unit TEXT DEFAULT 'piece',
                expiry_date TEXT,
                supplier_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP)""",
            """CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                total REAL DEFAULT 0,
                discount REAL DEFAULT 0,
                final_total REAL DEFAULT 0,
                payment_method TEXT DEFAULT 'cash',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP)""",
            """CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                unit_price REAL,
                total_price REAL)""",
            """CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                credit REAL DEFAULT 0)"""
        ]
        for table in tables:
            self.cursor.execute(table)

        # بيانات افتراضية
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(
                "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                ('admin', 'admin123', 'المدير', 'admin'))

        self.cursor.execute("SELECT COUNT(*) FROM categories")
        if self.cursor.fetchone()[0] == 0:
            cats = [
                ('مأكولات', 'الأطعمة والمأكولات'),
                ('مشروبات', 'المشروبات الغازية والعصائر'),
                ('منظفات', 'مواد التنظيف المنزلية'),
                ('عناية شخصية', 'العناية بالجسم والشعر'),
                ('إلكترونيات', 'الأجهزة الإلكترونية الصغيرة'),
                ('مستلزمات منزلية', 'أدوات المنزل')
            ]
            self.cursor.executemany(
                'INSERT INTO categories (name, description) VALUES (?, ?)', cats)

        self.conn.commit()

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor

    def fetchall(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetchone(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# نافذة تسجيل الدخول
# ═══════════════════════════════════════════════════════════════════════════════

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Super Market - تسجيل الدخول")
        self.root.geometry("450x420")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a2e')
        self.db = Database()
        self.current_user = None
        self.setup_ui()
        self.center_window()

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    def setup_ui(self):
        tk.Label(self.root, text="🛒", font=('Segoe UI', 48),
                bg='#1a1a2e', fg='white').pack(pady=(30, 0))
        tk.Label(self.root, text="Super Market", font=('Segoe UI', 24, 'bold'),
                bg='#1a1a2e', fg='#e94560').pack()
        tk.Label(self.root, text="نظام إدارة السوبر ماركت", font=('Segoe UI', 14),
                bg='#1a1a2e', fg='#aaa').pack(pady=(0, 20))

        form = tk.Frame(self.root, bg='#1a1a2e')
        form.pack(padx=50, fill='x')

        tk.Label(form, text="👤 اسم المستخدم", font=('Segoe UI', 11),
                bg='#1a1a2e', fg='white').pack(anchor='e')
        self.username_entry = tk.Entry(form, font=('Segoe UI', 12), bg='#16213e',
                                       fg='white', insertbackground='white',
                                       relief='flat', justify='right')
        self.username_entry.pack(fill='x', pady=(5, 15), ipady=8)

        tk.Label(form, text="🔒 كلمة المرور", font=('Segoe UI', 11),
                bg='#1a1a2e', fg='white').pack(anchor='e')
        self.password_entry = tk.Entry(form, font=('Segoe UI', 12), show='●',
                                       bg='#16213e', fg='white',
                                       insertbackground='white', relief='flat',
                                       justify='right')
        self.password_entry.pack(fill='x', pady=(5, 20), ipady=8)
        self.password_entry.bind('<Return>', lambda e: self.login())

        tk.Button(form, text="تسجيل الدخول", font=('Segoe UI', 13, 'bold'),
                 bg='#e94560', fg='white', relief='flat', cursor='hand2',
                 command=self.login, pady=8).pack(fill='x', pady=10)

        tk.Label(self.root,
                text="اسم المستخدم: admin | كلمة المرور: admin123",
                font=('Segoe UI', 9), bg='#1a1a2e', fg='#666').pack(pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("تنبيه", "الرجاء إدخال اسم المستخدم وكلمة المرور")
            return

        user = self.db.fetchone(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password))

        if user:
            self.current_user = dict(user)
            self.root.destroy()
            main_root = tk.Tk()
            MainApp(main_root, self.current_user, self.db)
            main_root.mainloop()
        else:
            messagebox.showerror("خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة!")


# ═══════════════════════════════════════════════════════════════════════════════
# التطبيق الرئيسي
# ═══════════════════════════════════════════════════════════════════════════════

class MainApp:
    def __init__(self, root, user, db):
        self.root = root
        self.user = user
        self.db = db
        self.root.title(f"Super Market - {user['full_name']}")
        self.root.geometry("1400x800")
        self.root.configure(bg='#0f0f23')
        self.root.state('zoomed')
        self.invoice_items = []
        self.setup_ui()
        self.show_dashboard()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#0f0f23')
        main_frame.pack(fill='both', expand=True)

        # الشريط الجانبي
        sidebar = tk.Frame(main_frame, bg='#1a1a2e', width=260)
        sidebar.pack(side='right', fill='y')
        sidebar.pack_propagate(False)

        # الشعار
        tk.Label(sidebar, text="🛒", font=('Segoe UI', 40),
                bg='#1a1a2e', fg='#e94560').pack(pady=(20, 0))
        tk.Label(sidebar, text="Super Market", font=('Segoe UI', 16, 'bold'),
                bg='#1a1a2e', fg='white').pack()

        # معلومات المستخدم
        user_frame = tk.Frame(sidebar, bg='#16213e', padx=15, pady=10)
        user_frame.pack(fill='x', padx=15, pady=15)
        tk.Label(user_frame, text=f"👤 {self.user['full_name']}",
                font=('Segoe UI', 11, 'bold'), bg='#16213e', fg='white').pack(anchor='e')
        tk.Label(user_frame,
                text=f"الصلاحية: {self.get_role_name(self.user['role'])}",
                font=('Segoe UI', 9), bg='#16213e', fg='#aaa').pack(anchor='e')

        # القائمة
        menu_items = [
            ("📊", "لوحة التحكم", self.show_dashboard),
            ("📦", "المنتجات", self.show_products),
            ("🛍️", "نقطة البيع", self.show_pos),
            ("📋", "المبيعات", self.show_sales),
            ("🏭", "الموردين", self.show_suppliers),
            ("👥", "العملاء", self.show_customers),
            ("📈", "التقارير", self.show_reports),
        ]
        if self.user['role'] == 'admin':
            menu_items.append(("👨‍💼", "المستخدمين", self.show_users))
        menu_items.append(("⚙️", "الإعدادات", self.show_settings))

        self.menu_buttons = []
        for icon, text, cmd in menu_items:
            btn = tk.Button(sidebar, text=f"{icon}  {text}", font=('Segoe UI', 12),
                           bg='#1a1a2e', fg='#aaa', relief='flat', anchor='e',
                           cursor='hand2',
                           command=lambda c=cmd, t=text: self.switch_tab(c, t))
            btn.pack(fill='x', padx=10, pady=2, ipady=10)
            self.menu_buttons.append((btn, text))

        tk.Button(sidebar, text="🚪  خروج", font=('Segoe UI', 12),
                 bg='#e94560', fg='white', relief='flat', anchor='e',
                 cursor='hand2', command=self.logout,
                 pady=10).pack(fill='x', padx=10, pady=20, side='bottom')

        self.content_frame = tk.Frame(main_frame, bg='#0f0f23')
        self.content_frame.pack(side='left', fill='both', expand=True,
                               padx=20, pady=20)

    def get_role_name(self, role):
        roles = {'admin': 'مدير', 'manager': 'مدير فرع', 'cashier': 'كاشير'}
        return roles.get(role, role)

    def switch_tab(self, command, tab_name):
        for btn, name in self.menu_buttons:
            if name == tab_name:
                btn.config(bg='#e94560', fg='white')
            else:
                btn.config(bg='#1a1a2e', fg='#aaa')
        for w in self.content_frame.winfo_children():
            w.destroy()
        command()

    def logout(self):
        if messagebox.askyesno("تأكيد", "هل تريد الخروج من النظام؟"):
            self.root.destroy()
            root = tk.Tk()
            LoginWindow(root)
            root.mainloop()

    def create_header(self, title):
        header = tk.Frame(self.content_frame, bg='#0f0f23')
        header.pack(fill='x', pady=(0, 20))
        tk.Label(header, text=title, font=('Segoe UI', 24, 'bold'),
                bg='#0f0f23', fg='white').pack(anchor='e')
        return header

    def create_tree(self, columns, headings, widths):
        tree = ttk.Treeview(self.content_frame, columns=columns,
                           show='headings', height=20)
        for col, head, width in zip(columns, headings, widths):
            tree.heading(col, text=head)
            tree.column(col, width=width,
                       anchor='center' if width < 200 else 'e')

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview", background="#1a1a2e", foreground="white",
                       fieldbackground="#1a1a2e", rowheight=30)
        style.configure("Treeview.Heading", background="#16213e",
                       foreground="white", font=('Segoe UI', 11, 'bold'))
        style.map("Treeview", background=[('selected', '#e94560')])

        sb = ttk.Scrollbar(self.content_frame, orient='vertical',
                          command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side='right', fill='both', expand=True)
        sb.pack(side='left', fill='y')
        return tree

    # ═══════════════════════════════════════════════════════════════════════════
    # لوحة التحكم
    # ═══════════════════════════════════════════════════════════════════════════

    def show_dashboard(self):
        self.create_header("📊 لوحة التحكم")
        tk.Label(self.content_frame,
                text=f"تاريخ اليوم: {datetime.now().strftime('%Y-%m-%d')}",
                font=('Segoe UI', 11), bg='#0f0f23', fg='#aaa').pack(anchor='e')

        cards_frame = tk.Frame(self.content_frame, bg='#0f0f23')
        cards_frame.pack(fill='x', pady=20)

        stats = self.get_dashboard_stats()
        cards = [
            ("📦 المنتجات", stats['products'], "#3498db", "إجمالي المنتجات"),
            ("💰 المبيعات اليوم", f"{stats['today_sales']:.2f} ر.س",
             "#2ecc71", "مبيعات اليوم"),
            ("📋 الفواتير", stats['today_invoices'],
             "#e74c3c", "فواتير اليوم"),
            ("⚠️ منخفض المخزن", stats['low_stock'],
             "#f39c12", "يحتاج تعبئة"),
        ]

        for icon, value, color, desc in cards:
            card = tk.Frame(cards_frame, bg='#1a1a2e', padx=20, pady=20,
                           highlightbackground=color, highlightthickness=2)
            card.pack(side='right', padx=10, fill='both', expand=True)
            tk.Label(card, text=icon, font=('Segoe UI', 28),
                    bg='#1a1a2e', fg=color).pack(anchor='e')
            tk.Label(card, text=str(value), font=('Segoe UI', 28, 'bold'),
                    bg='#1a1a2e', fg='white').pack(anchor='e')
            tk.Label(card, text=desc, font=('Segoe UI', 10),
                    bg='#1a1a2e', fg='#aaa').pack(anchor='e')

        # المنتجات منخفضة المخزون
        tk.Label(self.content_frame, text="⚠️ منتجات منخفضة المخزون",
                font=('Segoe UI', 16, 'bold'),
                bg='#0f0f23', fg='#f39c12').pack(anchor='e', pady=(20, 10))

        tree = self.create_tree(
            ('name', 'qty', 'min', 'status'),
            ['اسم المنتج', 'الكمية', 'الحد الأدنى', 'الحالة'],
            [300, 150, 150, 150])

        low = self.db.fetchall(
            'SELECT name, quantity, min_quantity FROM products '
            'WHERE quantity <= min_quantity ORDER BY quantity')
        for item in low:
            status = "❌ نفذ" if item['quantity'] == 0 else "🔴 منخفض"
            tree.insert('', 'end', values=(
                item['name'], item['quantity'],
                item['min_quantity'], status))

    def get_dashboard_stats(self):
        today = date.today().isoformat()
        products = self.db.fetchone(
            "SELECT COUNT(*) as c FROM products")['c']
        sales = self.db.fetchone(
            'SELECT COALESCE(SUM(final_total), 0) as t FROM sales '
            'WHERE DATE(created_at) = ?', (today,))['t']
        invoices = self.db.fetchone(
            'SELECT COUNT(*) as c FROM sales '
            'WHERE DATE(created_at) = ?', (today,))['c']
        low = self.db.fetchone(
            'SELECT COUNT(*) as c FROM products '
            'WHERE quantity <= min_quantity')['c']
        return {
            'products': products,
            'today_sales': sales,
            'today_invoices': invoices,
            'low_stock': low
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # المنتجات
    # ═══════════════════════════════════════════════════════════════════════════

    def show_products(self):
        self.create_header("📦 إدارة المنتجات")

        btn_frame = tk.Frame(self.content_frame, bg='#0f0f23')
        btn_frame.pack(fill='x', pady=(0, 15))

        for text, color, cmd in [
            ("➕ إضافة", '#2ecc71', self.add_product),
            ("✏️ تعديل", '#3498db', self.edit_product),
            ("🗑️ حذف", '#e74c3c', self.delete_product)
        ]:
            tk.Button(btn_frame, text=text, font=('Segoe UI', 11),
                     bg=color, fg='white', relief='flat',
                     cursor='hand2', command=cmd).pack(side='right', padx=5)

        search_frame = tk.Frame(btn_frame, bg='#0f0f23')
        search_frame.pack(side='left')
        self.product_search = tk.Entry(search_frame, font=('Segoe UI', 11),
                                      bg='#1a1a2e', fg='white',
                                      insertbackground='white',
                                      relief='flat', width=25, justify='right')
        self.product_search.pack(side='right', ipady=5, padx=5)
        self.product_search.bind('<KeyRelease>', lambda e: self.load_products())
        tk.Button(search_frame, text="🔍", font=('Segoe UI', 11),
                 bg='#e94560', fg='white', relief='flat',
                 cursor='hand2', command=self.load_products).pack(side='right')

        self.products_tree = self.create_tree(
            ('id', 'barcode', 'name', 'category', 'price', 'qty', 'status'),
            ['الرقم', 'الباركود', 'اسم المنتج', 'الفئة',
             'السعر', 'الكمية', 'الحالة'],
            [60, 120, 250, 120, 100, 80, 100])

        self.load_products()

    def load_products(self):
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        search = getattr(self, 'product_search', None)
        term = search.get() if search else ''

        products = self.db.fetchall(
            'SELECT p.id, p.barcode, p.name, c.name as category, '
            'p.sale_price, p.quantity, p.min_quantity '
            'FROM products p LEFT JOIN categories c ON p.category_id = c.id '
            'WHERE p.name LIKE ? OR p.barcode LIKE ? ORDER BY p.id DESC',
            (f'%{term}%', f'%{term}%'))

        for p in products:
            status = "✅" if p['quantity'] > p['min_quantity'] else (
                "⚠️" if p['quantity'] > 0 else "❌")
            self.products_tree.insert('', 'end', values=(
                p['id'], p['barcode'] or '-', p['name'],
                p['category'] or 'غير محدد',
                f"{p['sale_price']:.2f}", p['quantity'], status))

    def add_product(self):
        ProductDialog(self.root, self.db, self.load_products)

    def edit_product(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء اختيار منتج")
            return
        pid = self.products_tree.item(selected[0])['values'][0]
        ProductDialog(self.root, self.db, self.load_products, pid)

    def delete_product(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء اختيار منتج")
            return
        pid = self.products_tree.item(selected[0])['values'][0]
        name = self.products_tree.item(selected[0])['values'][2]
        if messagebox.askyesno("تأكيد", f"حذف '{name}'؟"):
            self.db.execute("DELETE FROM products WHERE id = ?", (pid,))
            self.load_products()

    # ═══════════════════════════════════════════════════════════════════════════
    # نقطة البيع
    # ═══════════════════════════════════════════════════════════════════════════

    def show_pos(self):
        self.create_header("🛍️ نقطة البيع")
        self.invoice_items = []

        pos_frame = tk.Frame(self.content_frame, bg='#0f0f23')
        pos_frame.pack(fill='both', expand=True)

        # الجانب الأيمن - البحث
        right = tk.Frame(pos_frame, bg='#1a1a2e', padx=20, pady=20)
        right.pack(side='right', fill='both', expand=True)

        tk.Label(right, text="🔍 البحث (اسم/باركود)",
                font=('Segoe UI', 14, 'bold'),
                bg='#1a1a2e', fg='white').pack(anchor='e')
        self.pos_search = tk.Entry(right, font=('Segoe UI', 14), bg='#0f0f23',
                                    fg='white', insertbackground='white',
                                    relief='flat', justify='right')
        self.pos_search.pack(fill='x', ipady=10, pady=10)
        self.pos_search.bind('<Return>', lambda e: self.pos_search_product())
        tk.Button(right, text="بحث", font=('Segoe UI', 12),
                 bg='#e94560', fg='white', relief='flat',
                 cursor='hand2', command=self.pos_search_product).pack(anchor='e')

        self.pos_results = tk.Frame(right, bg='#1a1a2e')
        self.pos_results.pack(fill='both', expand=True, pady=10)

        # الجانب الأيسر - الفاتورة
        left = tk.Frame(pos_frame, bg='#16213e', padx=20, pady=20, width=420)
        left.pack(side='left', fill='y')
        left.pack_propagate(False)

        tk.Label(left, text="🧾 الفاتورة", font=('Segoe UI', 16, 'bold'),
                bg='#16213e', fg='white').pack(anchor='e', pady=(0, 15))

        self.invoice_tree = ttk.Treeview(left,
            columns=('name', 'qty', 'price', 'total'),
            show='headings', height=12)
        for col, head, width in zip(
            ('name', 'qty', 'price', 'total'),
            ['المنتج', 'الكمية', 'السعر', 'الإجمالي'],
            [160, 60, 80, 80]):
            self.invoice_tree.heading(col, text=head)
            self.invoice_tree.column(col, width=width,
                                    anchor='center' if width < 150 else 'e')
        self.invoice_tree.pack(fill='both', expand=True, pady=(0, 15))

        totals = tk.Frame(left, bg='#16213e')
        totals.pack(fill='x', pady=15)

        self.invoice_subtotal = tk.Label(totals,
                                          text="الإجمالي: 0.00 ر.س",
                                          font=('Segoe UI', 14),
                                          bg='#16213e', fg='white')
        self.invoice_subtotal.pack(anchor='e')

        disc_frame = tk.Frame(totals, bg='#16213e')
        disc_frame.pack(fill='x', pady=5)
        tk.Label(disc_frame, text="الخصم:", font=('Segoe UI', 12),
                bg='#16213e', fg='#aaa').pack(side='right')
        self.discount_entry = tk.Entry(disc_frame, font=('Segoe UI', 12),
                                        bg='#0f0f23', fg='white',
                                        insertbackground='white',
                                        relief='flat', width=10, justify='center')
        self.discount_entry.pack(side='right', padx=5)
        self.discount_entry.insert(0, "0")
        self.discount_entry.bind('<KeyRelease>',
                                  lambda e: self.update_invoice_totals())

        self.invoice_total = tk.Label(totals,
                                       text="الصافي: 0.00 ر.س",
                                       font=('Segoe UI', 18, 'bold'),
                                       bg='#16213e', fg='#2ecc71')
        self.invoice_total.pack(anchor='e', pady=10)

        btns = tk.Frame(left, bg='#16213e')
        btns.pack(fill='x')
        tk.Button(btns, text="🗑️ إفراغ", font=('Segoe UI', 12),
                 bg='#e74c3c', fg='white', relief='flat',
                 cursor='hand2', command=self.clear_invoice).pack(
                 side='right', padx=5, fill='x', expand=True)
        tk.Button(btns, text="💰 إتمام البيع", font=('Segoe UI', 14, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat',
                 cursor='hand2', command=self.complete_sale).pack(
                 side='right', padx=5, fill='x', expand=True)

    def pos_search_product(self):
        search = self.pos_search.get().strip()
        if not search:
            return
        for w in self.pos_results.winfo_children():
            w.destroy()

        products = self.db.fetchall(
            'SELECT id, name, sale_price, quantity, barcode FROM products '
            'WHERE name LIKE ? OR barcode = ? LIMIT 5',
            (f'%{search}%', search))

        if not products:
            tk.Label(self.pos_results, text="❌ لم يتم العثور على منتج",
                    font=('Segoe UI', 12), bg='#1a1a2e',
                    fg='#e74c3c').pack(pady=20)
            return

        for p in products:
            if p['quantity'] <= 0:
                continue
            card = tk.Frame(self.pos_results, bg='#0f0f23', padx=15, pady=15)
            card.pack(fill='x', pady=5)
            info = tk.Frame(card, bg='#0f0f23')
            info.pack(side='right', fill='both', expand=True)
            tk.Label(info, text=p['name'], font=('Segoe UI', 13, 'bold'),
                    bg='#0f0f23', fg='white').pack(anchor='e')
            tk.Label(info,
                    text=f"السعر: {p['sale_price']:.2f} ر.س | المتاح: {p['quantity']}",
                    font=('Segoe UI', 10), bg='#0f0f23',
                    fg='#aaa').pack(anchor='e')

            qty_frame = tk.Frame(card, bg='#0f0f23')
            qty_frame.pack(side='left')
            qty_entry = tk.Entry(qty_frame, font=('Segoe UI', 12), width=5,
                                bg='#1a1a2e', fg='white',
                                insertbackground='white',
                                relief='flat', justify='center')
            qty_entry.pack(side='left', padx=5)
            qty_entry.insert(0, "1")
            tk.Button(qty_frame, text="➕ إضافة", font=('Segoe UI', 11),
                     bg='#2ecc71', fg='white', relief='flat',
                     cursor='hand2',
                     command=lambda prod=p, q=qty_entry: self.add_to_invoice(prod, q)).pack(side='left')

    def add_to_invoice(self, product, qty_entry):
        try:
            qty = int(qty_entry.get())
            if qty <= 0:
                raise ValueError
        except:
            messagebox.showwarning("تنبيه", "كمية غير صحيحة")
            return

        if qty > product['quantity']:
            messagebox.showwarning("تنبيه", f"المتاح: {product['quantity']}")
            return

        for i, item in enumerate(self.invoice_items):
            if item['product_id'] == product['id']:
                new_qty = item['quantity'] + qty
                if new_qty > product['quantity']:
                    messagebox.showwarning("تنبيه",
                        f"المتاح: {product['quantity']}")
                    return
                self.invoice_items[i]['quantity'] = new_qty
                self.invoice_items[i]['total'] = new_qty * item['unit_price']
                self.refresh_invoice()
                self.pos_search.delete(0, 'end')
                for w in self.pos_results.winfo_children():
                    w.destroy()
                return

        self.invoice_items.append({
            'product_id': product['id'],
            'name': product['name'],
            'quantity': qty,
            'unit_price': product['sale_price'],
            'total': qty * product['sale_price']
        })

        self.refresh_invoice()
        self.pos_search.delete(0, 'end')
        for w in self.pos_results.winfo_children():
            w.destroy()

    def refresh_invoice(self):
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        for item in self.invoice_items:
            self.invoice_tree.insert('', 'end', values=(
                item['name'], item['quantity'],
                f"{item['unit_price']:.2f}", f"{item['total']:.2f}"))
        self.update_invoice_totals()

    def update_invoice_totals(self):
        subtotal = sum(item['total'] for item in self.invoice_items)
        try:
            discount = float(self.discount_entry.get() or 0)
        except:
            discount = 0
        total = max(0, subtotal - discount)
        self.invoice_subtotal.config(text=f"الإجمالي: {subtotal:.2f} ر.س")
        self.invoice_total.config(text=f"الصافي: {total:.2f} ر.س")

    def clear_invoice(self):
        self.invoice_items = []
        self.refresh_invoice()
        self.discount_entry.delete(0, 'end')
        self.discount_entry.insert(0, "0")

    def complete_sale(self):
        if not self.invoice_items:
            messagebox.showwarning("تنبيه", "الفاتورة فارغة!")
            return
        try:
            discount = float(self.discount_entry.get() or 0)
        except:
            discount = 0
        subtotal = sum(item['total'] for item in self.invoice_items)
        total = max(0, subtotal - discount)
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        self.db.execute(
            'INSERT INTO sales (invoice_number, user_id, total, discount, final_total) '
            'VALUES (?, ?, ?, ?, ?)',
            (invoice_number, self.user['id'], subtotal, discount, total))
        sale_id = self.db.cursor.lastrowid

        for item in self.invoice_items:
            self.db.execute(
                'INSERT INTO sale_items (sale_id, product_id, quantity, '
                'unit_price, total_price) VALUES (?, ?, ?, ?, ?)',
                (sale_id, item['product_id'], item['quantity'],
                 item['unit_price'], item['total']))
            self.db.execute(
                'UPDATE products SET quantity = quantity - ? WHERE id = ?',
                (item['quantity'], item['product_id']))

        messagebox.showinfo("تم",
            f"تم إتمام البيع!\nرقم الفاتورة: {invoice_number}\nالمبلغ: {total:.2f} ر.س")
        self.clear_invoice()

    # ═══════════════════════════════════════════════════════════════════════════
    # المبيعات
    # ═══════════════════════════════════════════════════════════════════════════

    def show_sales(self):
        self.create_header("📋 سجل المبيعات")

        filter_frame = tk.Frame(self.content_frame, bg='#0f0f23')
        filter_frame.pack(fill='x', pady=(0, 15))

        for label, attr, default in [
            ("من:", 'sales_from', date.today().replace(day=1).isoformat()),
            ("إلى:", 'sales_to', date.today().isoformat())
        ]:
            tk.Label(filter_frame, text=label, font=('Segoe UI', 11),
                    bg='#0f0f23', fg='white').pack(side='right', padx=5)
            entry = tk.Entry(filter_frame, font=('Segoe UI', 11), width=12,
                            bg='#1a1a2e', fg='white',
                            insertbackground='white',
                            relief='flat', justify='center')
            entry.pack(side='right', padx=5)
            entry.insert(0, default)
            setattr(self, attr, entry)

        tk.Button(filter_frame, text="🔍 عرض", font=('Segoe UI', 11),
                 bg='#e94560', fg='white', relief='flat',
                 cursor='hand2', command=self.load_sales).pack(side='right', padx=10)
        self.sales_total_label = tk.Label(filter_frame, text="",
                                          font=('Segoe UI', 14, 'bold'),
                                          bg='#0f0f23', fg='#2ecc71')
        self.sales_total_label.pack(side='left')

        self.sales_tree = self.create_tree(
            ('invoice', 'date', 'user', 'total', 'discount', 'final'),
            ['رقم الفاتورة', 'التاريخ', 'الكاشير',
             'الإجمالي', 'الخصم', 'الصافي'],
            [150, 150, 120, 100, 100, 100])
        self.load_sales()

    def load_sales(self):
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)

        sales = self.db.fetchall(
            'SELECT s.invoice_number, s.created_at, u.full_name as user, '
            's.total, s.discount, s.final_total '
            'FROM sales s JOIN users u ON s.user_id = u.id '
            'WHERE DATE(s.created_at) BETWEEN ? AND ? '
            'ORDER BY s.created_at DESC',
            (self.sales_from.get(), self.sales_to.get()))

        total = 0
        for sale in sales:
            total += sale['final_total']
            self.sales_tree.insert('', 'end', values=(
                sale['invoice_number'], sale['created_at'][:16],
                sale['user'], f"{sale['total']:.2f}",
                f"{sale['discount']:.2f}", f"{sale['final_total']:.2f}"))
        self.sales_total_label.config(text=f"إجمالي: {total:.2f} ر.س")

    # ═══════════════════════════════════════════════════════════════════════════
    # الموردين
    # ═══════════════════════════════════════════════════════════════════════════

    def show_suppliers(self):
        self.create_header("🏭 الموردين")
        btn_frame = tk.Frame(self.content_frame, bg='#0f0f23')
        btn_frame.pack(fill='x', pady=(0, 15))
        tk.Button(btn_frame, text="➕ إضافة مورد", font=('Segoe UI', 11),
                 bg='#2ecc71', fg='white', relief='flat',
                 cursor='hand2', command=self.add_supplier).pack(side='right', padx=5)

        self.suppliers_tree = self.create_tree(
            ('id', 'name', 'company', 'phone', 'email'),
            ['الرقم', 'الاسم', 'الشركة', 'الهاتف', 'البريد'],
            [60, 200, 150, 120, 180])
        self.load_suppliers()

    def load_suppliers(self):
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        for s in self.db.fetchall("SELECT * FROM suppliers ORDER BY id DESC"):
            self.suppliers_tree.insert('', 'end', values=(
                s['id'], s['name'], s['company'] or '-',
                s['phone'] or '-', s['email'] or '-'))

    def add_supplier(self):
        SupplierDialog(self.root, self.db, self.load_suppliers)

    # ═══════════════════════════════════════════════════════════════════════════
    # العملاء
    # ═══════════════════════════════════════════════════════════════════════════

    def show_customers(self):
        self.create_header("👥 العملاء")
        btn_frame = tk.Frame(self.content_frame, bg='#0f0f23')
        btn_frame.pack(fill='x', pady=(0, 15))
        tk.Button(btn_frame, text="➕ إضافة عميل", font=('Segoe UI', 11),
                 bg='#2ecc71', fg='white', relief='flat',
                 cursor='hand2', command=self.add_customer).pack(side='right', padx=5)

        self.customers_tree = self.create_tree(
            ('id', 'name', 'phone', 'email', 'credit'),
            ['الرقم', 'الاسم', 'الهاتف', 'البريد', 'الرصيد'],
            [60, 200, 120, 180, 100])
        self.load_customers()

    def load_customers(self):
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        for c in self.db.fetchall("SELECT * FROM customers ORDER BY id DESC"):
            self.customers_tree.insert('', 'end', values=(
                c['id'], c['name'], c['phone'] or '-',
                c['email'] or '-', f"{c['credit']:.2f}"))

    def add_customer(self):
        CustomerDialog(self.root, self.db, self.load_customers)

    # ═══════════════════════════════════════════════════════════════════════════
    # التقارير
    # ═══════════════════════════════════════════════════════════════════════════

    def show_reports(self):
        self.create_header("📈 التقارير")
        reports_frame = tk.Frame(self.content_frame, bg='#0f0f23')
        reports_frame.pack(fill='both', expand=True)

        reports = [
            ("📊", "تقرير المبيعات اليومية", self.daily_sales_report),
            ("📦", "تقرير المخزون", self.inventory_report),
            ("💰", "تقرير الأرباح", self.profit_report),
            ("⚠️", "المنتجات منخفضة المخزون", self.low_stock_report),
        ]

        for icon, title, cmd in reports:
            card = tk.Frame(reports_frame, bg='#1a1a2e', padx=30, pady=30)
            card.pack(fill='x', pady=10)
            tk.Label(card, text=icon, font=('Segoe UI', 36),
                    bg='#1a1a2e', fg='#e94560').pack(side='right')
            info = tk.Frame(card, bg='#1a1a2e')
            info.pack(side='right', padx=20, fill='y')
            tk.Label(info, text=title, font=('Segoe UI', 16, 'bold'),
                    bg='#1a1a2e', fg='white').pack(anchor='e')
            tk.Button(card, text="عرض التقرير ▶", font=('Segoe UI', 12),
                     bg='#e94560', fg='white', relief='flat',
                     cursor='hand2', command=cmd).pack(side='left')

    def daily_sales_report(self):
        today = date.today().isoformat()
        s = self.db.fetchall(
            'SELECT COALESCE(SUM(final_total), 0) as total, '
            'COALESCE(SUM(discount), 0) as discount, COUNT(*) as count '
            'FROM sales WHERE DATE(created_at) = ?', (today,))[0]
        report = f"""تقرير المبيعات اليومية - {today}
{'='*40}
عدد الفواتير: {s['count']}
إجمالي المبيعات: {s['total']:.2f} ر.س
إجمالي الخصومات: {s['discount']:.2f} ر.س
"""
        self.show_report_window("تقرير المبيعات اليومية", report)

    def inventory_report(self):
        products = self.db.fetchall(
            'SELECT name, quantity, purchase_price, sale_price, '
            '(quantity * purchase_price) as cost, '
            '(quantity * sale_price) as value '
            'FROM products ORDER BY quantity DESC')
        total_cost = sum(p['cost'] for p in products)
        total_value = sum(p['value'] for p in products)
        report = f"""تقرير المخزون
{'='*50}
إجمالي التكلفة: {total_cost:.2f} ر.س
إجمالي قيمة البيع: {total_value:.2f} ر.س
عدد المنتجات: {len(products)}

{'المنتج':<20} {'الكمية':<8} {'التكلفة':<10} {'البيع':<10}
{'='*50}
"""
        for p in products:
            report += (f"{p['name']:<20} {p['quantity']:<8} "
                      f"{p['cost']:<10.2f} {p['value']:<10.2f}\n")
        self.show_report_window("تقرير المخزون", report)

    def profit_report(self):
        items = self.db.fetchall(
            'SELECT si.quantity, si.unit_price, p.purchase_price '
            'FROM sale_items si JOIN products p ON si.product_id = p.id')
        revenue = sum(i['quantity'] * i['unit_price'] for i in items)
        cost = sum(i['quantity'] * i['purchase_price'] for i in items)
        profit = revenue - cost
        margin = (profit / revenue * 100) if revenue else 0
        report = f"""تقرير الأرباح
{'='*40}
إجمالي الإيرادات: {revenue:.2f} ر.س
إجمالي التكاليف: {cost:.2f} ر.س
صافي الربح: {profit:.2f} ر.س
نسبة الربح: {margin:.1f}%
"""
        self.show_report_window("تقرير الأرباح", report)

    def low_stock_report(self):
        products = self.db.fetchall(
            'SELECT name, quantity, min_quantity, sale_price '
            'FROM products WHERE quantity <= min_quantity ORDER BY quantity')
        report = f"""المنتجات منخفضة المخزون
{'='*50}
عدد المنتجات: {len(products)}

{'المنتج':<20} {'الكمية':<8} {'الحد الأدنى':<12} {'السعر':<10}
{'='*50}
"""
        for p in products:
            report += (f"{p['name']:<20} {p['quantity']:<8} "
                      f"{p['min_quantity']:<12} {p['sale_price']:<10.2f}\n")
        self.show_report_window("منتجات منخفضة المخزون", report)

    def show_report_window(self, title, content):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("700x500")
        window.configure(bg='#0f0f23')
        text = scrolledtext.ScrolledText(window, font=('Consolas', 11),
                                        bg='#1a1a2e', fg='white',
                                        insertbackground='white',
                                        padx=20, pady=20)
        text.pack(fill='both', expand=True, padx=20, pady=20)
        text.insert('1.0', content)
        text.config(state='disabled')
        tk.Button(window, text="🖨️ حفظ", font=('Segoe UI', 12),
                 bg='#3498db', fg='white', relief='flat',
                 cursor='hand2',
                 command=lambda: self.save_report(content)).pack(pady=10)

    def save_report(self, content):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("تم", f"تم الحفظ في:\n{path}")

    # ═══════════════════════════════════════════════════════════════════════════
    # المستخدمين
    # ═══════════════════════════════════════════════════════════════════════════

    def show_users(self):
        self.create_header("👨‍💼 إدارة المستخدمين")
        btn_frame = tk.Frame(self.content_frame, bg='#0f0f23')
        btn_frame.pack(fill='x', pady=(0, 15))
        tk.Button(btn_frame, text="➕ إضافة مستخدم", font=('Segoe UI', 11),
                 bg='#2ecc71', fg='white', relief='flat',
                 cursor='hand2', command=self.add_user).pack(side='right', padx=5)

        self.users_tree = self.create_tree(
            ('id', 'username', 'name', 'role', 'created'),
            ['الرقم', 'اسم المستخدم', 'الاسم الكامل',
             'الصلاحية', 'تاريخ الإنشاء'],
            [60, 150, 200, 100, 150])
        self.load_users()

    def load_users(self):
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        for u in self.db.fetchall("SELECT * FROM users ORDER BY id"):
            self.users_tree.insert('', 'end', values=(
                u['id'], u['username'], u['full_name'],
                self.get_role_name(u['role']), u['created_at'][:16]))

    def add_user(self):
        UserDialog(self.root, self.db, self.load_users)

    # ═══════════════════════════════════════════════════════════════════════════
    # الإعدادات
    # ═══════════════════════════════════════════════════════════════════════════

    def show_settings(self):
        self.create_header("⚙️ الإعدادات")
        settings = tk.Frame(self.content_frame, bg='#0f0f23')
        settings.pack(fill='both', expand=True)

        backup_frame = tk.LabelFrame(settings, text="النسخ الاحتياطي",
                                      font=('Segoe UI', 14, 'bold'),
                                      bg='#1a1a2e', fg='white',
                                      padx=20, pady=20)
        backup_frame.pack(fill='x', pady=10)

        tk.Button(backup_frame, text="💾 نسخ احتياطي",
                 font=('Segoe UI', 12), bg='#3498db', fg='white',
                 relief='flat', cursor='hand2',
                 command=self.backup_db).pack(pady=10)
        tk.Button(backup_frame, text="📥 استعادة",
                 font=('Segoe UI', 12), bg='#e94560', fg='white',
                 relief='flat', cursor='hand2',
                 command=self.restore_db).pack(pady=10)

    def backup_db(self):
        path = filedialog.asksaveasfilename(defaultextension=".db",
                                            filetypes=[("Database", "*.db")])
        if path:
            shutil.copy2(self.db.db_file, path)
            messagebox.showinfo("تم", "تم إنشاء نسخة احتياطية!")

    def restore_db(self):
        path = filedialog.askopenfilename(filetypes=[("Database", "*.db")])
        if path and messagebox.askyesno("تأكيد",
            "سيتم استبدال البيانات الحالية!"):
            shutil.copy2(path, self.db.db_file)
            messagebox.showinfo("تم", "تمت الاستعادة! أعد تشغيل البرنامج.")


# ═══════════════════════════════════════════════════════════════════════════════
# نوافذ الحوار
# ═══════════════════════════════════════════════════════════════════════════════

class BaseDialog:
    def __init__(self, parent, title, width=500, height=600):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.configure(bg='#1a1a2e')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.entries = {}

        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def add_field(self, label, show=None, default=""):
        tk.Label(self.dialog, text=label, font=('Segoe UI', 12),
                bg='#1a1a2e', fg='white').pack(anchor='e',
                padx=30, pady=(15, 5))
        entry = tk.Entry(self.dialog, font=('Segoe UI', 12),
                        bg='#0f0f23', fg='white',
                        insertbackground='white', relief='flat',
                        justify='right', show=show or '')
        entry.pack(fill='x', padx=30, ipady=8)
        entry.insert(0, default)
        self.entries[label] = entry
        return entry

    def add_buttons(self, save_cmd):
        btn_frame = tk.Frame(self.dialog, bg='#1a1a2e')
        btn_frame.pack(fill='x', padx=30, pady=30)
        tk.Button(btn_frame, text="❌ إلغاء", font=('Segoe UI', 12),
                 bg='#e74c3c', fg='white', relief='flat',
                 cursor='hand2', command=self.dialog.destroy).pack(
                 side='right', padx=5)
        tk.Button(btn_frame, text="💾 حفظ", font=('Segoe UI', 12, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat',
                 cursor='hand2', command=save_cmd).pack(side='right', padx=5)


class ProductDialog(BaseDialog):
    def __init__(self, parent, db, refresh_callback, product_id=None):
        super().__init__(parent,
            "تعديل منتج" if product_id else "إضافة منتج جديد")
        self.db = db
        self.refresh = refresh_callback
        self.product_id = product_id

        categories = db.fetchall("SELECT id, name FROM categories")
        self.cat_map = {c['name']: c['id'] for c in categories}

        self.add_field("الاسم")
        self.add_field("الباركود")
        self.add_field("سعر الشراء")
        self.add_field("سعر البيع")
        self.add_field("الكمية")
        self.add_field("الحد الأدنى", default="5")

        tk.Label(self.dialog, text="الفئة:", font=('Segoe UI', 12),
                bg='#1a1a2e', fg='white').pack(anchor='e',
                padx=30, pady=(15, 5))
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(self.dialog, textvariable=self.cat_var,
                                      values=list(self.cat_map.keys()),
                                      font=('Segoe UI', 12), state='readonly')
        self.cat_combo.pack(fill='x', padx=30, ipady=5)

        if product_id:
            p = db.fetchone("SELECT * FROM products WHERE id = ?",
                           (product_id,))
            if p:
                self.entries["الاسم"].insert(0, p['name'])
                self.entries["الباركود"].insert(0, p['barcode'] or '')
                self.entries["سعر الشراء"].insert(0, str(p['purchase_price']))
                self.entries["سعر البيع"].insert(0, str(p['sale_price']))
                self.entries["الكمية"].insert(0, str(p['quantity']))
                self.entries["الحد الأدنى"].delete(0, 'end')
                self.entries["الحد الأدنى"].insert(0, str(p['min_quantity']))
                cat = db.fetchone(
                    "SELECT name FROM categories WHERE id = ?",
                    (p['category_id'],))
                if cat:
                    self.cat_var.set(cat['name'])

        self.add_buttons(self.save)

    def save(self):
        try:
            name = self.entries["الاسم"].get().strip()
            barcode = self.entries["الباركود"].get().strip() or None
            purchase = float(self.entries["سعر الشراء"].get() or 0)
            sale = float(self.entries["سعر البيع"].get() or 0)
            qty = int(self.entries["الكمية"].get() or 0)
            min_qty = int(self.entries["الحد الأدنى"].get() or 5)
            cat_id = self.cat_map.get(self.cat_var.get())

            if not name:
                messagebox.showwarning("تنبيه", "الرجاء إدخال اسم المنتج")
                return

            if self.product_id:
                self.db.execute(
                    'UPDATE products SET name=?, barcode=?, category_id=?, '
                    'purchase_price=?, sale_price=?, quantity=?, '
                    'min_quantity=? WHERE id=?',
                    (name, barcode, cat_id, purchase, sale,
                     qty, min_qty, self.product_id))
            else:
                self.db.execute(
                    'INSERT INTO products (name, barcode, category_id, '
                    'purchase_price, sale_price, quantity, min_quantity) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (name, barcode, cat_id, purchase, sale, qty, min_qty))

            messagebox.showinfo("تم", "تم حفظ المنتج بنجاح!")
            self.dialog.destroy()
            self.refresh()
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال أرقام صحيحة")


class SupplierDialog(BaseDialog):
    def __init__(self, parent, db, refresh_callback):
        super().__init__(parent, "إضافة مورد جديد", height=500)
        self.db = db
        self.refresh = refresh_callback
        self.add_field("الاسم")
        self.add_field("الشركة")
        self.add_field("الهاتف")
        self.add_field("البريد الإلكتروني")
        self.add_field("العنوان")
        self.add_buttons(self.save)

    def save(self):
        name = self.entries["الاسم"].get().strip()
        if not name:
            messagebox.showwarning("تنبيه", "الرجاء إدخال الاسم")
            return
        self.db.execute(
            'INSERT INTO suppliers (name, company, phone, email, address) '
            'VALUES (?, ?, ?, ?, ?)',
            (name,
             self.entries["الشركة"].get().strip() or None,
             self.entries["الهاتف"].get().strip() or None,
             self.entries["البريد الإلكتروني"].get().strip() or None,
             self.entries["العنوان"].get().strip() or None))
        messagebox.showinfo("تم", "تم إضافة المورد!")
        self.dialog.destroy()
        self.refresh()


class CustomerDialog(BaseDialog):
    def __init__(self, parent, db, refresh_callback):
        super().__init__(parent, "إضافة عميل جديد", height=500)
        self.db = db
        self.refresh = refresh_callback
        self.add_field("الاسم")
        self.add_field("الهاتف")
        self.add_field("البريد الإلكتروني")
        self.add_field("العنوان")
        self.add_buttons(self.save)

    def save(self):
        name = self.entries["الاسم"].get().strip()
        if not name:
            messagebox.showwarning("تنبيه", "الرجاء إدخال الاسم")
            return
        self.db.execute(
            'INSERT INTO customers (name, phone, email, address) '
            'VALUES (?, ?, ?, ?)',
            (name,
             self.entries["الهاتف"].get().strip() or None,
             self.entries["البريد الإلكتروني"].get().strip() or None,
             self.entries["العنوان"].get().strip() or None))
        messagebox.showinfo("تم", "تم إضافة العميل!")
        self.dialog.destroy()
        self.refresh()


class UserDialog(BaseDialog):
    def __init__(self, parent, db, refresh_callback):
        super().__init__(parent, "إضافة مستخدم جديد", height=500)
        self.db = db
        self.refresh = refresh_callback
        self.add_field("اسم المستخدم")
        self.add_field("كلمة المرور", show='●')
        self.add_field("الاسم الكامل")

        tk.Label(self.dialog, text="الصلاحية:", font=('Segoe UI', 12),
                bg='#1a1a2e', fg='white').pack(anchor='e',
                padx=30, pady=(15, 5))
        self.role_var = tk.StringVar(value='cashier')
        ttk.Combobox(self.dialog, textvariable=self.role_var,
                     values=['admin', 'manager', 'cashier'],
                     font=('Segoe UI', 12), state='readonly').pack(
                     fill='x', padx=30, ipady=5)
        self.add_buttons(self.save)

    def save(self):
        username = self.entries["اسم المستخدم"].get().strip()
        password = self.entries["كلمة المرور"].get().strip()
        full_name = self.entries["الاسم الكامل"].get().strip()

        if not all([username, password, full_name]):
            messagebox.showwarning("تنبيه", "الرجاء ملء جميع الحقول")
            return

        try:
            self.db.execute(
                'INSERT INTO users (username, password, full_name, role) '
                'VALUES (?, ?, ?, ?)',
                (username, password, full_name, self.role_var.get()))
            messagebox.showinfo("تم", "تم إضافة المستخدم!")
            self.dialog.destroy()
            self.refresh()
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "اسم المستخدم موجود مسبقاً!")


# ═══════════════════════════════════════════════════════════════════════════════
# التشغيل
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
