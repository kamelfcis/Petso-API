"""Build Postman collections (run from repo root: python tools/build_postman_collection.py).

Outputs:
- Petso_Postman_Collection.json — local (http://127.0.0.1:8000)
- Petso_Postman_Collection.Production.json — https://petso-api.vercel.app
"""
import json
from pathlib import Path


def req(name, method, path, body=None, auth="bearer", desc="", tests=None):
    r = {
        "name": name,
        "request": {
            "method": method,
            "header": [{"key": "Content-Type", "value": "application/json"}] if body else [],
            "url": "{{base_url}}/api" + path,
        },
    }
    if desc:
        r["request"]["description"] = desc
    if body is not None:
        r["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(body, ensure_ascii=False, indent=2),
            "options": {"raw": {"language": "json"}},
        }
    if auth == "noauth":
        r["request"]["auth"] = {"type": "noauth"}
    elif auth == "bearer":
        r["request"]["auth"] = {
            "type": "bearer",
            "bearer": [{"key": "token", "value": "{{access_token}}", "type": "string"}],
        }
    if tests:
        r["event"] = [{"listen": "test", "script": {"exec": tests, "type": "text/javascript"}}]
    return r


def folder(name, items, desc=""):
    f = {"name": name, "item": items}
    if desc:
        f["description"] = desc
    return f


def build_auth_items(*, production: bool):
    """Register, login, refresh. New accounts are verified at signup (no OTP / verify-email)."""
    items = [
        req(
            "Register - Farmer (مربي)",
            "POST",
            "/auth/register/",
            {
                "email": "{{farmer_email}}",
                "password": "{{farmer_password}}",
                "name": "Farmer Demo",
                "phone_number": "+201000000001",
                "role": "farmer",
            },
            auth="noauth",
            desc="Creates farmer account; `is_verified` is true — login with JWT immediately.",
        ),
        req(
            "Register - Vet (طبيب)",
            "POST",
            "/auth/register/",
            {
                "email": "{{vet_email}}",
                "password": "{{vet_password}}",
                "name": "Vet Demo",
                "phone_number": "+201000000002",
                "role": "vet",
            },
            auth="noauth",
        ),
        req(
            "Register - Company (شركة)",
            "POST",
            "/auth/register/",
            {
                "email": "{{company_email}}",
                "password": "{{company_password}}",
                "name": "Company Owner",
                "phone_number": "+201000000003",
                "role": "company",
            },
            auth="noauth",
        ),
    ]
    jwt_tests_farmer = [
        "function uidFromJwt(token) {",
        "  try {",
        "    var p = token.split('.')[1];",
        "    var s = p.replace(/-/g, '+').replace(/_/g, '/');",
        "    var pad = s.length % 4 ? '='.repeat(4 - s.length % 4) : '';",
        "    var json = atob(s + pad);",
        "    return JSON.parse(json).user_id;",
        "  } catch (e) { return null; }",
        "}",
        "try { var j = pm.response.json();",
        'if (j.access) { pm.collectionVariables.set("access_token", j.access);',
        "  var uid = uidFromJwt(j.access);",
        '  if (uid) pm.collectionVariables.set("farmer_user_id", String(uid));',
        "}",
        'if (j.refresh) pm.collectionVariables.set("refresh_token", j.refresh);',
        "} catch (e) {}",
    ]
    jwt_tests_vet = [
        "function uidFromJwt(token) {",
        "  try {",
        "    var p = token.split('.')[1];",
        "    var s = p.replace(/-/g, '+').replace(/_/g, '/');",
        "    var pad = s.length % 4 ? '='.repeat(4 - s.length % 4) : '';",
        "    var json = atob(s + pad);",
        "    return JSON.parse(json).user_id;",
        "  } catch (e) { return null; }",
        "}",
        "try { var j = pm.response.json();",
        'if (j.access) { pm.collectionVariables.set("access_token", j.access);',
        "  var uid = uidFromJwt(j.access);",
        '  if (uid) pm.collectionVariables.set("vet_user_id", String(uid));',
        "}",
        'if (j.refresh) pm.collectionVariables.set("refresh_token", j.refresh);',
        "} catch (e) {}",
    ]
    jwt_tests_company = [
        "function uidFromJwt(token) {",
        "  try {",
        "    var p = token.split('.')[1];",
        "    var s = p.replace(/-/g, '+').replace(/_/g, '/');",
        "    var pad = s.length % 4 ? '='.repeat(4 - s.length % 4) : '';",
        "    var json = atob(s + pad);",
        "    return JSON.parse(json).user_id;",
        "  } catch (e) { return null; }",
        "}",
        "try { var j = pm.response.json();",
        'if (j.access) { pm.collectionVariables.set("access_token", j.access);',
        "  var uid = uidFromJwt(j.access);",
        '  if (uid) pm.collectionVariables.set("company_user_id", String(uid));',
        "}",
        'if (j.refresh) pm.collectionVariables.set("refresh_token", j.refresh);',
        "} catch (e) {}",
    ]
    jwt_tests_admin = [
        "try { var j = pm.response.json();",
        'if (j.access) pm.collectionVariables.set("access_token", j.access);',
        'if (j.refresh) pm.collectionVariables.set("refresh_token", j.refresh);',
        "} catch (e) {}",
    ]
    login_items = []
    if production:
        login_items.append(
            req(
                "Login - Admin (bundled Vercel demo)",
                "POST",
                "/auth/login/",
                {"email": "{{admin_email}}", "password": "{{admin_password}}"},
                auth="noauth",
                tests=jwt_tests_admin,
                desc=(
                    "Superuser shipped in `deployment/petso.sqlite3` when `DATABASE_URL` is unset. "
                    "Same `admin_email` / `admin_password` work for Django `/admin/`."
                ),
            )
        )
    login_items.extend(
        [
            req(
                "Login - Farmer",
                "POST",
                "/auth/login/",
                {"email": "{{farmer_email}}", "password": "{{farmer_password}}"},
                auth="noauth",
                tests=jwt_tests_farmer,
            ),
            req(
                "Login - Vet",
                "POST",
                "/auth/login/",
                {"email": "{{vet_email}}", "password": "{{vet_password}}"},
                auth="noauth",
                tests=jwt_tests_vet,
            ),
            req(
                "Login - Company",
                "POST",
                "/auth/login/",
                {"email": "{{company_email}}", "password": "{{company_password}}"},
                auth="noauth",
                tests=jwt_tests_company,
            ),
            req(
                "Refresh Token",
                "POST",
                "/auth/token/refresh/",
                {"refresh": "{{refresh_token}}"},
                auth="noauth",
                tests=[
                    "try { var j = pm.response.json();",
                    'if (j.access) pm.collectionVariables.set("access_token", j.access);',
                    "} catch (e) {}",
                ],
            ),
        ]
    )
    items.extend(login_items)
    return items


def readme_folder(*, production: bool):
    if production:
        desc = (
            "**Production (Vercel)** — المتغير `base_url` الافتراضي: `https://petso-api.vercel.app`\n"
            "1. التسجيل يفعّل الحساب مباشرة (`is_verified`) — لا يوجد verify-email / OTP.\n"
            "2. سجّل الدخول أو أنشئ حسابًا ثم تابع المجلدات.\n"
            "3. حساب الـ demo المضمّن مع SQLite: `admin_email` / `admin_password` (انظر `deployment/README.md`) — نفسها لـ `/admin/`.\n"
            "4. حدّث `category_id`, `product_id`, … من ردود الطلبات.\n\n"
            "**Variables:** base_url, admin_*, role emails/passwords, tokens, *_id"
        )
    else:
        desc = (
            "**Suggested order (local)**\n"
            "1. Run server: `python manage.py runserver`\n"
            "2. Register users (pre-verified) → Login (same role) → follow folders\n"
            "3. Update collection variables from responses (ids)\n\n"
            "**Variables**: base_url, emails/passwords, tokens, *_id fields."
        )
    return {
        "name": "00 - README",
        "item": [
            {
                "name": "Overview",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": "{{base_url}}/api/docs/",
                    "description": desc,
                },
            }
        ],
    }


def collection_variables(*, production: bool):
    base_url = "https://petso-api.vercel.app" if production else "http://127.0.0.1:8000"
    vars_ = [
        {"key": "base_url", "value": base_url, "type": "string"},
        {"key": "farmer_email", "value": "farmer.demo@petso.local", "type": "string"},
        {"key": "farmer_password", "value": "DemoPass123!", "type": "string"},
        {"key": "vet_email", "value": "vet.demo@petso.local", "type": "string"},
        {"key": "vet_password", "value": "DemoPass123!", "type": "string"},
        {"key": "company_email", "value": "company.demo@petso.local", "type": "string"},
        {"key": "company_password", "value": "DemoPass123!", "type": "string"},
    ]
    if production:
        vars_.extend(
            [
                {"key": "admin_email", "value": "admin@petso.local", "type": "string"},
                {"key": "admin_password", "value": "PetsoVercel2026!", "type": "string"},
            ]
        )
    vars_.extend(
        [
            {"key": "access_token", "value": "", "type": "string"},
            {"key": "refresh_token", "value": "", "type": "string"},
            {"key": "company_user_id", "value": "1", "type": "string"},
            {"key": "company_profile_id", "value": "1", "type": "string"},
            {"key": "category_id", "value": "1", "type": "string"},
            {"key": "product_id", "value": "1", "type": "string"},
            {"key": "farmer_profile_id", "value": "1", "type": "string"},
            {"key": "flock_id", "value": "1", "type": "string"},
            {"key": "vet_profile_id", "value": "1", "type": "string"},
            {"key": "farmer_user_id", "value": "1", "type": "string"},
            {"key": "vet_user_id", "value": "2", "type": "string"},
            {"key": "post_id", "value": "1", "type": "string"},
            {"key": "chat_id", "value": "1", "type": "string"},
        ]
    )
    return vars_


def append_shared_api_folders(items):
    farmer_items = [
        req("List farmer profiles", "GET", "/farmers/profile/", None),
        req(
            "Create farmer profile",
            "POST",
            "/farmers/profile/",
            {
                "farm_name": "Demo Poultry Farm",
                "farm_location": "Giza, Egypt",
                "farm_address": "Plot 12, Road 9",
                "farm_area": "5.50",
                "flock_size": 500,
                "farm_type": "Broiler",
                "gps_lat": "30.0444",
                "gps_long": "31.2357",
            },
            tests=[
                "if (pm.response.code === 201) {",
                "  var j = pm.response.json();",
                '  if (j.id) pm.collectionVariables.set("farmer_profile_id", String(j.id));',
                "}",
            ],
        ),
        req("List flocks", "GET", "/farmers/flocks/", None),
        req(
            "Create flock",
            "POST",
            "/farmers/flocks/",
            {
                "flock_name": "Batch A-2026",
                "breed": "Ross 308",
                "hatch_date": "2026-01-15",
                "current_age_weeks": 8,
                "total_count": 5000,
                "mortality_count": 12,
                "feed_consumption": "120 kg/day",
                "notes": "Healthy flock",
            },
            tests=[
                "if (pm.response.code === 201) {",
                "  var j = pm.response.json();",
                '  if (j.id) pm.collectionVariables.set("flock_id", String(j.id));',
                "}",
            ],
        ),
    ]
    items.append(folder("02 - Farmer (login as farmer)", farmer_items))

    vet_items = [
        req(
            "List vet profiles",
            "GET",
            "/vets/profiles/",
            None,
            tests=[
                "try {",
                "  var j = pm.response.json();",
                "  var list = j.results !== undefined ? j.results : j;",
                "  if (Array.isArray(list) && list.length && list[0].id) {",
                '    pm.collectionVariables.set("vet_profile_id", String(list[0].id));',
                "  }",
                "} catch (e) {}",
            ],
        ),
        req(
            "Create vet profile",
            "POST",
            "/vets/profiles/",
            {
                "license_number": "VET-LIC-{{$timestamp}}",
                "specialties": "Poultry, Avian medicine",
                "qualifications": "DVM, MSc Poultry Health",
                "clinic_address": "15 Clinic St, Cairo",
                "years_of_experience": 7,
                "available": True,
                "rating": "0.00",
            },
            desc="If 400: backend may need perform_create to bind user to VetProfile.",
        ),
        req("List vet reviews", "GET", "/vets/reviews/", None),
        req(
            "Create vet review (farmer)",
            "POST",
            "/vets/reviews/",
            {
                "vet": "{{vet_profile_id}}",
                "farmer": "{{farmer_profile_id}}",
                "rating": 5,
                "review_text": "Excellent service.",
            },
            desc="Login as farmer; set vet_profile_id and farmer_profile_id.",
        ),
    ]
    items.append(folder("03 - Vet (login as vet)", vet_items))

    company_items = [
        req("List companies", "GET", "/companies/companies/", None),
        req(
            "Create company profile",
            "POST",
            "/companies/companies/",
            {
                "user": "{{company_user_id}}",
                "name": "Petso Feed Co.",
                "description": "Quality poultry feed supplier",
                "website": "https://petso-feed.example.com",
                "contact_email": "{{company_email}}",
                "contact_phone": "+201000000099",
                "business_registration": "BR-2026-001",
                "logo_url": "https://placehold.co/120x120/png",
            },
            desc="company_user_id: Django User PK for role=company (from admin or shell).",
            tests=[
                "if (pm.response.code === 201) {",
                "  var j = pm.response.json();",
                '  if (j.id) pm.collectionVariables.set("company_profile_id", String(j.id));',
                "}",
            ],
        ),
        req("List company analytics", "GET", "/companies/analytics/", None),
    ]
    items.append(folder("04 - Company (login as company or admin)", company_items))

    ecom_items = [
        req("List categories", "GET", "/ecommerce/categories/", None),
        req(
            "Create category",
            "POST",
            "/ecommerce/categories/",
            {"name": "Feed & Nutrition", "description": "Feeds and supplements", "parent": None},
            tests=[
                "if (pm.response.code === 201) {",
                "  var j = pm.response.json();",
                '  if (j.id) pm.collectionVariables.set("category_id", String(j.id));',
                "}",
            ],
        ),
        req(
            "List products",
            "GET",
            "/ecommerce/products/",
            None,
            tests=[
                "try {",
                "  var j = pm.response.json();",
                "  var list = j.results !== undefined ? j.results : j;",
                "  if (Array.isArray(list) && list.length && list[0].id) {",
                '    pm.collectionVariables.set("product_id", String(list[0].id));',
                "  }",
                "} catch (e) {}",
            ],
        ),
        req("Search products", "GET", "/ecommerce/products/?search=feed", None),
        req(
            "Create product",
            "POST",
            "/ecommerce/products/",
            {
                "company": "{{company_profile_id}}",
                "category": "{{category_id}}",
                "sku": "SKU-{{$timestamp}}",
                "name": "Starter Feed 25kg",
                "description": "High protein starter for broilers",
                "unit_price": "450.00",
                "currency": "EGP",
                "stock": 200,
                "is_active": True,
                "requires_prescription": False,
            },
            desc="company_profile_id = Company model PK.",
            tests=[
                "if (pm.response.code === 201) {",
                "  var j = pm.response.json();",
                '  if (j.id) pm.collectionVariables.set("product_id", String(j.id));',
                "}",
            ],
        ),
        req("List my cart", "GET", "/ecommerce/cart/", None),
        req(
            "Cart - Add item",
            "POST",
            "/ecommerce/cart/add_item/",
            {"product_id": "{{product_id}}", "quantity": 2},
            desc="Requires authenticated user (e.g. farmer).",
        ),
    ]
    items.append(
        folder(
            "05 - E-commerce",
            ecom_items,
            "Typical order: Login Company → Create company profile → Create category → Create product. "
            "Then Login Farmer → Cart add_item.",
        )
    )

    order_items = [
        req("List orders", "GET", "/orders/orders/", None),
        req(
            "Create order",
            "POST",
            "/orders/orders/",
            {
                "company": "{{company_profile_id}}",
                "shipping_address": "Farm gate, Giza",
                "total": "900.00",
                "payment_method": "Wallet",
                "prescription_id": None,
                "delivery_date": None,
            },
            desc="Serializer may mark total as read-only; adjust backend if create fails.",
        ),
        req("List order status history", "GET", "/orders/status-history/", None),
    ]
    items.append(folder("06 - Orders", order_items))

    pay_items = [
        req("List my wallet", "GET", "/payments/wallet/", None),
        req("List transactions", "GET", "/payments/transactions/", None),
    ]
    items.append(folder("07 - Payments", pay_items))

    med_items = [
        req("List appointments", "GET", "/medical/appointments/", None),
        req(
            "Create appointment",
            "POST",
            "/medical/appointments/",
            {
                "farmer": "{{farmer_profile_id}}",
                "vet": "{{vet_profile_id}}",
                "slot": None,
                "status": "scheduled",
                "scheduled_start": "2026-05-01T10:00:00Z",
                "scheduled_end": "2026-05-01T10:30:00Z",
            },
            desc="Set vet_profile_id from GET /vets/profiles/",
        ),
        req("List prescriptions", "GET", "/medical/prescriptions/", None),
        req(
            "Create prescription",
            "POST",
            "/medical/prescriptions/",
            {
                "vet": "{{vet_profile_id}}",
                "farmer": "{{farmer_profile_id}}",
                "flock": "{{flock_id}}",
                "diagnosis": "Respiratory stress",
                "prescription_text": "Antibiotic course per label",
                "status": "active",
            },
        ),
    ]
    items.append(folder("08 - Medical", med_items))

    soc_items = [
        req("List posts", "GET", "/social/posts/", None),
        req(
            "Create post",
            "POST",
            "/social/posts/",
            {"content": "Great harvest this week!", "image_url": "https://placehold.co/600x400/png"},
            tests=[
                "if (pm.response.code === 201) {",
                "  var j = pm.response.json();",
                '  if (j.id) pm.collectionVariables.set("post_id", String(j.id));',
                "}",
            ],
        ),
        req("List comments", "GET", "/social/comments/", None),
        req(
            "Create comment",
            "POST",
            "/social/comments/",
            {"post": "{{post_id}}", "content": "Congrats!"},
        ),
    ]
    items.append(folder("09 - Social", soc_items))

    chat_items = [
        req("List chats", "GET", "/chat/chats/", None),
        req(
            "Create chat",
            "POST",
            "/chat/chats/",
            {"user1": "{{farmer_user_id}}", "user2": "{{vet_user_id}}"},
            desc="User PK integers from Django admin / shell.",
        ),
        req("List messages", "GET", "/chat/messages/", None),
        req(
            "Send message",
            "POST",
            "/chat/messages/",
            {"chat": "{{chat_id}}", "message": "Hello from Postman", "is_read": False},
        ),
    ]
    items.append(folder("10 - Chat", chat_items))

    ai_items = [
        req("List AI cases", "GET", "/ai/cases/", None),
        req(
            "Create AI case",
            "POST",
            "/ai/cases/",
            {
                "Title": "Sick broiler batch",
                "symptoms": "Coughing, reduced feed intake",
                "images": [],
                "animal_type": "broiler",
            },
        ),
    ]
    items.append(folder("11 - AI", ai_items))

    sys_items = [
        req("List notifications", "GET", "/system/notifications/", None),
        req(
            "Create notification",
            "POST",
            "/system/notifications/",
            {
                "user": "{{farmer_user_id}}",
                "type": "system",
                "title": "Welcome",
                "body": "Your account is ready.",
                "is_read": False,
                "priority": "medium",
            },
            desc="Set farmer_user_id to the authenticated user's PK (Django User id).",
        ),
        req("Future features (public)", "GET", "/system/future-features/", None, auth="noauth"),
        req("OpenAPI schema", "GET", "/schema/", None, auth="noauth"),
    ]
    items.append(folder("12 - System & schema", sys_items))

    admin_items = [
        req(
            "List users (admin only)",
            "GET",
            "/auth/profile/",
            None,
            desc="Requires is_staff user token.",
        ),
    ]
    items.append(folder("13 - Admin API", admin_items))

def main():
    root = Path(__file__).resolve().parent.parent
    builds = [
        (
            False,
            "Petso_Postman_Collection.json",
            "Petso - Full Scenario (local)",
            "Postman collection for local dev at http://127.0.0.1:8000 (signup is pre-verified).\n"
            "**Roles:** farmer | vet | company | admin\n"
            "Run `python tools/build_postman_collection.py` to regenerate.",
        ),
        (
            True,
            "Petso_Postman_Collection.Production.json",
            "Petso - Production (Vercel)",
            "Postman collection for **https://petso-api.vercel.app** (signup is pre-verified).\n"
            "**Roles:** farmer | vet | company | admin\n"
            "Run `python tools/build_postman_collection.py` to regenerate.",
        ),
    ]

    for production, filename, title, description in builds:
        items = []
        items.append(readme_folder(production=production))
        auth_items = build_auth_items(production=production)
        items.append(
            folder(
                "01 - Authentication",
                auth_items,
                "JWT: Login requests save access_token and refresh_token to collection variables.",
            )
        )
        append_shared_api_folders(items)

        collection = {
            "info": {
                "name": title,
                "description": description,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "auth": {
                "type": "bearer",
                "bearer": [{"key": "token", "value": "{{access_token}}", "type": "string"}],
            },
            "variable": collection_variables(production=production),
            "item": items,
        }

        out = root / filename
        out.write_text(json.dumps(collection, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
