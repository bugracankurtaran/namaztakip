import json
import os
import datetime
import calendar
import random
import zipfile
import traceback

from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRoundFlatButton, MDRaisedButton, MDFillRoundFlatButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.toast import toast
from kivy.metrics import dp
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView

# --- GÜVENLİ BİLDİRİM SİSTEMİ ---
try:
    from plyer import notification
except ImportError:
    notification = None

# --- AYARLAR ---
AYLAR_LISTESI = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
                 "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
VAKIT_ISIMLERI = ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"]

KREM_BG = [0.96, 0.94, 0.88, 1]
PANEL_RENK = [0.85, 0.92, 0.88, 1]

# --- KV TASARIMI ---
KV_CODE = '''
# --- NAMAZ SATIRI ---
<NamazSatiri>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(42)
    padding: [0, 0]
    spacing: 0
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.05 if self.index % 2 == 1 else 0
        Rectangle:
            pos: self.pos
            size: self.size

    MDLabel:
        text: root.gun_text
        halign: "center"
        size_hint_x: 0.1
        font_style: "Caption"
        theme_text_color: "Primary"

    AnchorLayout:
        size_hint_x: 0.15
        MDIconButton:
            icon: root.icon_0
            theme_text_color: "Custom"
            text_color: root.color_0
            on_release: app.menu_ac(root.tarih_id, 0)
    AnchorLayout:
        size_hint_x: 0.15
        MDIconButton:
            icon: root.icon_1
            theme_text_color: "Custom"
            text_color: root.color_1
            on_release: app.menu_ac(root.tarih_id, 1)
    AnchorLayout:
        size_hint_x: 0.15
        MDIconButton:
            icon: root.icon_2
            theme_text_color: "Custom"
            text_color: root.color_2
            on_release: app.menu_ac(root.tarih_id, 2)
    AnchorLayout:
        size_hint_x: 0.15
        MDIconButton:
            icon: root.icon_3
            theme_text_color: "Custom"
            text_color: root.color_3
            on_release: app.menu_ac(root.tarih_id, 3)
    AnchorLayout:
        size_hint_x: 0.15
        MDIconButton:
            icon: root.icon_4
            theme_text_color: "Custom"
            text_color: root.color_4
            on_release: app.menu_ac(root.tarih_id, 4)
    AnchorLayout:
        size_hint_x: 0.15
        MDIconButton:
            icon: root.regl_icon
            theme_text_color: "Custom"
            text_color: root.regl_color
            icon_size: dp(20)
            on_release: app.regl_tikla(root.tarih_id)

# --- ORUÇ YIL KARTI ---
<OrucYilKarti>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(140)
    padding: dp(10)
    spacing: dp(5)
    md_bg_color: [0.96, 0.94, 0.88, 1]
    radius: [10]
    elevation: 1
    
    MDBoxLayout:
        size_hint_y: None
        height: dp(30)
        MDLabel:
            text: root.yil_text
            font_style: "H6"
            theme_text_color: "Primary"
        MDLabel:
            text: root.durum_ozet
            halign: "right"
            theme_text_color: "Custom"
            text_color: root.durum_renk
            bold: True

    MDSeparator:

    MDGridLayout:
        cols: 2
        spacing: dp(10)
        
        MDBoxLayout:
            orientation: 'vertical'
            MDLabel:
                text: "Toplam Borç"
                halign: "center"
                font_style: "Caption"
                theme_text_color: "Secondary"
            MDBoxLayout:
                adaptive_size: True
                pos_hint: {"center_x": .5}
                MDIconButton:
                    icon: "minus-circle-outline"
                    on_release: app.oruc_guncelle(root.yil_id, "borc", -1)
                MDLabel:
                    text: root.borc_sayi
                    halign: "center"
                    size_hint_x: None
                    width: dp(30)
                    bold: True
                MDIconButton:
                    icon: "plus-circle-outline"
                    on_release: app.oruc_guncelle(root.yil_id, "borc", 1)

        MDBoxLayout:
            orientation: 'vertical'
            MDLabel:
                text: "Tutulan (Kaza)"
                halign: "center"
                font_style: "Caption"
                theme_text_color: "Secondary"
            MDBoxLayout:
                adaptive_size: True
                pos_hint: {"center_x": .5}
                MDIconButton:
                    icon: "minus-circle"
                    theme_text_color: "Custom"
                    text_color: [0, 0.6, 0, 1]
                    on_release: app.oruc_guncelle(root.yil_id, "tutulan", -1)
                MDLabel:
                    text: root.tutulan_sayi
                    halign: "center"
                    size_hint_x: None
                    width: dp(30)
                    bold: True
                    theme_text_color: "Custom"
                    text_color: [0, 0.6, 0, 1]
                MDIconButton:
                    icon: "plus-circle"
                    theme_text_color: "Custom"
                    text_color: [0, 0.6, 0, 1]
                    on_release: app.oruc_guncelle(root.yil_id, "tutulan", 1)

    MDProgressBar:
        value: root.progress_val
        color: root.durum_renk
        size_hint_y: None
        height: dp(8)

<NamazListe>:
    viewclass: 'NamazSatiri'
    RecycleBoxLayout:
        default_size: None, dp(42)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'

<OrucListe>:
    viewclass: 'OrucYilKarti'
    RecycleBoxLayout:
        default_size: None, dp(140)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
'''

# --- SINIFLAR ---
class NamazSatiri(RecycleDataViewBehavior, MDBoxLayout):
    index = NumericProperty(0)
    gun_text = StringProperty("")
    tarih_id = StringProperty("")
    icon_0 = StringProperty("checkbox-blank-outline"); color_0 = ListProperty([0.5]*4)
    icon_1 = StringProperty("checkbox-blank-outline"); color_1 = ListProperty([0.5]*4)
    icon_2 = StringProperty("checkbox-blank-outline"); color_2 = ListProperty([0.5]*4)
    icon_3 = StringProperty("checkbox-blank-outline"); color_3 = ListProperty([0.5]*4)
    icon_4 = StringProperty("checkbox-blank-outline"); color_4 = ListProperty([0.5]*4)
    regl_icon = StringProperty("flower-outline"); regl_color = ListProperty([0.5]*4)
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(NamazSatiri, self).refresh_view_attrs(rv, index, data)

class OrucYilKarti(RecycleDataViewBehavior, MDCard):
    index = NumericProperty(0)
    yil_id = StringProperty("") 
    yil_text = StringProperty("") 
    borc_sayi = StringProperty("0")
    tutulan_sayi = StringProperty("0")
    durum_ozet = StringProperty("")
    durum_renk = ListProperty([0.8, 0.2, 0.2, 1])
    progress_val = NumericProperty(0)
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(OrucYilKarti, self).refresh_view_attrs(rv, index, data)

class NamazListe(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []

class OrucListe(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []

class NamazTakipV77App(MDApp):
    secili_tarih = None
    
    dialog_tarih = None
    dialog_istatistik = None
    dialog_namaz = None
    dialog_manuel = None
    secici_yil = 2026
    secici_hedef = None 
    lbl_secici_yil = None
    
    kaza_baslangic = None
    kaza_bitis = None
    is_kadin = False
    regl_suresi = 6
    manual_kazalar = [0]*5
    mevcut_borclar_listesi = [0,0,0,0,0]
    
    toplam_odenen = 0
    bugun_odenen = 0
    zincir_sayisi = 0
    
    performans_log = {}

    def build(self):
        self.secili_tarih = datetime.date.today()
        self.secici_yil = self.secili_tarih.year
        
        Builder.load_string(KV_CODE)
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        
        self.namaz_veriler = self.verileri_yukle("namaz_v77_data.json")
        self.oruc_veriler = self.verileri_yukle("oruc_v77_data.json")
        self.performans_log = self.verileri_yukle("performans_v77_log.json")
        
        namaz_ayarlar = self.verileri_yukle("namaz_v77_settings.json")
        self.kaza_baslangic = namaz_ayarlar.get("baslangic")
        self.kaza_bitis = namaz_ayarlar.get("bitis")
        self.is_kadin = namaz_ayarlar.get("is_kadin", False)
        self.regl_suresi = namaz_ayarlar.get("regl_suresi", 6)
        self.manual_kazalar = namaz_ayarlar.get("manual_kazalar", [0]*5)

        screen = MDScreen()
        bottom_nav = MDBottomNavigation(selected_color_background="orange", text_color_active="orange")

        # --- SEKME 1: NAMAZ ---
        tab_namaz = MDBottomNavigationItem(name='namaz', text='Namaz', icon='mosque')
        layout_namaz = MDBoxLayout(orientation='vertical')
        
        self.toolbar = MDTopAppBar(title="Namaz Takibi", md_bg_color=self.theme_cls.primary_color, elevation=2)
        self.toolbar.left_action_items = [["arrow-left", lambda x: self.ay_degistir(-1)]]
        self.toolbar.right_action_items = [
            ["chart-bar", lambda x: self.istatistik_ac()], 
            ["target", lambda x: self.en_yakin_kaza_git()], 
            ["calculator", lambda x: self.namaz_hesaplayici_ac()],
            ["calendar", lambda x: self.tarih_secici_ac('ana_ekran')], 
            ["arrow-right", lambda x: self.ay_degistir(1)]
        ]
        layout_namaz.add_widget(self.toolbar)

        self.namaz_card = MDCard(orientation="vertical", size_hint_y=None, height=dp(85), md_bg_color=PANEL_RENK, padding=10, spacing=5)
        self.progress = MDProgressBar(value=0, color=self.theme_cls.primary_color, size_hint_y=None, height=dp(10))
        self.namaz_card.add_widget(self.progress)
        
        stats_box = MDBoxLayout(size_hint_y=None, height=dp(20))
        self.lbl_yuzde = MDLabel(text="%0", font_style="Caption", theme_text_color="Primary")
        self.lbl_seri = MDLabel(text="Zincir: 0", halign="right", font_style="Caption", theme_text_color="Custom", text_color=[1, 0.5, 0, 1], bold=True)
        stats_box.add_widget(self.lbl_yuzde); stats_box.add_widget(self.lbl_seri)
        self.namaz_card.add_widget(stats_box)
        
        self.lbl_ozet = MDLabel(text="...", halign="center", font_style="Caption", bold=True, theme_text_color="Custom", text_color=[0.8,0.2,0.2,1])
        self.namaz_card.add_widget(self.lbl_ozet)
        self.lbl_tahmin = MDLabel(text="...", halign="center", font_style="Caption", theme_text_color="Secondary")
        self.namaz_card.add_widget(self.lbl_tahmin)
        layout_namaz.add_widget(self.namaz_card)

        baslik_box = MDBoxLayout(size_hint_y=None, height=dp(30))
        baslik_box.add_widget(MDLabel(text="Gün", halign="center", size_hint_x=0.1, font_style="Caption", bold=True))
        for v in ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"]:
            baslik_box.add_widget(MDLabel(text=v, halign="center", size_hint_x=0.15, font_style="Caption", bold=True))
        baslik_box.add_widget(MDLabel(text="Regl", halign="center", size_hint_x=0.15, font_style="Caption", bold=True))
        layout_namaz.add_widget(baslik_box)

        self.namaz_liste_widget = NamazListe()
        layout_namaz.add_widget(self.namaz_liste_widget)
        tab_namaz.add_widget(layout_namaz)
        bottom_nav.add_widget(tab_namaz)

        # --- SEKME 2: ORUÇ ---
        tab_oruc = MDBottomNavigationItem(name='oruc', text='Oruç', icon='food-off')
        layout_oruc = MDBoxLayout(orientation='vertical', md_bg_color=KREM_BG)
        layout_oruc.add_widget(MDTopAppBar(title="Ramazan Kaza Takibi", md_bg_color=[0.9, 0.6, 0.2, 1], elevation=2))

        self.oruc_ozet_card = MDCard(size_hint_y=None, height=dp(60), md_bg_color=KREM_BG, padding=15)
        self.lbl_oruc_toplam = MDLabel(text="...", halign="center", font_style="H6", theme_text_color="Custom", text_color=[0.9, 0.4, 0, 1])
        self.oruc_ozet_card.add_widget(self.lbl_oruc_toplam)
        layout_oruc.add_widget(self.oruc_ozet_card)

        self.oruc_liste_widget = OrucListe()
        layout_oruc.add_widget(self.oruc_liste_widget)
        tab_oruc.add_widget(layout_oruc)
        bottom_nav.add_widget(tab_oruc)

        screen.add_widget(bottom_nav)
        
        self.tum_listeleri_guncelle()
        self.namaz_sayaci_guncelle()
        
        return screen

    # --- BİLDİRİM & LOG ---
    def bildirim_gonder(self, baslik, mesaj):
        if notification:
            try: notification.notify(title=baslik, message=mesaj, app_name="Namaz Takip", timeout=5)
            except: pass

    def log_performans_arttir(self):
        t_bugun = datetime.date.today().strftime("%Y-%m-%d")
        bugun_sayi = self.performans_log.get(t_bugun, 0)
        self.performans_log[t_bugun] = bugun_sayi + 1
        self.veriyi_dosyaya_yaz("performans_v77_log.json", self.performans_log)

    def get_gercek_performans(self, gun_sayisi):
        toplam = 0
        today = datetime.date.today()
        for i in range(gun_sayisi):
            tarih = today - datetime.timedelta(days=i)
            t_str = tarih.strftime("%Y-%m-%d")
            toplam += self.performans_log.get(t_str, 0)
        return toplam

    # --- AKILLI İSTATİSTİK PENCERESİ (DÜZELTİLDİ) ---
    def istatistik_ac(self):
        son_7_gun_performans = self.get_gercek_performans(7)
        toplam_borc = sum(self.mevcut_borclar_listesi)
        
        # --- AKILLI BÖLÜCÜ (Yeni Kullanıcılar İçin) ---
        # Log dosyasındaki en eski tarihe bakıyoruz.
        # Eğer kullanıcı 2 gün önce başladıysa, toplamı 2'ye böleriz (7'ye değil).
        # Böylece ilk günlerdeki hız doğru hesaplanır.
        
        log_dates = sorted(self.performans_log.keys())
        bolucu = 7 # Varsayılan
        if log_dates:
            ilk_tarih = datetime.datetime.strptime(log_dates[0], "%Y-%m-%d").date()
            gecen_gun = (datetime.date.today() - ilk_tarih).days + 1
            if gecen_gun < 7:
                bolucu = max(1, gecen_gun) # En az 1 olsun
        
        gunluk_hiz = son_7_gun_performans / bolucu
        
        tahmin_metni = "Veri Yetersiz"
        if gunluk_hiz > 0:
            kalan_gun = int(toplam_borc / gunluk_hiz)
            bitis_tarihi = datetime.date.today() + datetime.timedelta(days=kalan_gun)
            tahmin_metni = bitis_tarihi.strftime('%d.%m.%Y')

        bu_hafta = son_7_gun_performans
        bu_ay = self.get_gercek_performans(30)

        icerik = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(350), padding=20, spacing=15)
        
        icerik.add_widget(MDLabel(text="DETAYLI ANALİZ", halign="center", font_style="H5", bold=True, theme_text_color="Primary"))
        
        row_zincir = MDBoxLayout(adaptive_height=True, spacing=10)
        row_zincir.add_widget(MDIconButton(icon="fire", theme_text_color="Custom", text_color=[1, 0.5, 0, 1]))
        row_zincir.add_widget(MDLabel(text=f"Zincir: {self.zincir_sayisi} Gün", theme_text_color="Custom", text_color=[1, 0.5, 0, 1], bold=True))
        icerik.add_widget(row_zincir)

        row_tahmin = MDBoxLayout(adaptive_height=True, spacing=10)
        row_tahmin.add_widget(MDIconButton(icon="calendar-clock", theme_text_color="Primary"))
        row_tahmin.add_widget(MDLabel(text=f"Tahmini Bitiş: {tahmin_metni}"))
        icerik.add_widget(row_tahmin)
        
        row_hafta = MDBoxLayout(adaptive_height=True, spacing=10)
        row_hafta.add_widget(MDIconButton(icon="chart-line", theme_text_color="Custom", text_color=[0, 0.6, 0, 1]))
        row_hafta.add_widget(MDLabel(text=f"Bu Hafta: {bu_hafta} Vakit"))
        icerik.add_widget(row_hafta)

        row_ay = MDBoxLayout(adaptive_height=True, spacing=10)
        row_ay.add_widget(MDIconButton(icon="calendar-month", theme_text_color="Custom", text_color=[0, 0.6, 0, 1]))
        row_ay.add_widget(MDLabel(text=f"Bu Ay: {bu_ay} Vakit"))
        icerik.add_widget(row_ay)

        row_borc = MDBoxLayout(adaptive_height=True, spacing=10)
        row_borc.add_widget(MDIconButton(icon="chart-box", theme_text_color="Error"))
        row_borc.add_widget(MDLabel(text=f"Toplam Borç: {toplam_borc}", theme_text_color="Error"))
        icerik.add_widget(row_borc)

        self.dialog_istatistik = MDDialog(title="", type="custom", content_cls=icerik)
        self.dialog_istatistik.open()

    def hesapla_zincir(self):
        streak = 0
        check_date = datetime.date.today()
        t_today = check_date.strftime("%Y-%m-%d")
        if self.performans_log.get(t_today, 0) > 0:
            streak += 1
            check_date -= datetime.timedelta(days=1)
        else:
            check_date -= datetime.timedelta(days=1)

        while True:
            t_str = check_date.strftime("%Y-%m-%d")
            if self.performans_log.get(t_str, 0) > 0:
                streak += 1
                check_date -= datetime.timedelta(days=1)
            else:
                break
        
        self.zincir_sayisi = streak
        self.lbl_seri.text = f"Zincir: {streak} Gün"

    # --- YEDEKLEME ---
    def verileri_yedekle(self):
        try:
            hedef_klasor = os.getcwd()
            yedek_adi = f"Yedek_{datetime.date.today()}.zip"
            tam_yol = os.path.join(hedef_klasor, yedek_adi)
            dosyalar = ["namaz_v77_data.json", "oruc_v77_data.json", "namaz_v77_settings.json", "performans_v77_log.json"]
            with zipfile.ZipFile(tam_yol, 'w') as zipf:
                for dosya in dosyalar:
                    kaynak_yol = self.get_file_path(dosya)
                    if os.path.exists(kaynak_yol):
                        zipf.write(kaynak_yol, arcname=dosya)
            toast(f"Yedeklendi: {yedek_adi}")
        except Exception as e:
            toast(f"Hata: {str(e)}")

    # --- DİĞER FONKSİYONLAR ---
    def tarih_secici_ac(self, hedef):
        self.secici_hedef = hedef
        if hedef == 'ana_ekran': self.secici_yil = self.secili_tarih.year
        elif hedef == 'baslangic' and self.kaza_baslangic:
            try: self.secici_yil = int(self.kaza_baslangic.split("-")[0])
            except: self.secici_yil = 2015
        elif hedef == 'bitis' and self.kaza_bitis:
            try: self.secici_yil = int(self.kaza_bitis.split("-")[0])
            except: self.secici_yil = 2020
        else: self.secici_yil = 2026

        icerik = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(300), spacing=10)
        yil_box = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=20, padding=[10,0])
        self.lbl_secici_yil = MDLabel(text=str(self.secici_yil), halign="center", font_style="H5", theme_text_color="Primary")
        btn_ileri = MDIconButton(icon="chevron-right", on_release=lambda x: self.secici_yil_degis(1))
        btn_geri = MDIconButton(icon="chevron-left", on_release=lambda x: self.secici_yil_degis(-1))
        yil_box.add_widget(btn_geri); yil_box.add_widget(self.lbl_secici_yil); yil_box.add_widget(btn_ileri)
        icerik.add_widget(yil_box)
        aylar_grid = MDGridLayout(cols=3, spacing=5, size_hint_y=None, height=dp(200))
        for i in range(1, 13):
            aylar_grid.add_widget(MDRoundFlatButton(text=AYLAR_LISTESI[i], size_hint=(1, None), on_release=lambda x, ay=i: self.tarih_secildi(ay)))
        icerik.add_widget(aylar_grid)
        self.dialog_tarih = MDDialog(title="Dönem Seç (Ay/Yıl)", type="custom", content_cls=icerik)
        self.dialog_tarih.open()

    def secici_yil_degis(self, yon):
        self.secici_yil += yon
        if self.lbl_secici_yil: self.lbl_secici_yil.text = str(self.secici_yil)

    def tarih_secildi(self, ay):
        tarih_str = f"{self.secici_yil}-{ay:02d}-01"
        if self.secici_hedef == 'ana_ekran':
            self.secili_tarih = datetime.date(self.secici_yil, ay, 1)
            self.tum_listeleri_guncelle()
        elif self.secici_hedef == 'baslangic':
            self.kaza_baslangic = tarih_str
            self.btn_basla.text = f"Başlangıç: {tarih_str}"
        elif self.secici_hedef == 'bitis':
            self.kaza_bitis = tarih_str
            self.btn_bitis.text = f"Bitiş: {tarih_str}"
        self.dialog_tarih.dismiss()

    def en_yakin_kaza_git(self, *args):
        try:
            candidates = []
            today = datetime.date.today()
            for t_str, vals in self.namaz_veriler.items():
                if 2 in vals:
                    t_date = datetime.datetime.strptime(t_str, "%Y-%m-%d").date()
                    if t_date < today: candidates.append(t_date)
            if self.kaza_baslangic and self.kaza_bitis:
                start = datetime.datetime.strptime(self.kaza_baslangic, "%Y-%m-%d").date()
                end = datetime.datetime.strptime(self.kaza_bitis, "%Y-%m-%d").date()
                curr = end - datetime.timedelta(days=1)
                limit = 0 
                found_virtual = None
                while curr >= start and limit < 3650:
                    t_str = curr.strftime("%Y-%m-%d")
                    is_paid = False
                    if t_str in self.namaz_veriler:
                        vals = self.namaz_veriler[t_str]
                        if all(v in [1, 3] for v in vals): is_paid = True
                    if not is_paid:
                        found_virtual = curr
                        break 
                    curr -= datetime.timedelta(days=1)
                    limit += 1
                if found_virtual: candidates.append(found_virtual)
            max_manual = max(self.manual_kazalar)
            if max_manual > 0:
                for i in range(1, max_manual + 50): 
                    check_date = today - datetime.timedelta(days=i)
                    t_str = check_date.strftime("%Y-%m-%d")
                    status_list = [self.get_namaz_status(t_str, k) for k in range(5)]
                    if 2 in status_list:
                        candidates.append(check_date)
                        break 
            if candidates:
                target = max(candidates)
                self.secili_tarih = target
                self.tum_listeleri_guncelle()
                toast(f"Hedefe Işınlandı: {target.strftime('%d.%m.%Y')}")
            else: toast("Geçmişe dönük kaza bulunamadı! Tebrikler.")
        except: toast("Hesaplama Hatası")

    # --- ORTAK FONKSİYONLAR ---
    def tum_listeleri_guncelle(self):
        self.namaz_liste_guncelle()
        self.oruc_liste_guncelle()
        ay_str = f"{AYLAR_LISTESI[self.secili_tarih.month]} {self.secili_tarih.year}"
        self.toolbar.title = f"Namaz - {ay_str}"

    def ay_degistir(self, yon):
        yil = self.secili_tarih.year; ay = self.secili_tarih.month + yon
        if ay > 12: ay = 1; yil += 1
        elif ay < 1: ay = 12; yil -= 1
        self.secili_tarih = datetime.date(yil, ay, 1)
        self.tum_listeleri_guncelle()

    def get_namaz_status(self, tarih_str, index):
        if self.namaz_veriler.get(tarih_str): return self.namaz_veriler[tarih_str][index]
        in_range = False
        if self.kaza_baslangic and self.kaza_bitis:
            t1, t2 = sorted([self.kaza_baslangic, self.kaza_bitis])
            if t1 <= tarih_str < t2: in_range = True
        if in_range: return 2
        try:
            today = datetime.date.today()
            t_date = datetime.datetime.strptime(tarih_str, "%Y-%m-%d").date()
            diff = (today - t_date).days
            if 0 < diff <= self.manual_kazalar[index]: return 2
        except: pass
        return 0

    def namaz_liste_guncelle(self):
        gun_sayisi = calendar.monthrange(self.secili_tarih.year, self.secili_tarih.month)[1]
        data = []
        for gun in range(1, gun_sayisi+1):
            tarih_id = f"{self.secili_tarih.year}-{self.secili_tarih.month:02d}-{gun:02d}"
            gunluk = [self.get_namaz_status(tarih_id, i) for i in range(5)]
            kayitli = self.namaz_veriler.get(tarih_id)
            if kayitli and all(x==3 for x in kayitli): gunluk = [3]*5
            row = {'gun_text': str(gun), 'tarih_id': tarih_id}
            is_regl = all(x==3 for x in gunluk)
            for i in range(5):
                durum = gunluk[i]
                ikon, renk = ("checkbox-marked", [0,0.6,0,1]) if durum==1 else \
                             ("close-box", [0.8,0.1,0.1,1]) if durum==2 else \
                             ("minus-circle-outline", [0.6,0.3,0.7,1]) if durum==3 else \
                             ("checkbox-blank-outline", [0.6,0.6,0.6,1])
                if is_regl: ikon="checkbox-blank-circle-outline"; renk=[0.8,0.8,0.8,0.5]
                row[f'icon_{i}'] = ikon; row[f'color_{i}'] = renk
            row['regl_icon'] = "flower" if is_regl else "flower-outline"
            row['regl_color'] = [0.7,0.2,0.5,1] if is_regl else [0.6]*4
            data.append(row)
        self.namaz_liste_widget.data = data

    def menu_ac(self, tarih_id, index):
        menu = MDListBottomSheet()
        menu.add_item("Kılındı", lambda x: self.namaz_yaz(tarih_id, index, 1), icon="checkbox-marked")
        menu.add_item("Kaza", lambda x: self.namaz_yaz(tarih_id, index, 2), icon="close-box")
        menu.add_item("Temizle", lambda x: self.namaz_yaz(tarih_id, index, 0), icon="eraser")
        menu.open()

    def namaz_yaz(self, tarih, index, deger):
        current = [self.get_namaz_status(tarih, i) for i in range(5)]
        if tarih in self.namaz_veriler: current = self.namaz_veriler[tarih]
        if deger == 0:
            current[index] = 0
            if tarih in self.namaz_veriler:
                self.namaz_veriler[tarih] = current
                if all(x==0 for x in current): del self.namaz_veriler[tarih]
        else:
            current[index] = deger
            self.namaz_veriler[tarih] = current
        self.veriyi_dosyaya_yaz("namaz_v77_data.json", self.namaz_veriler)
        
        # MANUEL BORÇ DÜŞME (ÜSTTEKİ KUTU BOŞALMASIN DİYE)
        # Sadece sayısal değeri düşüyoruz, otomatik hesaplamayı etkilememesi için
        if deger == 1 and self.manual_kazalar[index] > 0:
            # Sadece bu tarih "Manuel Kaza" aralığındaysa düş
            t_date = datetime.datetime.strptime(tarih, "%Y-%m-%d").date()
            today = datetime.date.today()
            diff = (today - t_date).days
            if 0 < diff <= self.manual_kazalar[index]:
                self.manual_kazalar[index] -= 1
                data = {"baslangic": self.kaza_baslangic, "bitis": self.kaza_bitis, 
                        "is_kadin": self.is_kadin, "regl_suresi": self.regl_suresi,
                        "manual_kazalar": self.manual_kazalar}
                self.veriyi_dosyaya_yaz("namaz_v77_settings.json", data)

        self.namaz_liste_guncelle(); self.namaz_sayaci_guncelle()
        if deger == 1: 
            self.log_performans_arttir()
            self.bildirim_gonder("Tebrikler", "Bir kaza namazı eksildi!")

    def regl_tikla(self, tarih):
        current = [self.get_namaz_status(tarih, i) for i in range(5)]
        if all(x==3 for x in current):
            if tarih in self.namaz_veriler: del self.namaz_veriler[tarih]
        else:
            self.namaz_veriler[tarih] = [3]*5
        self.veriyi_dosyaya_yaz("namaz_v77_data.json", self.namaz_veriler)
        self.namaz_liste_guncelle(); self.namaz_sayaci_guncelle()

    def namaz_sayaci_guncelle(self):
        try:
            borclar = [0]*5
            if self.kaza_baslangic and self.kaza_bitis:
                t1 = datetime.datetime.strptime(self.kaza_baslangic, "%Y-%m-%d")
                t2 = datetime.datetime.strptime(self.kaza_bitis, "%Y-%m-%d")
                days = abs((t2-t1).days)
                borclar = [days]*5
                if self.is_kadin:
                    ind = int((days/30)*self.regl_suresi)
                    borclar = [x - ind for x in borclar]
            for i in range(5): borclar[i] += self.manual_kazalar[i]
            
            toplam_load = sum(borclar)
            odenen = 0
            
            mevcut_borclar = list(borclar) 

            for t_str, vals in self.namaz_veriler.items():
                t_date = datetime.datetime.strptime(t_str, "%Y-%m-%d").date()
                for i in range(5):
                    durum = vals[i]
                    is_virtual = False
                    if self.kaza_baslangic and self.kaza_bitis:
                        if self.kaza_baslangic <= t_str < self.kaza_bitis: is_virtual = True
                    if not is_virtual:
                        diff = (datetime.date.today() - t_date).days
                        if 0 < diff <= self.manual_kazalar[i]: is_virtual = True
                    if is_virtual:
                        if durum == 1: 
                            mevcut_borclar[i] -= 1
                            odenen += 1
                    else:
                        if durum == 2: mevcut_borclar[i] += 1

            self.mevcut_borclar_listesi = mevcut_borclar
            self.lbl_ozet.text = f"Sabah:{mevcut_borclar[0]} Öğle:{mevcut_borclar[1]} İkindi:{mevcut_borclar[2]} Akşam:{mevcut_borclar[3]} Yatsı:{mevcut_borclar[4]}"
            
            if toplam_load > 0:
                yuzde = (odenen/toplam_load)*100
                self.progress.value = yuzde
                self.lbl_yuzde.text = f"%{yuzde:.1f} Tamamlandı"
            else:
                self.progress.value = 0
                self.lbl_yuzde.text = "%0"
            
            self.hesapla_zincir()
            
        except: pass

    def oruc_liste_guncelle(self):
        start_year = 2015 
        if self.kaza_baslangic:
            try: start_year = int(self.kaza_baslangic.split("-")[0])
            except: pass
        current_year = datetime.date.today().year + 1
        data = []
        toplam_kalan = 0
        for yil in range(current_year, start_year - 1, -1):
            yil_str = str(yil)
            yil_veri = self.oruc_veriler.get(yil_str, {"borc": 0, "tutulan": 0})
            borc = yil_veri["borc"]
            tutulan = yil_veri["tutulan"]
            kalan = max(0, borc - tutulan)
            toplam_kalan += kalan
            durum_text = f"Kalan: {kalan} Gün"
            durum_renk = [0.8, 0.2, 0.2, 1] 
            if borc > 0 and kalan == 0:
                durum_text = "TAMAMLANDI"
                durum_renk = [0, 0.6, 0, 1] 
            elif borc == 0:
                durum_text = "BORÇ YOK"
                durum_renk = [0.6, 0.6, 0.6, 1] 
            progress = 0
            if borc > 0: progress = (tutulan / borc) * 100
            if progress > 100: progress = 100
            data.append({
                'yil_id': yil_str,
                'yil_text': f"Ramazan {yil_str}",
                'borc_sayi': str(borc),
                'tutulan_sayi': str(tutulan),
                'durum_ozet': durum_text,
                'durum_renk': durum_renk,
                'progress_val': progress
            })
        self.oruc_liste_widget.data = data
        self.lbl_oruc_toplam.text = f"TOPLAM ORUÇ BORCU: {toplam_kalan} GÜN"

    def oruc_guncelle(self, yil_id, tip, degisim):
        yil_veri = self.oruc_veriler.get(yil_id, {"borc": 0, "tutulan": 0})
        if tip == "borc":
            yeni_deger = max(0, min(30, yil_veri["borc"] + degisim))
            yil_veri["borc"] = yeni_deger
        elif tip == "tutulan":
            yeni_deger = max(0, yil_veri["tutulan"] + degisim)
            yil_veri["tutulan"] = yeni_deger
        self.oruc_veriler[yil_id] = yil_veri
        self.veriyi_dosyaya_yaz("oruc_v77_data.json", self.oruc_veriler)
        self.oruc_liste_guncelle()

    # --- 0 SİLME FONKSİYONU ---
    def on_odaklanma(self, instance, focused):
        if focused:
            if instance.text == "0": instance.text = ""
        else:
            if instance.text.strip() == "": instance.text = "0"

    # --- NAMAZ HESAPLAYICI (SABİT BUTONLU) ---
    def namaz_hesaplayici_ac(self):
        try:
            dialog_main = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(550), spacing=0, padding=0)
            
            summary_card = MDCard(size_hint_y=None, height=dp(80), md_bg_color=self.theme_cls.primary_color, padding=dp(10), radius=[0,0,10,10])
            total_debt = sum(self.mevcut_borclar_listesi)
            lbl_total = MDLabel(text=f"Toplam Kalan Borç\n{total_debt} Vakit", halign="center", theme_text_color="Custom", text_color=[1,1,1,1], font_style="H6", bold=True)
            summary_card.add_widget(lbl_total)
            dialog_main.add_widget(summary_card)
            
            scroll = ScrollView(size_hint_y=1)
            icerik_kutusu = MDBoxLayout(orientation="vertical", adaptive_height=True, padding=dp(10), spacing=dp(15))
            scroll.add_widget(icerik_kutusu)
            dialog_main.add_widget(scroll)

            row_kadin = MDBoxLayout(adaptive_height=True, spacing=dp(10))
            row_kadin.add_widget(MDLabel(text="Kadın Modu:", theme_text_color="Secondary", size_hint_x=0.7))
            sw = MDSwitch(active=self.is_kadin, size_hint_x=0.3)
            row_kadin.add_widget(sw)
            icerik_kutusu.add_widget(row_kadin)
            
            # STANDART TEXT FIELD (GÜVENLİ)
            txt_regl = MDTextField(hint_text="Regl Süresi", text=str(self.regl_suresi), halign="center")
            txt_regl.bind(focus=self.on_odaklanma)
            icerik_kutusu.add_widget(txt_regl)
            
            self.btn_basla = MDRoundFlatButton(
                text=f"Başlangıç: {self.kaza_baslangic}" if self.kaza_baslangic else "Ergenlik Tarihi Seç",
                on_release=lambda x: self.tarih_secici_ac("baslangic"), size_hint_x=1
            )
            icerik_kutusu.add_widget(self.btn_basla)
            
            self.btn_bitis = MDRoundFlatButton(
                text=f"Bitiş: {self.kaza_bitis}" if self.kaza_bitis else "Düzenli Namaz Başlangıcı",
                on_release=lambda x: self.tarih_secici_ac("bitis"), size_hint_x=1
            )
            icerik_kutusu.add_widget(self.btn_bitis)

            icerik_kutusu.add_widget(MDLabel(text="Ekstra Kaza Sayıları:", theme_text_color="Secondary", font_style="Caption"))
            grid = MDGridLayout(cols=5, spacing=dp(5), adaptive_height=True)
            inputs = []
            labels = ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"]
            for i in range(5):
                # STANDART TEXT FIELD + BIND (GÜVENLİ)
                t = MDTextField(hint_text=labels[i][0], text=str(self.manual_kazalar[i]), input_filter="int", halign="center")
                t.bind(focus=self.on_odaklanma)
                inputs.append(t)
                grid.add_widget(t)
            icerik_kutusu.add_widget(grid)
            
            btn_yedek = MDFlatButton(text="YEDEK AL (ZIP)", theme_text_color="Custom", text_color=[0, 0.5, 0, 1], on_release=lambda x: self.verileri_yedekle())
            icerik_kutusu.add_widget(btn_yedek)
            
            icerik_kutusu.add_widget(MDBoxLayout(size_hint_y=None, height=dp(20)))

            def kaydet(*args):
                self.is_kadin = sw.active
                try: self.regl_suresi = int(txt_regl.text)
                except: pass
                self.manual_kazalar = [int(x.text or 0) for x in inputs]
                data = {"baslangic": self.kaza_baslangic, "bitis": self.kaza_bitis, 
                        "is_kadin": self.is_kadin, "regl_suresi": self.regl_suresi,
                        "manual_kazalar": self.manual_kazalar}
                self.veriyi_dosyaya_yaz("namaz_v77_settings.json", data)
                self.dialog_namaz.dismiss()
                self.namaz_sayaci_guncelle()
                self.namaz_liste_guncelle()
                self.oruc_liste_guncelle()
                self.bildirim_gonder("Ayarlar", "Hesaplamalar güncellendi.")

            button_box = MDBoxLayout(size_hint_y=None, height=dp(70), padding=[dp(10), dp(10), dp(10), dp(10)])
            btn_kaydet = MDRaisedButton(text="HESAPLA VE KAYDET", on_release=kaydet, size_hint_x=1, pos_hint={'center_y': 0.5})
            button_box.add_widget(btn_kaydet)
            dialog_main.add_widget(button_box)

            self.dialog_namaz = MDDialog(title="Borç & Ayarlar", type="custom", content_cls=dialog_main)
            self.dialog_namaz.open()
        except Exception as e:
            toast("Hata oluştu: " + str(e))
            print(traceback.format_exc())

    def get_file_path(self, filename):
        return os.path.join(self.user_data_dir, filename)

    def veriyi_dosyaya_yaz(self, dosya, veri):
        path = self.get_file_path(dosya)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(veri, f)

    def verileri_yukle(self, dosya):
        path = self.get_file_path(dosya)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return {}
        return {}

if __name__ == "__main__":
    NamazTakipV77App().run()