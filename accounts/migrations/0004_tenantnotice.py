from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_loginsession_loginhistory"),
    ]

    operations = [
        migrations.CreateModel(
            name="TenantNotice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sender_company", models.CharField(max_length=50)),
                ("target_filter_type", models.CharField(max_length=50)),
                ("subject", models.CharField(max_length=200)),
                ("body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_unread", models.BooleanField(default=True)),
                ("is_starred", models.BooleanField(default=False)),
                ("is_trash", models.BooleanField(default=False)),
                (
                    "recipient_tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notices",
                        to="accounts.tenantprofile",
                    ),
                ),
            ],
        ),
    ]
