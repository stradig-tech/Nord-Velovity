from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chauffeur', '0003_alter_vehiclephoto_options_and_more'),
    ]

    operations = [
        # --- STEP 1: Rename existing fields (preserves data) ---
        migrations.RenameField(
            model_name='fixedroute',
            old_name='origin_name',
            new_name='pickup_name',
        ),
        migrations.RenameField(
            model_name='fixedroute',
            old_name='origin_lat',
            new_name='pickup_lat',
        ),
        migrations.RenameField(
            model_name='fixedroute',
            old_name='origin_lng',
            new_name='pickup_lng',
        ),
        migrations.RenameField(
            model_name='fixedroute',
            old_name='destination_name',
            new_name='dropoff_name',
        ),
        migrations.RenameField(
            model_name='fixedroute',
            old_name='destination_lat',
            new_name='dropoff_lat',
        ),
        migrations.RenameField(
            model_name='fixedroute',
            old_name='destination_lng',
            new_name='dropoff_lng',
        ),

        # --- STEP 2: Add new fields ---
        migrations.AddField(
            model_name='fixedroute',
            name='transfer_type',
            field=models.CharField(
                choices=[
                    ('AIRPORT', 'Airport Transfer'),
                    ('CITY', 'City-to-City Transfer'),
                    ('HOTEL', 'Hotel Transfer'),
                    ('RESORT', 'Resort Transfer'),
                    ('ATTRACTION', 'Attraction Transfer'),
                    ('CUSTOM', 'Custom Transfer'),
                ],
                default='AIRPORT',
                help_text='Category of this fixed price transfer',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='fixedroute',
            name='passenger_capacity',
            field=models.PositiveIntegerField(default=4, help_text='Max passengers for this transfer route'),
        ),
        migrations.AddField(
            model_name='fixedroute',
            name='luggage_capacity',
            field=models.PositiveIntegerField(default=2, help_text='Max luggage pieces for this transfer route'),
        ),
        migrations.AddField(
            model_name='fixedroute',
            name='description',
            field=models.TextField(blank=True, help_text='Customer-facing description of this transfer route'),
        ),
        migrations.AddField(
            model_name='fixedroute',
            name='notes',
            field=models.TextField(blank=True, help_text='Internal admin notes'),
        ),

        # --- STEP 3: Update field help_text and max_length on renamed fields ---
        migrations.AlterField(
            model_name='fixedroute',
            name='pickup_name',
            field=models.CharField(help_text='Pickup location name, e.g. Helsinki-Vantaa Airport, Hotel Kämp, Santa Claus Village', max_length=200),
        ),
        migrations.AlterField(
            model_name='fixedroute',
            name='dropoff_name',
            field=models.CharField(help_text='Drop-off location name', max_length=200),
        ),
        migrations.AlterField(
            model_name='fixedroute',
            name='name',
            field=models.CharField(help_text='e.g. Helsinki Airport → City Center, Levi Resort → Kittilä Airport', max_length=200),
        ),

        # --- STEP 4: Update model Meta ---
        migrations.AlterModelOptions(
            name='fixedroute',
            options={
                'ordering': ['transfer_type', 'name'],
                'verbose_name': 'Fixed Price Transfer',
                'verbose_name_plural': 'Fixed Price Transfers',
            },
        ),
    ]
