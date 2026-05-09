"""
Management command to seed categories and products with images.

Usage:
    python manage.py seed_ecommerce
    python manage.py seed_ecommerce --company-id 1     # use specific company
    python manage.py seed_ecommerce --clear            # delete existing data first
"""
import io
import urllib.request
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from apps.companies.models import Company
from apps.ecommerce.models import Category, Product, ProductImage


CATEGORIES = [
    {
        "name": "Feed & Nutrition",
        "description": "Poultry feeds, supplements, vitamins and minerals for healthy flock growth.",
        "products": [
            {
                "name": "Starter Feed 25kg",
                "sku": "FEED-START-25",
                "description": "High-protein (22%) starter crumble for broiler chicks aged 0–14 days. Supports rapid early growth.",
                "unit_price": "450.00",
                "currency": "EGP",
                "stock": 200,
                "requires_prescription": False,
                "image_url": "https://placehold.co/400x400/4CAF50/ffffff?text=Starter+Feed",
            },
            {
                "name": "Grower Feed 50kg",
                "sku": "FEED-GROW-50",
                "description": "Balanced grower pellets (19% protein) for broilers aged 15–28 days. Optimises feed conversion ratio.",
                "unit_price": "780.00",
                "currency": "EGP",
                "stock": 150,
                "requires_prescription": False,
                "image_url": "https://placehold.co/400x400/8BC34A/ffffff?text=Grower+Feed",
            },
            {
                "name": "Finisher Feed 50kg",
                "sku": "FEED-FINISH-50",
                "description": "Energy-rich finisher pellets (17% protein) for broilers aged 29+ days. Maximises weight gain before harvest.",
                "unit_price": "760.00",
                "currency": "EGP",
                "stock": 180,
                "requires_prescription": False,
                "image_url": "https://placehold.co/400x400/CDDC39/ffffff?text=Finisher+Feed",
            },
            {
                "name": "Layer Feed 25kg",
                "sku": "FEED-LAYER-25",
                "description": "Calcium-enriched layer mash for laying hens. Promotes strong shells and high egg production.",
                "unit_price": "420.00",
                "currency": "EGP",
                "stock": 300,
                "requires_prescription": False,
                "image_url": "https://placehold.co/400x400/FFC107/ffffff?text=Layer+Feed",
            },
            {
                "name": "Vitamin & Electrolyte Sachet 1kg",
                "sku": "SUPP-VIT-1KG",
                "description": "Water-soluble vitamins A, D3, E, B-complex with electrolytes. Essential during heat stress or illness.",
                "unit_price": "95.00",
                "currency": "EGP",
                "stock": 500,
                "requires_prescription": False,
                "image_url": "https://placehold.co/400x400/FF9800/ffffff?text=Vitamins",
            },
        ],
    },
    {
        "name": "Vaccines & Medications",
        "description": "Licensed vaccines, antibiotics and antiparasitic treatments for poultry flocks.",
        "products": [
            {
                "name": "Newcastle Disease Vaccine (100 doses)",
                "sku": "VAC-ND-100",
                "description": "Live attenuated La Sota strain. Eye-drop or drinking-water application. Store at 2–8 °C.",
                "unit_price": "65.00",
                "currency": "EGP",
                "stock": 400,
                "requires_prescription": True,
                "image_url": "https://placehold.co/400x400/F44336/ffffff?text=ND+Vaccine",
            },
            {
                "name": "Infectious Bronchitis Vaccine (500 doses)",
                "sku": "VAC-IB-500",
                "description": "H120 + Ma5 bivalent live vaccine. Spray or drinking water. Broad-spectrum IB protection.",
                "unit_price": "120.00",
                "currency": "EGP",
                "stock": 250,
                "requires_prescription": True,
                "image_url": "https://placehold.co/400x400/E91E63/ffffff?text=IB+Vaccine",
            },
            {
                "name": "Gumboro (IBD) Vaccine (1000 doses)",
                "sku": "VAC-IBD-1000",
                "description": "Intermediate plus strain. Drinking-water administration at day 14. Protects bursa of Fabricius.",
                "unit_price": "180.00",
                "currency": "EGP",
                "stock": 200,
                "requires_prescription": True,
                "image_url": "https://placehold.co/400x400/9C27B0/ffffff?text=IBD+Vaccine",
            },
            {
                "name": "Doxycycline Antibiotic 100g",
                "sku": "MED-DOX-100G",
                "description": "Broad-spectrum tetracycline antibiotic powder. Water-soluble. Treats CRD, E. coli infections.",
                "unit_price": "85.00",
                "currency": "EGP",
                "stock": 600,
                "requires_prescription": True,
                "image_url": "https://placehold.co/400x400/3F51B5/ffffff?text=Doxycycline",
            },
        ],
    },
    {
        "name": "Equipment & Biosecurity",
        "description": "Drinkers, feeders, heaters, disinfectants and protective equipment for the poultry house.",
        "products": [
            {
                "name": "Automatic Nipple Drinker Line (10m)",
                "sku": "EQ-DRINK-10M",
                "description": "PVC nipple drinker line with pressure regulator. Suitable for 500 broilers. Easy snap-fit assembly.",
                "unit_price": "1200.00",
                "currency": "EGP",
                "stock": 50,
                "requires_prescription": False,
                "image_url": "https://placehold.co/400x400/00BCD4/ffffff?text=Nipple+Drinker",
            },
            {
                "name": "Pan Feeder 7kg Capacity",
                "sku": "EQ-FEED-PAN7",
                "description": "Hanging pan feeder with adjustable flow gate. Reduces feed wastage by up to 30%.",
                "unit_price": "320.00",
                "currency": "EGP",
                "stock": 120,
                "requires_prescription": False,
                "image_url": "https://placehold.co/400x400/009688/ffffff?text=Pan+Feeder",
            },
            {
                "name": "Gas Brooder Heater 1500W",
                "sku": "EQ-HEAT-GAS",
                "description": "Infrared gas brooder for chick brooding. Covers 50 m². Built-in thermostat and safety valve.",
                "unit_price": "2500.00",
                "currency": "EGP",
                "stock": 30,
                "requires_prescription": False,
                "image_url": "https://placehold.co/400x400/FF5722/ffffff?text=Gas+Brooder",
            },
            {
                "name": "Virkon S Disinfectant 5kg",
                "sku": "BIO-VIRKON-5KG",
                "description": "Broad-spectrum virucidal and bactericidal disinfectant powder. Mix 1:100 for routine spray application.",
                "unit_price": "950.00",
                "currency": "EGP",
                "stock": 80,
                "requires_prescription": False,
                "image_url": "https://placehold.co/400x400/607D8B/ffffff?text=Virkon+S",
            },
        ],
    },
    {
        "name": "Diagnostic Tools",
        "description": "Field-test kits, scales and monitoring devices for flock health assessment.",
        "products": [
            {
                "name": "Digital Poultry Scale 30kg",
                "sku": "DIAG-SCALE-30",
                "description": "Stainless-steel platform scale. 10 g resolution. Battery + AC powered. Essential for flock weight monitoring.",
                "unit_price": "1800.00",
                "currency": "EGP",
                "stock": 25,
                "requires_prescription": False,
                "image_url": "https://placehold.co/400x400/795548/ffffff?text=Scale",
            },
            {
                "name": "Avian Influenza Rapid Test Kit (10 tests)",
                "sku": "DIAG-AI-KIT10",
                "description": "Lateral-flow antigen test for H5/H7 AI strains. Results in 15 minutes. WOAH-approved.",
                "unit_price": "350.00",
                "currency": "EGP",
                "stock": 100,
                "requires_prescription": False,
                "image_url": "https://placehold.co/400x400/9E9E9E/ffffff?text=AI+Test+Kit",
            },
        ],
    },
]


def _download_image(url: str, filename: str):
    """Download image from URL and return a ContentFile."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        return ContentFile(data, name=filename)
    except Exception as exc:
        return None


class Command(BaseCommand):
    help = "Seed ecommerce categories and products with placeholder images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--company-id",
            type=int,
            default=None,
            help="Company PK to assign products to. Defaults to the first company found.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing products and categories before seeding.",
        )
        parser.add_argument(
            "--no-images",
            action="store_true",
            help="Skip downloading images (faster, good for offline environments).",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing products and categories...")
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared."))

        # Resolve company
        company_id = options["company_id"]
        if company_id:
            try:
                company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                raise CommandError(f"Company with id={company_id} does not exist.")
        else:
            company = Company.objects.first()
            if company is None:
                raise CommandError(
                    "No company found. Create one first:\n"
                    "  1. Register a user with role=company\n"
                    "  2. POST /api/companies/companies/ to create the company profile\n"
                    "  3. Re-run: python manage.py seed_ecommerce --company-id <id>"
                )

        self.stdout.write(f"Using company: {company} (id={company.pk})")
        skip_images = options["no_images"]
        total_products = 0

        for cat_data in CATEGORIES:
            cat, cat_created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={"description": cat_data["description"]},
            )
            action = "Created" if cat_created else "Found"
            self.stdout.write(f"  {action} category: {cat.name}")

            for p_data in cat_data["products"]:
                product, p_created = Product.objects.get_or_create(
                    sku=p_data["sku"],
                    defaults={
                        "company": company,
                        "category": cat,
                        "name": p_data["name"],
                        "description": p_data["description"],
                        "unit_price": p_data["unit_price"],
                        "currency": p_data["currency"],
                        "stock": p_data["stock"],
                        "is_active": True,
                        "requires_prescription": p_data["requires_prescription"],
                    },
                )
                p_action = "Created" if p_created else "Skipped (exists)"
                self.stdout.write(f"    {p_action}: {product.name}")

                # Add image only for new products (or if none exists)
                if p_created and not skip_images and not product.images.exists():
                    img_url = p_data.get("image_url")
                    if img_url:
                        safe_name = product.sku.lower().replace("-", "_") + ".png"
                        self.stdout.write(f"      Downloading image from {img_url} ...")
                        content_file = _download_image(img_url, safe_name)
                        if content_file:
                            ProductImage.objects.create(
                                product=product,
                                image=content_file,
                                alt_text=product.name,
                                position=0,
                            )
                            self.stdout.write(self.style.SUCCESS("      Image saved."))
                        else:
                            # Fallback: store URL only (no file download needed)
                            ProductImage.objects.create(
                                product=product,
                                image_url=img_url,
                                alt_text=product.name,
                                position=0,
                            )
                            self.stdout.write(self.style.WARNING("      Download failed — stored URL instead."))

                if p_created:
                    total_products += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Seeded {len(CATEGORIES)} categories and {total_products} products."
            )
        )
