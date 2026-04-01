import time
from datetime import datetime

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ==============================
# KONFIGURASI EDGE PROFILE
# ==============================
edge_options = Options()
edge_options.add_argument(
    r"--user-data-dir=C:\Users\POLI UMUM\AppData\Local\Microsoft\Edge\User Data"
)
edge_options.add_argument("--profile-directory=Default")
edge_options.add_argument("--remote-debugging-port=9222")
edge_options.add_argument("--disable-dev-shm-usage")
edge_options.add_argument("--no-sandbox")
edge_options.add_argument("--disable-gpu")


# ==============================
# START EDGE
# ==============================
driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 5)

# ==============================
# BUKA WEBSITE
# ==============================
driver.get("https://sehatindonesiaku.kemkes.go.id")

# ==============================
# CEK APAKAH MASIH LOGIN
# ==============================
current_url = driver.current_url.lower()
print("URL:", current_url)

if "login" in current_url:
    input(
        "\n🔐 Session habis.\n"
        "Silakan LOGIN MANUAL + CAPTCHA di Edge.\n\n"
        "Jika sudah masuk DASHBOARD, tekan ENTER di sini..."
    )
else:
    print("✅ Session aktif, langsung dashboard")


try:
    ckg_umum_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'CKG Umum')]"))
    )
    ckg_umum_btn.click()
    print("✅ CKG Umum diklik")
except:
    print("ℹ️ CKG Umum tidak muncul / sudah aktif")

menu_pendaftaran = wait.until(
    EC.element_to_be_clickable((By.ID, "menu_cari/daftarkan_individu"))
)
menu_pendaftaran.click()


def klik_daftar_baru():
    daftar_baru_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//div[normalize-space()='Daftar Baru']]")
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", daftar_baru_btn
    )

    daftar_baru_btn.click()

    print("✅ Tombol Daftar Baru diklik")


klik_daftar_baru()

# ===== BACA EXCEL =====
df = pd.read_excel("datasehat.xlsx", sheet_name="daftar", dtype=str)
df = df.fillna("")

# ===== AMBIL BARIS PERTAMA DULU (TEST) =====
i = 0
nik = str(df.loc[i, "nik"])
nama = str(df.loc[i, "nama"]).upper()
tanggal_str = str(df.loc[i, "tanggal_lahir"])
jenis = df.loc[i, "jenis_kelamin"]
no_whatsapp = df.loc[i, "nomor_whatsapp"]
nama_pekerjaan = df.loc[i, "pekerjaan"]

print("NIK dari excel:", nik)
print("NAMA dari Excel:", nama)
print("Tanggal Lahir:", tanggal_str)
print("Jenis Kelamin:", jenis)
print("WA", no_whatsapp)
print("Perkerjaan:", nama_pekerjaan)

time.sleep(1)


def isi_nik(nik):
    field = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "nik")))

    field.clear()
    field.send_keys(str(nik))

    print("✅ NIK diisi")


def klik_cek_nik():
    """Klik tombol Cek NIK setelah NIK diisi"""
    cek_nik_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(normalize-space(), 'Cek NIK')]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cek_nik_btn)
    cek_nik_btn.click()
    print("✅ Tombol Cek NIK diklik")


def klik_gunakan_data():
    """Klik tombol Gunakan Data setelah hasil loading muncul"""
    gunakan_data_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(normalize-space(), 'Gunakan Data')]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", gunakan_data_btn)
    gunakan_data_btn.click()
    print("✅ Tombol Gunakan Data diklik")


def klik_tanggal_pemeriksaan():
    """Klik field tanggal pemeriksaan - cari tombol kalender"""
    print("🔍 Mencari field tanggal pemeriksaan...")

    # Debug - print semua button di halaman
    try:
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"  Total button di halaman: {len(all_buttons)}")
        for btn in all_buttons[:15]:
            try:
                classes = btn.get_attribute("class") or ""
                text = btn.text or ""
                if "flex flex-col" in classes or "rounded" in classes:
                    print(f"    button: class='{classes[:80]}', text='{text[:30]}'")
            except:
                pass
    except Exception as e:
        print(f"  Debug error: {e}")

    # Cari button dengan struktur kalender (mengandung angka tanggal)
    # Pattern: span dengan font-bold text-[18px] dan angka tanggal
    tanggal_button_selectors = [
        # Button dengan class flex-col (struktur kalender)
        "//button[contains(@class,'flex-col') and contains(@class,'rounded') and .//span[contains(@class,'font-bold')]]",
        # Button yang mengandung angka (tanggal)
        "//button[.//span[contains(@class,'text-[18px]')]]",
        # Semua button dengan bg-theme
        "//button[contains(@class,'bg-theme')]",
        # Button dengan struktur span.font-bold.text-[18px]
        "//button[.//span[@class='font-bold text-[18px] text-white']]",
    ]

    for selector in tanggal_button_selectors:
        try:
            buttons = driver.find_elements(By.XPATH, selector)
            print(f"  Cek selector: {selector[:60]}... -> {len(buttons)} ditemukan")
            for idx, btn in enumerate(buttons):
                try:
                    text = btn.text.strip()
                    # Cek apakah button ini adalah tanggal (mengandung angka 1-31)
                    spans = btn.find_elements(By.TAG_NAME, "span")
                    for span in spans:
                        span_text = span.text.strip()
                        # Jika span mengandung angka tanggal (1-31)
                        if span_text.isdigit() and 1 <= int(span_text) <= 31:
                            print(f"  ✅ Button tanggal ditemukan: '{text}'")
                            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                            time.sleep(0.3)
                            btn.click()
                            print(f"  ✅ Tanggal {span_text} diklik!")
                            return
                except Exception as e:
                    continue
        except Exception as e:
            print(f"  Selector error: {e}")
            continue

    raise Exception("❌ Gagal menemukan button tanggal pemeriksaan")


def is_datepicker_visible():
    """Cek apakah datepicker/mx-calendar visible di halaman"""
    try:
        # Cek mx-calendar
        calendars = driver.find_elements(By.CSS_SELECTOR, ".mx-calendar")
        for cal in calendars:
            if cal.is_displayed():
                return True

        # Cek header label datepicker
        headers = driver.find_elements(By.CSS_SELECTOR, ".mx-calendar-header-label")
        for h in headers:
            if h.is_displayed():
                return True

        # Cek picker container
        pickers = driver.find_elements(By.CSS_SELECTOR, ".mx-datepicker")
        for p in pickers:
            if p.is_displayed():
                return True
    except:
        pass
    return False


def pilih_tanggal_pemeriksaan(tanggal_str):
    """Pilih tanggal pemeriksaan di datepicker"""
    target = datetime.strptime(tanggal_str, "%Y-%m-%d")
    target_year = target.year
    target_month = target.month
    target_day = target.day

    bulan_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }

    print(f"🎯 Target: {target_day} {target_month} {target_year}")

    # Tunggu datepicker muncul
    time.sleep(0.5)

    max_attempts = 24  # 12 bulan x 2 arah
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        try:
            header_label = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".mx-calendar-header-label")
                )
            )
            header_text = header_label.get_attribute("innerText").strip()
            print(f"  Attempt {attempt}: Header = '{header_text}'")

            current_year = int(header_text[-4:])
            current_month_text = header_text[:3]
            current_month = bulan_map.get(current_month_text, 0)

            if current_year != target_year:
                if current_year > target_year:
                    driver.find_element(By.CSS_SELECTOR, "button.mx-btn-icon-double-left").click()
                else:
                    driver.find_element(By.CSS_SELECTOR, "button.mx-btn-icon-double-right").click()
                time.sleep(0.3)
                continue

            if current_month != target_month:
                if current_month > target_month:
                    driver.find_element(By.CSS_SELECTOR, "button.mx-btn-icon-left").click()
                else:
                    driver.find_element(By.CSS_SELECTOR, "button.mx-btn-icon-right").click()
                time.sleep(0.3)
                continue

            # Tahun & bulan cocok - cari tanggal
            print(f"  Bulan & Tahun sudah cocok, cari tanggal {target_day}")
            time.sleep(0.3)

            # Coba beberapa cara untuk klik tanggal
            tanggal_selectors = [
                f"//td[@title='{tanggal_str}']",
                f"//td[contains(@class,'cell') and contains(@class,'not-current-month')]/../td[@title='{tanggal_str}']",
                f"//div[contains(@class,'mx-calendar')]//td[.//span[text()='{target_day}']]",
                f"//td[contains(@class,'cell')]//span[text()='{target_day}']/..",
            ]

            for tgl_sel in tanggal_selectors:
                try:
                    tanggal_element = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, tgl_sel))
                    )
                    tanggal_element.click()
                    print(f"✅ Tanggal {target_day} dipilih!")
                    return
                except:
                    continue

            # Jika tidak ketemu, coba klik next/prev month
            print(f"  Tanggal {target_day} tidak ditemukan di bulan ini, coba next month")
            driver.find_element(By.CSS_SELECTOR, "button.mx-btn-icon-right").click()
            time.sleep(0.3)

        except Exception as e:
            print(f"  Error attempt {attempt}: {e}")
            time.sleep(0.5)
            continue

    raise Exception(f"❌ Gagal memilih tanggal {tanggal_str} setelah {max_attempts} attempts")


def klik_selanjutnya():
    """Klik tombol Selanjutnya"""
    # Tunggu sebentar agar datepicker tertutup dan tombol visible
    time.sleep(1)

    selectors = [
        "//button[contains(normalize-space(), 'Selanjutnya')]",
        "//button[contains(@class, 'btn') and contains(., 'Selanjutnya')]",
        "//div[contains(@class,'flex')]//button[contains(., 'Selanjutnya')]",
        "//button[@type='button' and contains(., 'Selanjutnya')]",
    ]

    for idx, selector in enumerate(selectors):
        try:
            selanjutnya_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", selanjutnya_btn)
            time.sleep(0.3)
            selanjutnya_btn.click()
            print(f"✅ Tombol Selanjutnya diklik (selector #{idx+1})")
            return
        except Exception as e:
            print(f"ℹ️ Selector #{idx+1} gagal")
            continue

    raise Exception("❌ Gagal klik tombol Selanjutnya")


def isi_nama(nama):
    field = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@placeholder='Masukkan nama lengkap']")
        )
    )

    field.clear()
    field.send_keys(nama)

    print("✅ Nama diisi")


def buka_datepicker_tgl_lahir():
    field = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//div[contains(@class,'mx-datepicker')]"
                "[.//div[contains(text(),'Pilih tanggal lahir')]]",
            )
        )
    )

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", field)

    field.click()

    print("📅 Datepicker dibuka")


def pilih_tanggal_otomatis(tanggal_str):

    target = datetime.strptime(tanggal_str, "%Y-%m-%d")
    target_year = target.year
    target_month = target.month

    buka_datepicker_tgl_lahir()

    bulan_map = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    while True:
        header_label = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".mx-calendar-header-label")
            )
        )

        header_text = header_label.get_attribute("innerText").strip()
        print("HEADER TERBACA:", header_text)

        current_year = int(header_text[-4:])
        current_month_text = header_text[:3]
        current_month = bulan_map[current_month_text]

        # jika tahun belum cocok
        if current_year != target_year:
            if current_year > target_year:
                driver.find_element(
                    By.CSS_SELECTOR, "button.mx-btn-icon-double-left"
                ).click()
            else:
                driver.find_element(
                    By.CSS_SELECTOR, "button.mx-btn-icon-double-right"
                ).click()

            time.sleep(0.2)
            continue

        # jika tahun sudah cocok tapi bulan belum
        if current_month != target_month:
            if current_month > target_month:
                driver.find_element(By.CSS_SELECTOR, "button.mx-btn-icon-left").click()
            else:
                driver.find_element(By.CSS_SELECTOR, "button.mx-btn-icon-right").click()

            time.sleep(0.2)
            continue

        # jika tahun & bulan sudah cocok
        break

    # klik tanggal
    tanggal_element = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, f"//td[@title='{tanggal_str}']"))
    )

    tanggal_element.click()

    print(f"✅ Tanggal dipilih: {tanggal_str}")


def pilih_jenis_kelamin(jenis):

    dropdown = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//div[contains(text(),'Jenis Kelamin')]/following::div[contains(@class,'font-medium')][1]",
            )
        )
    )

    ActionChains(driver).move_to_element(dropdown).pause(0.2).click().perform()

    print("🔽 Dropdown jenis kelamin dibuka (real click)")

    # Tunggu popup benar-benar muncul
    option = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//div[contains(@class,'absolute')]//div[normalize-space()='{jenis}']",
            )
        )
    )

    ActionChains(driver).move_to_element(option).pause(0.2).click().perform()

    print(f"✅ Jenis kelamin dipilih: {jenis}")


def isi_nomor_whatsapp(no_whatsapp):
    field = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@placeholder='Masukkan nomor whatsapp']")
        )
    )

    field.clear()
    field.send_keys(no_whatsapp)

    print(f"✅ Nomor WA diisi {no_whatsapp}")


def pilih_pekerjaan(nama_pekerjaan):

    # 1️⃣ Klik field pekerjaan (div flex parent)
    field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//div[contains(text(),'Pekerjaan')]/following::div[contains(@class,'cursor-pointer')][1]",
            )
        )
    )

    ActionChains(driver).move_to_element(field).pause(0.2).click().perform()

    print("📂 Dropdown pekerjaan dibuka")
    time.sleep(2)
    # 2️⃣ Tunggu modal muncul dan klik berdasarkan text
    option = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//div[normalize-space()='{nama_pekerjaan}']")
        )
    )

    ActionChains(driver).move_to_element(option).pause(0.2).click().perform()

    print(f"✅ Pekerjaan dipilih: {nama_pekerjaan}")


isi_nik(nik)
klik_cek_nik()
klik_gunakan_data()

# Tunggu datepicker terbuka dan form terisi
time.sleep(3)

# Tanggal pemeriksaan (ambil dari Excel atau hardcode, sesuaikan dengan kolom di Excel)
tanggal_pemeriksaan = str(df.loc[i, "tanggal_pemeriksaan"]) if "tanggal_pemeriksaan" in df.columns else datetime.now().strftime("%Y-%m-%d")
klik_tanggal_pemeriksaan()
time.sleep(1)  # tunggu tanggal terpilih
klik_selanjutnya()

# Tunggu page loading
time.sleep(2)

# Klik tombol Lanjutkan
def klik_lanjutkan():
    selectors = [
        "//button[contains(normalize-space(), 'Lanjutkan')]",
        "//button[contains(translate(., 'LANJUTKAN', 'lanjutkan'), 'lanjutkan')]",
    ]
    for sel in selectors:
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, sel))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.5)
            btn.click()
            print("✅ Tombol Lanjutkan diklik")
            time.sleep(2)
            return
        except:
            continue
    print("ℹ️ Tombol Lanjutkan tidak ditemukan")

klik_lanjutkan()

# Klik tombol Selanjutnya lagi
def klik_selanjutnya_lagi():
    selectors = [
        "//button[contains(normalize-space(), 'Selanjutnya')]",
        "//button[contains(translate(., 'SELANJUTNYA', 'selanjutnya'), 'selanjutnya')]",
    ]
    for sel in selectors:
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, sel))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.5)
            btn.click()
            print("✅ Tombol Selanjutnya (lagi) diklik")
            time.sleep(2)
            return
        except:
            continue
    print("ℹ️ Tombol Selanjutnya tidak ditemukan")

klik_selanjutnya_lagi()

# Klik tombol Pilih
def klik_pilih():
    selectors = [
        "//button[contains(normalize-space(), 'Pilih')]",
        "//button[contains(translate(., 'PILIH', 'pilih'), 'pilih')]",
    ]
    for sel in selectors:
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, sel))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.5)
            btn.click()
            print("✅ Tombol Pilih diklik")
            time.sleep(2)
            return
        except:
            continue
    print("ℹ️ Tombol Pilih tidak ditemukan")

klik_pilih()

# Klik tombol Daftarkan dengan NIK
def klik_daftarkan_dengan_nik():
    selectors = [
        "//button[contains(normalize-space(), 'Daftarkan dengan NIK')]",
        "//button[contains(., 'Daftarkan dengan NIK')]",
    ]
    for sel in selectors:
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, sel))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.5)
            btn.click()
            print("✅ Tombol Daftarkan dengan NIK diklik")
            time.sleep(2)
            return
        except:
            continue
    print("ℹ️ Tombol Daftarkan dengan NIK tidak ditemukan")

klik_daftarkan_dengan_nik()

# Klik tombol Tutup
def klik_tutup():
    selectors = [
        "//button[contains(normalize-space(), 'Tutup')]",
        "//button[contains(translate(., 'TUTUP', 'tutup'), 'tutup')]",
        "//button[contains(@class,'btn-close')]",
    ]
    for sel in selectors:
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, sel))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.5)
            btn.click()
            print("✅ Tombol Tutup diklik")
            time.sleep(2)
            return
        except:
            continue
    print("ℹ️ Tombol Tutup tidak ditemukan")

klik_tutup()

print("🎯 Selesai semua")


# clik simpan
try:
    simpan_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Simpan')]"))
    )
    simpan_btn.click()
    print("✅ simpan diklik")
except:
    print("ℹ️ CKG Umum tidak muncul / sudah aktif")


# ===== TUNGGU INPUT MUNCUL =====
wait = WebDriverWait(driver, 1000)

input_nama = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='searchNik']")))

# ===== ISI INPUT =====
input_nama.clear()
input_nama.send_keys(nik)  # Gunakan NIK bukan nama

print("✅ NIK berhasil diinput")
input_nama.send_keys(Keys.ENTER)

# mulaibutton
# mulai_btn = wait.until(
#     EC.element_to_be_clickable(
#         (By.XPATH, "//button[contains(., 'Mulai')]")
#     )
# )
# mulai_btn.click()

# print("✅ Tombol Mulai diklik")


# clik mulaipemeriksaan dipake nanti saja kalau sudah production
# try:
#     mulaipemeriksaan_btn = wait.until(
#         EC.element_to_be_clickable(
#             (By.XPATH, "//button[contains(., 'Mulai Pemeriksaan')]")
#         )
#     )
#     mulaipemeriksaan_btn.click()
#     print("✅ mulai pemeriksaan diklik")
# except:
#     print("ℹ️ mulai pemeriksaan tidak muncul / sudah aktif")
def klik_konfirmasi_hadir(tanggal_pemeriksaan):
    print(f"🔍 DEBUG: tanggal_pemeriksaan dari Excel = '{tanggal_pemeriksaan}'")

    # Convert tanggal 2026-04-01 -> 01 apr 2026
    tgl_obj = datetime.strptime("2026-04-01", "%Y-%m-%d")
    tgl_display = tgl_obj.strftime("%d %b %Y").lower()
    print(f"🔍 DEBUG: tanggal display = '{tgl_display}'")

    print(f"🔍 Mencari row dengan tanggal: {tgl_display}")

    try:
        # Cari row berdasarkan tanggal di td, lalu button Konfirmasi Hadir
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                    f"//tr[.//td[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{tgl_display}')]]"
                    f"//button[.//text()[contains(., 'Konfirmasi Hadir')]]"
                )
            )
        )

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        time.sleep(0.3)
        btn.click()

        print(f"✅ Tombol Konfirmasi Hadir diklik")
        return True

    except Exception as e:
        print(f"❌ Gagal klik Konfirmasi Hadir: {e}")
        return False

# Klik checkbox "Peserta memahami & bersedia untuk menjalani prosedur CKG"
def klik_checkbox_CKG():
    try:
        checkbox = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='verify']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", checkbox)
        time.sleep(0.5)

        # Click dengan ActionChains
        ActionChains(driver).move_to_element(checkbox).pause(0.2).click().perform()
        time.sleep(1)

        # Check apakah sudah ter-check
        is_checked = driver.execute_script("return arguments[0].checked;", checkbox)
        print(f"🔍 Checkbox checked: {is_checked}")

        # Tunggu tombol Hadir menjadi aktif
        time.sleep(1)

        return True
    except Exception as e:
        print(f"❌ Gagal klik checkbox: {e}")
        return False

klik_checkbox_CKG()
time.sleep(1)

# Klik tombol Hadir
def klik_hadir():
    # Tunggu tombol Hadir visible dan enabled
    time.sleep(2)

    try:
        # Cari semua button yang mengandung "Hadir"
        buttons = driver.find_elements(By.XPATH, "//button[contains(normalize-space(), 'Hadir')]")
        print(f"🔍 Ditemukan {len(buttons)} button dengan teks 'Hadir'")

        for idx, btn in enumerate(buttons):
            is_displayed = btn.is_displayed()
            is_enabled = btn.is_enabled()
            classes = btn.get_attribute("class") or ""
            print(f"  Button #{idx}: displayed={is_displayed}, enabled={is_enabled}, class={classes[:60]}")

        # Cek apakah ada overlay yang blocking
        overlays = driver.find_elements(By.CSS_SELECTOR, "[class*='fixed'][class*='inset-0'][class*='bg-']")
        for ov in overlays:
            try:
                if ov.is_displayed() and "rgba" in (ov.get_attribute("class") or ""):
                    print(f"🔍 Overlay ditemukan, klik untuk dismiss...")
                    driver.execute_script("arguments[0].click();", ov)
                    time.sleep(1)
            except:
                pass

        # Retry klik tombol Hadir
        buttons = driver.find_elements(By.XPATH, "//button[contains(normalize-space(), 'Hadir')]")
        for idx, btn in enumerate(buttons):
            try:
                if btn.is_displayed() and btn.is_enabled():
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", btn)
                    print(f"✅ Tombol Hadir #{idx} diklik via JS")
                    return True
            except Exception as e:
                print(f"  Button #{idx} JS error: {e}")
                continue

    except Exception as e:
        print(f"❌ Error cari tombol Hadir: {e}")

    print("ℹ️ Tombol Hadir tidak ditemukan atau tidak bisa diklik")
    return False


# =================== ESEKUSI ===================
klik_konfirmasi_hadir(tanggal_pemeriksaan)
time.sleep(2)
klik_checkbox_CKG()
time.sleep(3)  # tunggu tombol Hadir menjadi aktif
klik_hadir()


def klik_tombol_jika_ada(teks_tombol):
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//button[.//text()[contains(., '{teks_tombol}')]]")
            )
        )

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)

        ActionChains(driver).move_to_element(btn).pause(0.2).click().perform()

        print(f"✅ Tombol '{teks_tombol}' diklik")

        return True

    except:
        print(f"ℹ️ Tombol '{teks_tombol}' tidak muncul / sudah dilewati")
        return False


klik_tombol_jika_ada("Mulai Pemeriksaan")


# KIRIMBUTTON
def klik_kirim():
    try:
        kirim_btn = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='sv-nav-complete']//input[@type='button']")
            )
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", kirim_btn
        )
        driver.execute_script("arguments[0].click();", kirim_btn)
        print("✅ Form dikirim")
        return True
    except:
        print("ℹ️ Tombol kirim tidak muncul / sudah dilewati")
        return False


# gizi BB-TB-LP
def klik_input_data_by_row(row_id):
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[@id='{row_id}']//button"))
        )

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)

        ActionChains(driver).move_to_element(btn).click().perform()

        print(f"✅ Input Data diklik ({row_id})")
        return True
    except:
        print(f"ℹ️ Input tidak bisa diisi ({row_id})")
        return False


# RADIOSRUVEYJS
def klik_radio_surveyjs_by_value(value):
    try:
        label = WebDriverWait(driver, 4).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    f"//label[contains(@class,'sd-selectbase__label')][.//input[@value='{value}']]",
                )
            )
        )

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", label)

        ActionChains(driver).move_to_element(label).pause(0.2).click().perform()

        print(f"✅ Radio dengan value {value} sudah diklik")
        return True
    except:
        print(f"ℹ️ Tombol {value} tidak muncul / sudah dilewati")
        return False


# INPUTFORMMMMM
klik_input_data_by_row("rowfrm000051")


def normalize_number(val):
    return str(val).replace(",", ".")


def isi_input_text_surveyjs(xpath_input, nilai):
    try:
        nilai = normalize_number(nilai)

        field = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, xpath_input))
        )

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", field)

        field.click()
        field.clear()
        field.send_keys(nilai)
        field.send_keys(Keys.TAB)

        print(f"✅ Input (SurveyJS) diisi & committed: {nilai}")
        return True
    except:
        print(f"ℹ️ Input tidak bisa diisi")
        return False


isi_input_text_surveyjs("//*[@id='sq_100i']", df.loc[ckg, "BB"])  # berat badan
time.sleep(0.3)
isi_input_text_surveyjs("//*[@id='sq_101i']", df.loc[ckg, "TB"])  # tinggi badan
time.sleep(0.3)
isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[ckg, "LP"])  # lingkar perut
time.sleep(0.3)
klik_kirim()
time.sleep(3)


klik_input_data_by_row("rowfrm000256")
klik_radio_surveyjs_by_value("PPV00000328")
isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[ckg, "GDS"])
klik_kirim()
time.sleep(3)

klik_input_data_by_row("rowfrm000265")
klik_radio_surveyjs_by_value("PPV00000380")
isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[ckg, "sistol"])
isi_input_text_surveyjs("//*[@id='sq_103i']", df.loc[ckg, "diastol"])
klik_kirim()
time.sleep(3)


# ==============================
# PAUSE BIAR BROWSER TIDAK NUTUP
# ==============================
input(
    "\nBrowser siap.\n"
    "Session aktif.\n"
    "Tekan ENTER untuk lanjut ke step berikutnya (radio / form)..."
)
