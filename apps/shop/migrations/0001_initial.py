# Generated by Django 5.1.5 on 2025-02-08 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BotUsers",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "telegram_id",
                    models.BigIntegerField(unique=True, verbose_name="Telegram ID"),
                ),
                (
                    "username",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Foydalanuvchi nomi",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Ism"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Familiya"
                    ),
                ),
                (
                    "full_name",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Ism va Familiya",
                    ),
                ),
                (
                    "phone",
                    models.BigIntegerField(
                        blank=True, null=True, unique=True, verbose_name="Telefon raqam"
                    ),
                ),
                (
                    "language_code",
                    models.CharField(
                        choices=[("uz", "O'zbek tili"), ("ru", "Rus tili")],
                        default="uz",
                        max_length=10,
                        verbose_name="Til",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Faolmi")),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("moderator", "Moderator"),
                            ("user", "Foydalanuvchi"),
                        ],
                        default="user",
                        max_length=10,
                        verbose_name="Rol",
                    ),
                ),
            ],
            options={
                "verbose_name": "Bot Foydalanuvchisi",
                "verbose_name_plural": "Bot Foydalanuvchilari",
                "db_table": "bot_users",
                "ordering": ["-created_at"],
            },
        ),
    ]
