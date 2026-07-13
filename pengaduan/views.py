from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
import csv
from django.utils import timezone
import datetime
import calendar
from django.db.models import Q, Avg
from .models import Laporan, Bidang

import urllib.request
import urllib.parse
import json
from django.conf import settings

User = get_user_model()
# --- AUTHENTICATION VIEWS ---

def login_admin(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Username atau password salah, atau Anda bukan Admin.')
    return render(request, 'login-admin.html')

def login_user(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None and not user.is_staff:
            if getattr(user, 'is_teknisi', False) and not getattr(user, 'is_verified_teknisi', False):
                messages.error(request, 'Akun Teknisi Anda sedang menunggu verifikasi Admin.')
            else:
                login(request, user)
                return redirect('dashboard')
        elif user is not None and user.is_staff:
            messages.error(request, 'Silakan login di halaman admin.')
        else:
            messages.error(request, 'Username atau password salah.')
    return render(request, 'login-user.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        req = urllib.request.Request('https://www.google.com/recaptcha/api/siteverify', urllib.parse.urlencode(data).encode('utf-8'))
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        
        if not result.get('success'):
            messages.error(request, 'Silakan centang kotak "I\'m not a robot" terlebih dahulu.')
            return render(request, 'register.html', {'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY})

        nama_lengkap = request.POST.get('nama_lengkap')
        username_email = request.POST.get('username_email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Kata sandi dan konfirmasi kata sandi tidak cocok.')
            return render(request, 'register.html', {'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY})
            
        if User.objects.filter(username=username_email).exists():
            messages.error(request, 'Username/Email sudah digunakan.')
            return render(request, 'register.html', {'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY})
            
        # Create user (Hanya User Biasa/Pelapor)
        user = User.objects.create_user(
            username=username_email,
            email=username_email if '@' in username_email else '',
            password=password,
            first_name=nama_lengkap,
            is_teknisi=False
        )
        user.save()
        
        messages.success(request, 'Pendaftaran berhasil. Silakan login.')
        return redirect('login_user')
        
    return render(request, 'register.html', {'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY})

def lupa_password(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username_email = request.POST.get('username_email')
        
        # Here in a real application, you'd send an email with a reset link.
        # For now, we will just show a success message simulating that behavior.
        if User.objects.filter(Q(username=username_email) | Q(email=username_email)).exists():
            messages.success(request, 'Tautan untuk mengatur ulang kata sandi telah dikirim ke email Anda. (Simulasi: fitur email belum dikonfigurasi)')
        else:
            # For security, often applications display the same message even if email doesn't exist,
            # but to be helpful here we can show an error or the same success message.
            messages.success(request, 'Jika email/username terdaftar, tautan reset akan dikirimkan. (Simulasi)')
            
        return redirect('lupa_password')
        
    return render(request, 'lupa_password.html')

def logout_view(request):
    is_admin = request.user.is_authenticated and request.user.is_staff
    logout(request)
    if is_admin:
        return redirect('login_admin')
    return redirect('login_user')

@login_required
def buat_teknisi(request):
    if not request.user.is_staff:
        return redirect('dashboard')
        
    if request.method == 'POST':
        nama_lengkap = request.POST.get('nama_lengkap')
        username_email = request.POST.get('username_email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Kata sandi dan konfirmasi tidak cocok.')
            return render(request, 'buat_teknisi.html')
            
        if User.objects.filter(username=username_email).exists():
            messages.error(request, 'Username/Email sudah digunakan oleh akun lain.')
            return render(request, 'buat_teknisi.html')
            
        # Create user teknisi
        user = User.objects.create_user(
            username=username_email,
            email=username_email if '@' in username_email else '',
            password=password,
            first_name=nama_lengkap,
            is_teknisi=True,
            is_verified_teknisi=True
        )
        user.save()
        
        messages.success(request, f'Akun Teknisi "{nama_lengkap}" berhasil dibuat.')
        return redirect('dashboard')
        
    return render(request, 'buat_teknisi.html')


# --- ADMIN VIEWS ---

@login_required
def dashboard(request):
    if request.user.is_staff:
        total = Laporan.objects.count()
        menunggu = Laporan.objects.filter(status='menunggu').count()
        diproses = Laporan.objects.filter(status='diproses').count()
        selesai = Laporan.objects.filter(status='selesai').count()
        
        unverified_teknisi = User.objects.filter(is_teknisi=True, is_verified_teknisi=False)
    
        context = {
            'total': total,
            'menunggu': menunggu,
            'diproses': diproses,
            'selesai': selesai,
            'unverified_teknisi': unverified_teknisi,
        }
        return render(request, 'dashboard.html', context)
    elif getattr(request.user, 'is_teknisi', False):
        menunggu_list = Laporan.objects.filter(status='menunggu').order_by('created_at')
        tugas_saya = Laporan.objects.filter(teknisi_bertugas=request.user, status='diproses').order_by('-created_at')
        riwayat_selesai = Laporan.objects.filter(teknisi_bertugas=request.user, status='selesai').order_by('-created_at')
        
        avg_rating = riwayat_selesai.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg']
        if avg_rating is None:
            avg_rating = 0
            
        context = {
            'menunggu_list': menunggu_list,
            'tugas_saya': tugas_saya,
            'riwayat_selesai': riwayat_selesai,
            'count_menunggu': menunggu_list.count(),
            'count_tugas': tugas_saya.count(),
            'count_selesai': riwayat_selesai.count(),
            'avg_rating': round(avg_rating, 1),
        }
        return render(request, 'teknisi_dashboard.html', context)
    else:
        menunggu = Laporan.objects.filter(pelapor=request.user, status='menunggu').count()
        diproses = Laporan.objects.filter(pelapor=request.user, status='diproses').count()
        selesai = Laporan.objects.filter(pelapor=request.user, status='selesai').count()
    
        context = {
            'menunggu': menunggu,
            'diproses': diproses,
            'selesai': selesai,
        }
        return render(request, 'user_dashboard.html', context)

@login_required
def laporan_list(request):
    # Fetch all, sorted by created_at desc (as defined in Meta ordering)
    laporans = Laporan.objects.all()
    
    # Simple search & filter
    q = request.GET.get('q')
    status = request.GET.get('status')
    kategori = request.GET.get('kategori')
    
    if q:
        laporans = laporans.filter(
            Q(judul__icontains=q) |
            Q(bidang__nama__icontains=q) |
            Q(pelapor__username__icontains=q) |
            Q(pelapor__first_name__icontains=q) |
            Q(pelapor__last_name__icontains=q)
        )
    if status:
        laporans = laporans.filter(status=status)
    if kategori:
        laporans = laporans.filter(kategori=kategori)

    context = {
        'laporans': laporans,
    }
    return render(request, 'laporan_list.html', context)

@login_required
def buat_laporan(request):
    if request.user.is_staff:
        messages.error(request, 'Admin tidak perlu membuat laporan.')
        return redirect('dashboard')
        
    if request.method == 'POST':
        judul = request.POST.get('judul')
        kategori = request.POST.get('kategori')
        bidang_id = request.POST.get('bidang')
        deskripsi = request.POST.get('deskripsi')
        lampiran = request.FILES.get('lampiran')
        tanggal_lapor = request.POST.get('tanggal_lapor')
        
        bidang = Bidang.objects.filter(id=bidang_id).first() if bidang_id else None
        
        laporan = Laporan(
            judul=judul,
            kategori=kategori,
            bidang=bidang,
            deskripsi=deskripsi,
            lampiran=lampiran,
            pelapor=request.user
        )
        if tanggal_lapor:
            laporan.created_at = tanggal_lapor
            
        laporan.save()
        
        messages.success(request, 'Laporan berhasil dibuat.')
        return redirect('status_laporan')
        
    context = {
        'kategori_choices': Laporan.KATEGORI_CHOICES,
        'bidang_list': Bidang.objects.all()
    }
    return render(request, 'buat_laporan.html', context)

@login_required
def status_laporan(request):
    if request.user.is_staff:
        return redirect('dashboard')
        
    laporans = Laporan.objects.filter(pelapor=request.user)
    
    # Filter
    q = request.GET.get('q')
    status = request.GET.get('status')
    kategori = request.GET.get('kategori')
    
    if q:
        from django.db.models import Q
        laporans = laporans.filter(
            Q(judul__icontains=q) |
            Q(bidang__nama__icontains=q)
        )
    if status:
        laporans = laporans.filter(status=status)
    if kategori:
        laporans = laporans.filter(kategori=kategori)
        
    context = {
        'laporans': laporans,
        'status_choices': Laporan.STATUS_CHOICES,
        'kategori_choices': Laporan.KATEGORI_CHOICES,
    }
    return render(request, 'status_laporan.html', context)

@login_required
def edit_profil(request):
    if request.method == 'POST':
        if request.POST.get('ubah_password'):
            kata_sandi_lama = request.POST.get('kata_sandi_lama')
            kata_sandi_baru = request.POST.get('kata_sandi_baru')
            konfirmasi_kata_sandi = request.POST.get('konfirmasi_kata_sandi')
            
            if not request.user.check_password(kata_sandi_lama):
                messages.error(request, 'Password lama tidak sesuai.')
            elif kata_sandi_baru != konfirmasi_kata_sandi:
                messages.error(request, 'Konfirmasi password baru tidak cocok.')
            elif len(kata_sandi_baru) < 8:
                messages.error(request, 'Password baru harus minimal 8 karakter.')
            else:
                request.user.set_password(kata_sandi_baru)
                request.user.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password berhasil diperbarui.')
            return redirect('edit_profil')
        else:
            nama_lengkap = request.POST.get('nama_lengkap')
            nomor_telepon = request.POST.get('nomor_telepon')
            foto_profil = request.FILES.get('foto_profil')
            
            updated = False
            
            if foto_profil:
                request.user.foto_profil = foto_profil
                updated = True
                
            if nama_lengkap and nama_lengkap != request.user.first_name:
                request.user.first_name = nama_lengkap
                updated = True
                
            if nomor_telepon is not None and nomor_telepon != request.user.nomor_telepon:
                request.user.nomor_telepon = nomor_telepon
                updated = True
                
            if updated:
                request.user.save()
                messages.success(request, 'Profil berhasil diperbarui.')
            else:
                messages.info(request, 'Tidak ada perubahan yang disimpan.')
            return redirect('edit_profil')

    if request.user.is_staff:
        base_template = 'base_admin.html'
    elif getattr(request.user, 'is_teknisi', False):
        base_template = 'base_teknisi.html'
    else:
        base_template = 'base_user.html'
        
    context = {'base_template': base_template}
    return render(request, 'edit_profil.html', context)

@login_required
def laporan_detail(request, id):
    laporan = get_object_or_404(Laporan, id=id)
    
    is_teknisi = getattr(request.user, 'is_teknisi', False)
    
    # Ensure user can only see their own report unless they are staff or teknisi
    if not request.user.is_staff and not is_teknisi and laporan.pelapor != request.user:
        return redirect('dashboard')
        
    if request.method == 'POST':
        if request.user.is_staff or is_teknisi:
            new_status = request.POST.get('status')
            new_solusi = request.POST.get('solusi')
            estimasi_mulai = request.POST.get('estimasi_mulai')
            estimasi_penanganan = request.POST.get('estimasi_penanganan')
            bukti_penyelesaian = request.FILES.get('bukti_penyelesaian')
            
            if new_status:
                if new_status == 'diproses' and laporan.status != 'diproses':
                    if not laporan.waktu_diambil:
                        laporan.waktu_diambil = timezone.now()
                    laporan.waktu_selesai = None
                elif new_status == 'selesai' and laporan.status != 'selesai':
                    laporan.waktu_selesai = timezone.now()
                    if not laporan.waktu_diambil:
                        laporan.waktu_diambil = timezone.now()
                elif new_status == 'menunggu':
                    laporan.waktu_selesai = None
                    laporan.waktu_diambil = None
                laporan.status = new_status
                
            if new_solusi is not None:
                laporan.solusi = new_solusi
                
            if bukti_penyelesaian:
                laporan.bukti_penyelesaian = bukti_penyelesaian
                
            if estimasi_penanganan:
                laporan.estimasi_penanganan = estimasi_penanganan
            elif 'estimasi_penanganan' in request.POST:
                laporan.estimasi_penanganan = None
                
            if estimasi_mulai:
                laporan.estimasi_mulai = estimasi_mulai
            elif 'estimasi_mulai' in request.POST:
                laporan.estimasi_mulai = None
                
            if request.user.is_staff:
                prioritas = request.POST.get('prioritas')
                if prioritas:
                    laporan.prioritas = prioritas
                    
            laporan.save()
            messages.success(request, 'Status laporan berhasil diperbarui.')
            return redirect('laporan_list' if request.user.is_staff else 'dashboard')
            
        elif laporan.pelapor == request.user and laporan.status == 'selesai':
            rating = request.POST.get('rating')
            ulasan = request.POST.get('ulasan')
            if rating:
                try:
                    laporan.rating = int(rating)
                    laporan.ulasan = ulasan
                    laporan.save()
                    messages.success(request, 'Terima kasih atas penilaian Anda.')
                except ValueError:
                    messages.error(request, 'Rating tidak valid.')
            return redirect('laporan_detail', id=laporan.id)
            
    context = {
        'laporan': laporan
    }
    
    if request.user.is_staff or getattr(request.user, 'is_teknisi', False):
        return render(request, 'laporan_detail.html', context)
    else:
        return render(request, 'user_laporan_detail.html', context)

@login_required
def ubah_laporan(request, id):
    laporan = get_object_or_404(Laporan, id=id)
    
    # Hanya pelapor yang bisa mengubah, dan status harus menunggu
    if laporan.pelapor != request.user or laporan.status != 'menunggu':
        messages.error(request, 'Anda tidak memiliki akses untuk mengubah laporan ini.')
        return redirect('status_laporan')
        
    if request.method == 'POST':
        judul = request.POST.get('judul')
        kategori = request.POST.get('kategori')
        bidang_id = request.POST.get('bidang')
        deskripsi = request.POST.get('deskripsi')
        lampiran = request.FILES.get('lampiran')
        tanggal_lapor = request.POST.get('tanggal_lapor')
        
        bidang = Bidang.objects.filter(id=bidang_id).first() if bidang_id else None
        
        laporan.judul = judul
        laporan.kategori = kategori
        laporan.bidang = bidang
        laporan.deskripsi = deskripsi
        if lampiran:
            laporan.lampiran = lampiran
        if tanggal_lapor:
            laporan.created_at = tanggal_lapor
            
        laporan.save()
        
        messages.success(request, 'Laporan berhasil diperbarui.')
        return redirect('laporan_detail', id=laporan.id)
        
    context = {
        'laporan': laporan,
        'kategori_choices': Laporan.KATEGORI_CHOICES,
        'bidang_list': Bidang.objects.all()
    }
    return render(request, 'ubah_laporan.html', context)

@login_required
def batalkan_laporan(request, id):
    laporan = get_object_or_404(Laporan, id=id)
    
    # Hanya pelapor yang bisa membatalkan, dan status harus menunggu
    if laporan.pelapor == request.user and laporan.status == 'menunggu':
        laporan.delete()
        messages.success(request, 'Laporan berhasil dibatalkan (dihapus).')
    else:
        messages.error(request, 'Laporan ini tidak dapat dibatalkan.')
        
    return redirect('status_laporan')

@login_required
def ambil_tiket(request, id):
    if not getattr(request.user, 'is_teknisi', False):
        messages.error(request, 'Anda tidak memiliki akses untuk mengambil tiket ini.')
        return redirect('dashboard')
        
    laporan = get_object_or_404(Laporan, id=id)
    if laporan.status == 'menunggu' and not laporan.teknisi_bertugas:
        laporan.status = 'diproses'
        laporan.teknisi_bertugas = request.user
        laporan.waktu_diambil = timezone.now()
        if not laporan.estimasi_mulai:
            laporan.estimasi_mulai = timezone.now()
        laporan.save()
        messages.success(request, f'Laporan "{laporan.judul}" berhasil diambil dan sekarang sedang diproses.')
    else:
        messages.error(request, 'Laporan ini sudah diambil oleh teknisi lain atau tidak valid.')
        
    return redirect('dashboard')


@login_required
def chart_data(request):
    period = request.GET.get('period', 'minggu')
    month_param = request.GET.get('month')
    year_param = request.GET.get('year')
    week_param = request.GET.get('week')
    today = timezone.now().date()
    
    indonesian_days = {'Mon': 'Sen', 'Tue': 'Sel', 'Wed': 'Rab', 'Thu': 'Kam', 'Fri': 'Jum', 'Sat': 'Sab', 'Sun': 'Min'}
    
    if period == 'minggu':
        target_year = today.year
        target_month = today.month
        
        if week_param:
            try:
                week_num = int(week_param)
                start_day = (week_num - 1) * 7 + 1
                _, num_days_in_month = calendar.monthrange(target_year, target_month)
                
                if start_day > num_days_in_month:
                    start_day = num_days_in_month
                    
                end_day = min(start_day + 6, num_days_in_month)
                
                start_date = datetime.date(target_year, target_month, start_day)
                end_date = datetime.date(target_year, target_month, end_day)
                
                num_days = (end_date - start_date).days + 1
                date_range = [start_date + datetime.timedelta(days=i) for i in range(num_days)]
                labels = [f"{indonesian_days[d.strftime('%a')]} {d.strftime('%d')}" for d in date_range]
            except ValueError:
                start_date = today - datetime.timedelta(days=6)
                date_range = [start_date + datetime.timedelta(days=i) for i in range(7)]
                labels = [indonesian_days[d.strftime('%a')] for d in date_range]
                end_date = today
        else:
            start_date = today - datetime.timedelta(days=6)
            date_range = [start_date + datetime.timedelta(days=i) for i in range(7)]
            labels = [indonesian_days[d.strftime('%a')] for d in date_range]
            end_date = today
    else: # bulan
        target_year = today.year
        target_month = today.month
        
        if month_param and year_param:
            try:
                target_year = int(year_param)
                target_month = int(month_param)
            except ValueError:
                pass
                
        start_date = datetime.date(target_year, target_month, 1)
        _, num_days = calendar.monthrange(target_year, target_month)
        date_range = [start_date + datetime.timedelta(days=i) for i in range(num_days)]
        
        indonesian_months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mei', 6: 'Jun', 7: 'Jul', 8: 'Ags', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Des'}
        labels = [f"{d.strftime('%d')} {indonesian_months[d.month]}" for d in date_range]
        
        end_date = start_date.replace(day=num_days)
        
    if request.user.is_staff:
        laporans = Laporan.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    else:
        laporans = Laporan.objects.filter(pelapor=request.user, created_at__date__gte=start_date, created_at__date__lte=end_date)
    
    data_total = {d: 0 for d in date_range}
    data_selesai = {d: 0 for d in date_range}
    data_diproses = {d: 0 for d in date_range}
    data_menunggu = {d: 0 for d in date_range}
    
    category_counts = {}
    bidang_counts = {}
    
    total_waktu_penyelesaian = 0
    laporan_selesai_count = 0
    teknisi_stats = {}
    
    for d in laporans:
        date_key = d.created_at.date()
        if date_key in data_total:
            data_total[date_key] += 1
            if d.status == 'selesai':
                data_selesai[date_key] += 1
            elif d.status == 'diproses':
                data_diproses[date_key] += 1
            elif d.status == 'menunggu':
                data_menunggu[date_key] += 1
                
        cat = d.get_kategori_display()
        if cat in category_counts:
            category_counts[cat] += 1
        else:
            category_counts[cat] = 1
            
        bidang_nama = d.bidang.nama if d.bidang else 'Tanpa Bidang'
        if bidang_nama in bidang_counts:
            bidang_counts[bidang_nama] += 1
        else:
            bidang_counts[bidang_nama] = 1
            
        if d.status == 'selesai' and d.waktu_selesai and d.waktu_diambil:
            waktu_penyelesaian = (d.waktu_selesai - d.waktu_diambil).total_seconds()
            if waktu_penyelesaian > 0:
                total_waktu_penyelesaian += waktu_penyelesaian
                laporan_selesai_count += 1
                
        if d.status == 'selesai' and d.teknisi_bertugas:
            teknisi_id = d.teknisi_bertugas.id
            teknisi_name = d.teknisi_bertugas.get_full_name() or d.teknisi_bertugas.username
            if teknisi_id not in teknisi_stats:
                teknisi_stats[teknisi_id] = {'name': teknisi_name, 'completed': 0, 'rating_sum': 0, 'rating_count': 0}
            
            teknisi_stats[teknisi_id]['completed'] += 1
            if d.rating is not None:
                teknisi_stats[teknisi_id]['rating_sum'] += d.rating
                teknisi_stats[teknisi_id]['rating_count'] += 1
                
    if laporan_selesai_count > 0:
        avg_seconds = total_waktu_penyelesaian / laporan_selesai_count
        hours = int(avg_seconds // 3600)
        minutes = int((avg_seconds % 3600) // 60)
        if hours > 0:
            sla_text = f"{hours} Jam {minutes} Menit"
        else:
            sla_text = f"{minutes} Menit"
    else:
        sla_text = "-"
        
    leaderboard = []
    for stat in teknisi_stats.values():
        avg_rating = stat['rating_sum'] / stat['rating_count'] if stat['rating_count'] > 0 else 0
        leaderboard.append({
            'name': stat['name'],
            'completed': stat['completed'],
            'avg_rating': round(avg_rating, 1)
        })
    leaderboard.sort(key=lambda x: x['completed'], reverse=True)
    leaderboard = leaderboard[:5]
                
    return JsonResponse({
        'labels': labels,
        'category_labels': list(category_counts.keys()),
        'category_data': list(category_counts.values()),
        'bidang_labels': list(bidang_counts.keys()),
        'bidang_data': list(bidang_counts.values()),
        'sla_text': sla_text,
        'leaderboard': leaderboard,
        'datasets': [
            {
                'label': 'Total Laporan Masuk',
                'data': list(data_total.values()),
                'borderColor': '#0d6efd',
                'backgroundColor': '#0d6efd',
                'borderRadius': 4,
                'borderWidth': 0
            },
            {
                'label': 'Selesai',
                'data': list(data_selesai.values()),
                'borderColor': '#16a34a',
                'backgroundColor': '#16a34a',
                'borderRadius': 4,
                'borderWidth': 0
            },
            {
                'label': 'Sedang Diproses',
                'data': list(data_diproses.values()),
                'borderColor': '#facc15',
                'backgroundColor': '#facc15',
                'borderRadius': 4,
                'borderWidth': 0
            },
            {
                'label': 'Menunggu',
                'data': list(data_menunggu.values()),
                'borderColor': '#fbbf24',
                'backgroundColor': '#fbbf24',
                'borderRadius': 4,
                'borderWidth': 0
            }
        ]
    })

@login_required
def export_dashboard(request):
    if not request.user.is_staff:
        return redirect('dashboard')
        

    # Handle filtering based on period, month, year, week
    period = request.GET.get('period', 'minggu')
    month_param = request.GET.get('month')
    year_param = request.GET.get('year')
    week_param = request.GET.get('week')
    today = timezone.now().date()

    if period == 'minggu':
        target_year = today.year
        target_month = today.month
        
        if week_param:
            try:
                week_num = int(week_param)
                start_day = (week_num - 1) * 7 + 1
                _, num_days_in_month = calendar.monthrange(target_year, target_month)
                
                if start_day > num_days_in_month:
                    start_day = num_days_in_month
                    
                end_day = min(start_day + 6, num_days_in_month)
                start_date = datetime.date(target_year, target_month, start_day)
                end_date = datetime.date(target_year, target_month, end_day)
            except ValueError:
                start_date = today - datetime.timedelta(days=6)
                end_date = today
        else:
            start_date = today - datetime.timedelta(days=6)
            end_date = today
    else: # bulan
        target_year = today.year
        target_month = today.month
        
        if month_param and year_param:
            try:
                target_year = int(year_param)
                target_month = int(month_param)
            except ValueError:
                pass
                
        start_date = datetime.date(target_year, target_month, 1)
        _, num_days = calendar.monthrange(target_year, target_month)
        end_date = start_date.replace(day=num_days)
    
    
    response = HttpResponse(content_type='text/csv')
    filename = f"Rekap_Laporan_{start_date.strftime('%d-%b-%Y')}_sd_{end_date.strftime('%d-%b-%Y')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(['ID Laporan', 'Judul', 'Kategori', 'Pelapor', 'Bidang', 'Status', 'Tanggal Lapor', 'Estimasi Mulai', 'Estimasi Selesai', 'Solusi'])

    # Get reports based on the calculated date range
    laporans = Laporan.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).order_by('-created_at')
    
    for laporan in laporans:
        writer.writerow([
            laporan.id,
            laporan.judul,
            laporan.get_kategori_display(),
            laporan.pelapor.get_full_name() or laporan.pelapor.username,
            laporan.bidang.nama if laporan.bidang else '-',
            laporan.get_status_display(),
            laporan.created_at.strftime("%Y-%m-%d %H:%M:%S") if laporan.created_at else '-',
            laporan.estimasi_mulai.strftime("%Y-%m-%d %H:%M:%S") if laporan.estimasi_mulai else '-',
            laporan.estimasi_penanganan.strftime("%Y-%m-%d %H:%M:%S") if laporan.estimasi_penanganan else '-',
            laporan.solusi or '-'
        ])
        
    return response

@login_required
def verifikasi_teknisi(request, id):
    if not request.user.is_staff:
        return redirect('dashboard')
        
    teknisi = get_object_or_404(User, id=id, is_teknisi=True)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'terima':
            teknisi.is_verified_teknisi = True
            teknisi.save()
            messages.success(request, f'Teknisi {teknisi.username} berhasil diverifikasi.')
        elif action == 'tolak':
            teknisi.delete()
            messages.success(request, f'Pendaftaran teknisi ditolak dan dihapus.')
            
    return redirect('dashboard')

@login_required
def export_excel(request):
    if not request.user.is_staff:
        return redirect('dashboard')
        
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="laporan_sinar.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Judul', 'Kategori', 'Pelapor', 'Bidang', 'Status', 'Teknisi Bertugas', 'Tanggal Lapor', 'Waktu Selesai', 'Rating', 'Ulasan'])
    
    laporan_list = Laporan.objects.all().select_related('pelapor', 'bidang', 'teknisi_bertugas')
    for lap in laporan_list:
        writer.writerow([
            lap.id,
            lap.judul,
            lap.get_kategori_display(),
            lap.pelapor.get_full_name() or lap.pelapor.username,
            lap.bidang.nama if lap.bidang else '-',
            lap.get_status_display(),
            (lap.teknisi_bertugas.get_full_name() or lap.teknisi_bertugas.username) if lap.teknisi_bertugas else '-',
            lap.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            lap.waktu_selesai.strftime('%Y-%m-%d %H:%M:%S') if lap.waktu_selesai else '-',
            lap.rating if lap.rating else '-',
            lap.ulasan if lap.ulasan else '-'
        ])
        
    return response

@login_required
def export_pdf(request):
    if not request.user.is_staff:
        return redirect('dashboard')
        
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.alignment = 1
    elements.append(Paragraph("Rekap Laporan SINAR", title_style))
    
    data = [['ID', 'Judul', 'Kategori', 'Pelapor', 'Bidang', 'Status', 'Teknisi', 'Tanggal']]
    
    # Filter date range
    period = request.GET.get('period', 'minggu')
    month_param = request.GET.get('month')
    year_param = request.GET.get('year')
    week_param = request.GET.get('week')
    today = timezone.now().date()

    if period == 'minggu':
        target_year = today.year
        target_month = today.month
        
        if week_param:
            try:
                week_num = int(week_param)
                start_day = (week_num - 1) * 7 + 1
                _, num_days_in_month = calendar.monthrange(target_year, target_month)
                
                if start_day > num_days_in_month:
                    start_day = num_days_in_month
                    
                end_day = min(start_day + 6, num_days_in_month)
                start_date = datetime.date(target_year, target_month, start_day)
                end_date = datetime.date(target_year, target_month, end_day)
            except ValueError:
                start_date = today - datetime.timedelta(days=6)
                end_date = today
        else:
            start_date = today - datetime.timedelta(days=6)
            end_date = today
    else: # bulan
        target_year = today.year
        target_month = today.month
        
        if month_param and year_param:
            try:
                target_year = int(year_param)
                target_month = int(month_param)
            except ValueError:
                pass
                
        start_date = datetime.date(target_year, target_month, 1)
        _, num_days = calendar.monthrange(target_year, target_month)
        end_date = start_date.replace(day=num_days)
        
    elements.append(Paragraph(f"Rekap Laporan SINAR ({start_date.strftime('%d-%b-%Y')} s/d {end_date.strftime('%d-%b-%Y')})", styles['Normal']))
    
    laporan_list = Laporan.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).select_related('pelapor', 'bidang', 'teknisi_bertugas').order_by('-created_at')
    for lap in laporan_list:
        data.append([
            str(lap.id),
            (lap.judul[:25] + '...') if len(lap.judul) > 25 else lap.judul,
            lap.get_kategori_display()[:20],
            lap.pelapor.get_full_name() or lap.pelapor.username,
            lap.bidang.nama if lap.bidang else '-',
            lap.get_status_display(),
            (lap.teknisi_bertugas.get_full_name() or lap.teknisi_bertugas.username) if lap.teknisi_bertugas else '-',
            lap.created_at.strftime('%Y-%m-%d')
        ])
        
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    filename = f"Rekap_Laporan_{start_date.strftime('%d-%b-%Y')}_sd_{end_date.strftime('%d-%b-%Y')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    
    return response
