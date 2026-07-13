from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# 1. Model Bidang (Departemen/Unit Kerja)
class Bidang(models.Model):
    nama = models.CharField(max_length=100, unique=True, verbose_name="Nama Bidang")
    
    class Meta:
        verbose_name_plural = "Bidang"

    def __str__(self):
        return self.nama

# 2. Custom User Model
class CustomUser(AbstractUser):
    bidang = models.ForeignKey(
        Bidang, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users',
        verbose_name="Asal Bidang"
    )
    foto_profil = models.ImageField(upload_to='profil/', null=True, blank=True, verbose_name="Foto Profil")
    nomor_telepon = models.CharField(max_length=20, null=True, blank=True, verbose_name="Nomor Telepon")
    is_teknisi = models.BooleanField(default=False, verbose_name="Status Teknisi")
    is_verified_teknisi = models.BooleanField(default=False, verbose_name="Teknisi Terverifikasi")
    
    def __str__(self):
        return self.get_full_name() or self.username

# 3. Model Laporan (Tiket Pengaduan)
class Laporan(models.Model):
    STATUS_CHOICES = [
        ('menunggu', 'Menunggu'),
        ('diproses', 'Diproses'),
        ('selesai', 'Selesai'),
    ]

    KATEGORI_CHOICES = [
        ('jaringan_terputus', 'Jaringan Terputus / Mati Total'),
        ('koneksi_lambat', 'Koneksi Lambat / Tidak Stabil'),
        ('pemasangan_baru', 'Pemasangan Jaringan Baru'),
        ('kendala_intranet', 'Kendala Akses Intranet / Aplikasi Lokal'),
        ('kerusakan_fisik', 'Kerusakan Fisik Perangkat Jaringan'),
        ('relokasi_titik', 'Relokasi Titik Jaringan'),
        ('permintaan_konfigurasi', 'Permintaan Konfigurasi Jaringan'),
    ]

    PRIORITAS_CHOICES = [
        ('level_1', 'Level 1'),
        ('level_2', 'Level 2'),
        ('level_3', 'Level 3'),
        ('level_4', 'Level 4'),
    ]

    # Informasi Utama
    judul = models.CharField(max_length=200, verbose_name="Judul Masalah")
    kategori = models.CharField(max_length=50, choices=KATEGORI_CHOICES, verbose_name="Kategori Masalah")
    deskripsi = models.TextField(verbose_name="Deskripsi Detail")
    lampiran = models.FileField(upload_to='lampiran/', blank=True, null=True, verbose_name="Lampiran")
    
    # Relasi
    pelapor = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='laporan_saya',
        verbose_name="Nama Pelapor"
    )
    bidang = models.ForeignKey(
        Bidang, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='laporan_bidang',
        verbose_name="Bidang Pelapor"
    )
    teknisi_bertugas = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tugas_teknisi',
        limit_choices_to={'is_teknisi': True},
        verbose_name="Teknisi Bertugas"
    )

    # Status & Resolusi
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu', verbose_name="Status Laporan")
    solusi = models.TextField(blank=True, null=True, verbose_name="Solusi yang Diberikan")
    bukti_penyelesaian = models.ImageField(upload_to='bukti/', null=True, blank=True, verbose_name="Foto Bukti Penyelesaian")
    estimasi_mulai = models.DateTimeField(blank=True, null=True, verbose_name="Estimasi Mulai Dikerjakan")
    estimasi_penanganan = models.DateTimeField(blank=True, null=True, verbose_name="Estimasi Penanganan")
    prioritas = models.CharField(max_length=20, choices=PRIORITAS_CHOICES, default='level_1', verbose_name="Prioritas Laporan")
    
    # Rating & Kepuasan
    rating = models.IntegerField(null=True, blank=True, verbose_name="Rating (1-5)")
    ulasan = models.TextField(blank=True, null=True, verbose_name="Ulasan Pelapor")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Tanggal Lapor")
    waktu_diambil = models.DateTimeField(blank=True, null=True, verbose_name="Waktu Mulai Dikerjakan")
    waktu_selesai = models.DateTimeField(blank=True, null=True, verbose_name="Waktu Selesai")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Terakhir Diupdate")

    class Meta:
        verbose_name_plural = "Laporan"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_status_display()}] {self.judul} - {self.pelapor.username}"
        
    @property
    def is_sla_warning(self):
        if self.status in ['menunggu', 'diproses']:
            return (timezone.now() - self.created_at).total_seconds() > 86400 # 24 hours
        return False
