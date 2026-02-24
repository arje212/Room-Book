from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_auto_20250924_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='passwordchangerequest',
            name='notified',
            field=models.BooleanField(default=False),
        ),
    ]
