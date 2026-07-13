from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Bidang, Laporan

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'bidang', 'is_teknisi', 'is_verified_teknisi', 'is_staff')
    list_filter = ('is_teknisi', 'is_verified_teknisi', 'bidang', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    # Menambahkan custom fields ke UserAdmin fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('Informasi Tambahan', {'fields': ('bidang', 'foto_profil', 'nomor_telepon', 'is_teknisi', 'is_verified_teknisi')}),
    )

@admin.register(Bidang)
class BidangAdmin(admin.ModelAdmin):
    list_display = ('nama',)
    search_fields = ('nama',)

@admin.register(Laporan)
class LaporanAdmin(admin.ModelAdmin):
    list_display = ('judul', 'pelapor', 'bidang', 'status', 'teknisi_bertugas', 'created_at')
    list_filter = ('status', 'kategori', 'bidang', 'teknisi_bertugas')
    search_fields = ('judul', 'deskripsi', 'pelapor__username')
    date_hierarchy = 'created_at'
