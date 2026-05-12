from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_tenantnotice"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenantprofile",
            name="callable_end_time",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="tenantprofile",
            name="callable_start_time",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="tenantprofile",
            name="contact_by_app",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="tenantprofile",
            name="contact_by_email",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="tenantprofile",
            name="contact_by_phone",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="tenantprofile",
            name="contact_by_sms",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="EmergencyContact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("contact_name", models.CharField(blank=True, max_length=100)),
                ("phone_number", models.CharField(max_length=20)),
                ("relationship", models.CharField(blank=True, max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="emergency_contacts",
                        to="accounts.tenantprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TenantPhoneNumber",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone_number", models.CharField(max_length=20, unique=True)),
                ("is_primary", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="phone_numbers",
                        to="accounts.tenantprofile",
                    ),
                ),
            ],
        ),
    ]
