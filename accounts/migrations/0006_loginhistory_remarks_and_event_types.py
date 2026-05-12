from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_contact_settings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="loginhistory",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("IN", "ログイン"),
                    ("OUT", "ログアウト"),
                    ("TEL", "電話番号"),
                    ("MAIL", "メールアドレス"),
                    ("PASS", "パスワード"),
                    ("EMG", "緊急連絡先"),
                ],
                max_length=4,
            ),
        ),
        migrations.AddField(
            model_name="loginhistory",
            name="remarks",
            field=models.TextField(blank=True, default=""),
        ),
    ]
