# Generated manually to create FeaturedProductSection table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_order_payment_status_order_phonepe_merchant_order_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeaturedProductSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(default='Featured Products', max_length=150)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Featured Product Section',
                'verbose_name_plural': 'Featured Product Section',
            },
        ),
    ]
