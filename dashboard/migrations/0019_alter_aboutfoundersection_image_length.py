from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0018_something"),
    ]

    operations = [
        migrations.AlterField(
            model_name="aboutfoundersection",
            name="image",
            field=models.ImageField(
                upload_to="about/founder/",
                max_length=500,
                blank=True,
                null=True,
            ),
        ),
    ]
