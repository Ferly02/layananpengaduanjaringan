from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('laporan/', views.laporan_list, name='laporan_list'),
    path('buat-laporan/', views.buat_laporan, name='buat_laporan'),
    path('status-laporan/', views.status_laporan, name='status_laporan'),
    path('edit-profil/', views.edit_profil, name='edit_profil'),
    path('laporan/detail/<int:id>/', views.laporan_detail, name='laporan_detail'),
    path('admin-login/', views.login_admin, name='login_admin'),
    path('login/', views.login_user, name='login_user'),
    path('register/', views.register, name='register'),
    path('lupa-password/', views.lupa_password, name='lupa_password'),
    path('api/chart-data/', views.chart_data, name='chart_data'),
    path('export-dashboard/', views.export_dashboard, name='export_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('laporan/ubah/<int:id>/', views.ubah_laporan, name='ubah_laporan'),
    path('laporan/batalkan/<int:id>/', views.batalkan_laporan, name='batalkan_laporan'),
    path('laporan/ambil/<int:id>/', views.ambil_tiket, name='ambil_tiket'),
    path('teknisi/verifikasi/<int:id>/', views.verifikasi_teknisi, name='verifikasi_teknisi'),
    path('teknisi/buat/', views.buat_teknisi, name='buat_teknisi'),
    path('laporan/export-excel/', views.export_excel, name='export_excel'),
    path('laporan/export-pdf/', views.export_pdf, name='export_pdf'),
]
