import os
import sys
import django

sys.path.append('c:\\sinar')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pengaduan.models import Bidang

bidang_list = [
    'Sekretariat',
    'Informasi dan Komunikasi Publik',
    'Teknologi Informasi dan Komunikasi',
    'Statistik',
    'Persandian'
]

for b in bidang_list:
    obj, created = Bidang.objects.get_or_create(nama=b)
    if created:
        print(f"Created: {b}")
    else:
        print(f"Already exists: {b}")
