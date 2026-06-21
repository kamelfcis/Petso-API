from django.db import migrations


def approve_existing_posts(apps, schema_editor):
    Post = apps.get_model("social", "Post")
    Post.objects.all().update(status="approved")


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0004_post_status"),
    ]

    operations = [
        migrations.RunPython(approve_existing_posts, migrations.RunPython.noop),
    ]
