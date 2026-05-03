# Petso API

واجهة خلفية (Backend) مبنية بـ Django + DRF لتطبيق Petso، وتغطي:
المستخدمين، المزارعين، الأطباء البيطريين، الشركات، المتجر، الطلبات، المدفوعات، الخدمات الطبية، السوشيال، الشات، والذكاء الاصطناعي.

## نظرة عامة سريعة

- **اللغة والإطار:** Python, Django, Django REST Framework
- **التوثيق:** Swagger عبر `drf-spectacular`
- **المصادقة:** JWT (`/api/auth/login/` + `/api/auth/token/refresh/`)
- **لوحة التحكم:** Django Admin على `/admin/`
- **النظام مبني Multi-App** داخل مجلد `apps`

## هيكل المشروع

```text
petso_project/           إعدادات المشروع والـ URLs الرئيسية
apps/
  users/                 auth + register + profiles + activity
  farmers/               ملف المربي + قطعان الدواجن
  vets/                  ملفات الأطباء + التقييمات
  companies/             الشركات + التحليلات
  ecommerce/             التصنيفات + المنتجات + السلة
  orders/                الطلبات + تاريخ حالات الطلب
  payments/              المحفظة + المعاملات
  medical/               المواعيد + الروشتات
  ai/                    حالات الذكاء الاصطناعي
  social/                المنشورات + التعليقات
  chat/                  المحادثات + الرسائل
  system/                الإشعارات + السجلات + future features
tools/
  build_postman_collection.py
deployment/
  petso.sqlite3          SQLite جاهزة للتجارب (خاصة Vercel demo)
```

## الـ Roles في النظام

الأدوار المعرفة في نموذج المستخدم `apps/users/models.py`:

- `farmer` (مربي)
- `vet` (طبيب بيطري)
- `company` (شركة)
- `admin` (مدير النظام)

> تسجيل الدخول الأساسي في المشروع يعتمد على **email** وليس username.

## كل Role بيعمل إيه؟

### 1) Admin

- إدارة شاملة عبر Django Admin (`/admin/`)
- عرض/إدارة المستخدمين عبر `GET/POST /api/auth/profile/` (صلاحية `IsAdminUser`)
- مشاهدة سجلات النظام:
  - `GET /api/system/audit-logs/`
  - `GET /api/system/error-logs/`
- يرى كل البيانات في بعض الموديولات (مثل الطلبات وحالات AI)

### 2) Farmer

- إنشاء وإدارة ملفه كمربي: `/api/farmers/profile/`
- إدارة قطعان الدواجن: `/api/farmers/flocks/`
- التسوق: تصفح المنتجات + إضافة للسلة عبر `/api/ecommerce/cart/` و `add_item`
- إنشاء الطلبات ومتابعتها: `/api/orders/orders/`
- التعامل الطبي: عرض مواعيده وروشتاته حسب علاقته
- كتابة منشورات وتعليقات في السوشيال

### 3) Vet

- إنشاء/تعديل ملف الطبيب: `/api/vets/profiles/`
- استقبال التقييمات: `/api/vets/reviews/`
- التعامل مع المواعيد والروشتات في الموديول الطبي
- المشاركة في الشات والسوشيال

### 4) Company

- إدارة بيانات الشركة: `/api/companies/companies/`
- عرض تحليلات الشركة (حسب الحالة): `/api/companies/analytics/`
- إدارة منتجات المتجر بشكل عام عبر `/api/ecommerce/products/`
- إدارة الحساب والطلبات والمدفوعات المرتبطة به

## الموديولات الرئيسية (API Modules)

المسارات الأساسية معرفة في `petso_project/urls.py`:

- `api/auth/` المستخدمين والمصادقة
- `api/farmers/` المزارعين
- `api/vets/` الأطباء
- `api/companies/` الشركات
- `api/ecommerce/` المتجر
- `api/orders/` الطلبات
- `api/payments/` المدفوعات
- `api/ai/` الذكاء الاصطناعي
- `api/medical/` الجانب الطبي
- `api/social/` المجتمع
- `api/chat/` الدردشة
- `api/system/` النظام والإشعارات

## المصادقة والتسجيل

داخل `api/auth/`:

- `POST /api/auth/register/` إنشاء حساب (**مفعّل مباشرة** `is_verified=True` — لا يوجد OTP ولا تحقق بريد)
- `POST /api/auth/login/` JWT login
- `POST /api/auth/token/refresh/` refresh token

ملاحظات:

- `/api/auth/login/` لا يحتاج CSRF عند استخدام JWT JSON request.
- تسجيل الدخول للـ admin panel (`/admin/`) يحتاج CSRF + Cookies بشكل صحيح.

## التوثيق والتجربة

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- Schema: `http://127.0.0.1:8000/api/schema/`
- API root docs: `http://127.0.0.1:8000/api/`

## التشغيل محليًا (Local)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

## Postman Collections

- `Petso_Postman_Collection.json`: سيناريو محلي كامل (تسجيل ثم دخول مباشرة)
- `Petso_Postman_Collection.Production.json`: إنتاج Vercel + متغيرات الأدوار والتوكنات

إعادة التوليد:

```bash
python tools/build_postman_collection.py
```

## قاعدة البيانات: SQLite vs Postgres

### SQLite

- مناسب للتطوير المحلي أو VPS بقرص دائم.
- لا يحتاج خدمة DB خارجية.

### Postgres

- الأفضل للإنتاج الحقيقي (خصوصًا cloud/serverless).
- يدعم التوسع والاعتمادية بشكل أفضل.

## النشر على Vercel (مهم جدًا)

الرابط الحالي: **https://petso-api.vercel.app**

### فكرة العمل الحالية

- لو `DATABASE_URL` **غير مضبوط**:
  - يستخدم النظام SQLite المرفقة في `deployment/petso.sqlite3`
  - يتم نسخها في بيئة Vercel المؤقتة
  - أي بيانات جديدة قد لا تستمر بعد cold start/redeploy

- لو `DATABASE_URL` مضبوط على Postgres:
  - كل من `/admin/` و`/api/` يستخدموا نفس قاعدة البيانات الدائمة

### متغيرات البيئة الأساسية على Vercel

| Variable | مثال |
|---|---|
| `SECRET_KEY` | قيمة عشوائية قوية |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.vercel.app,your-project.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | `https://your-project.vercel.app` |
| `DATABASE_URL` | اتركه فارغًا للـ bundled SQLite أو ضعه Postgres للإنتاج الدائم |
| `REDIS_URL` | Redis لـ Channels (اختياري لكن مهم للـ realtime) |

### Admin + API نفس قاعدة البيانات

Django دائمًا يستخدم `DATABASES['default']`، وبالتالي:

- Admin panel وREST API على نفس الـ DB دائمًا
- حساب demo bundled:
  - `admin@petso.local`
  - `PetsoVercel2026!`

## النشر على VPS (خصوصًا Windows VPS)

لو عندك VPS بقرص دائم، SQLite تكون مناسبة جدًا:

1. انسخ المشروع على السيرفر
2. ثبّت المتطلبات
3. اجعل `DATABASE_URL=sqlite:///D:/Petso/db.sqlite3` (مسار دائم)
4. شغّل:
   - `python manage.py migrate`
   - `python manage.py createsuperuser`
5. شغّل التطبيق كخدمة (Waitress + NSSM مثلًا)
6. اربطه بـ IIS/Nginx reverse proxy

بهذا الشكل البيانات تظل محفوظة ولن تُمسح تلقائيًا مثل serverless.

## مشاكل شائعة وحلولها

### 1) 401 في `/api/auth/login/`

- تأكد من البريد وكلمة المرور
- تأكد أن الحساب موجود في نفس قاعدة البيانات المستخدمة فعليًا

### 2) 403 CSRF في `/admin/`

- اضبط:
  - `ALLOWED_HOSTS`
  - `CSRF_TRUSTED_ORIGINS` مع `http://` أو `https://`
- امسح cookies وأعد تحميل صفحة الـ admin

### 3) 500 في `/api/auth/register/`

- راجع سجلات السيرفر (traceback)؛ التسجيل لا يعتمد على Celery بعد الآن.

## أوامر مفيدة

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py bootstrap_admin
python manage.py build_vercel_sqlite
python tools/build_postman_collection.py
```

## ملاحظات أمنية

- لا ترفع `.env` على Git
- غيّر كلمات المرور الافتراضية فورًا
- استخدم `DEBUG=False` في الإنتاج
- استخدم `SECRET_KEY` قوية

## GitHub

المستودع: [kamelfcis/Petso-API](https://github.com/kamelfcis/Petso-API)
