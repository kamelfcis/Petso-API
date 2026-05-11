from django.db import migrations, models


def set_existing_users_verified(apps, schema_editor):
    """All users that existed before this migration are considered already verified."""
    User = apps.get_model('users', 'User')
    User.objects.all().update(is_email_verified=True)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_email_verified',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.RunPython(set_existing_users_verified, migrations.RunPython.noop),
    ]
