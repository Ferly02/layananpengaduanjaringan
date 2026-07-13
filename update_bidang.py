import os
import sys
import django

sys.path.append('c:\\sinar')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pengaduan.models import CustomUser, Bidang, Laporan

# Find the Bidang 'Persandian'
try:
    persandian = Bidang.objects.get(nama__iexact='Persandian')
except Bidang.DoesNotExist:
    print("Bidang Persandian tidak ditemukan.")
    sys.exit()

# Find user by first_name/last_name or username
users = CustomUser.objects.filter(first_name__icontains='Grace')
if not users.exists():
    users = CustomUser.objects.filter(username__icontains='grace')
if not users.exists():
    # If full name is used somewhere
    users = CustomUser.objects.all()
    user = None
    for u in users:
        if 'grace' in u.get_full_name().lower() or 'oktaviani' in u.get_full_name().lower():
            user = u
            break
else:
    user = users.first()

if user:
    # Update User Bidang
    user.bidang = persandian
    user.save()
    print(f"Updated bidang for user {user.username} to Persandian.")
    
    # Update Laporan Bidang
    laporans = Laporan.objects.filter(pelapor=user)
    updated_count = laporans.update(bidang=persandian)
    print(f"Updated {updated_count} laporans for user {user.username}.")
else:
    print("User Grace Oktaviani not found.")
