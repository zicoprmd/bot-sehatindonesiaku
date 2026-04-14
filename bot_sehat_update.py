from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
import pandas as pd
from selenium.webdriver.common.keys import Keys
import logging
from selenium.webdriver.common.action_chains import ActionChains
import time

#==============================
# LOGGING
#==============================
logging.basicConfig(
    filename="bot_sehatindo.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)

def log(msg):
    print(msg)
    logger.info(msg)

#==============================
# KONFIGURASI
#==============================
EDGE_PROFILE = r"C:\Users\ThinkPad\AppData\Local\Microsoft\Edge\User Data"
WEBSITE_URL = "https://sehatindonesiaku.kemkes.go.id"
EXCEL_FILE = "datasehat.xlsx"
PROGRESS_FILE = "progress.txt"

#==============================
# BROWSER SETUP
#==============================
def init_browser():
    options = Options()
    options.add_argument(f"--user-data-dir={EDGE_PROFILE}")
    options.add_argument("--profile-directory=Default")

    driver = webdriver.Edge(options=options)
    driver.implicitly_wait(0)  # NO implicit wait - kita kontrol manual
    return driver, WebDriverWait(driver, 10)

#==============================
# HELPER: SIMPLE CLICK (tanpa retry - cepat)
#==============================
def simple_click(wait, locator, log_teks=""):
    """Klik element simple, tanpa retry. Timeout 3 detik agar skip cepat."""
    try:
        el = WebDriverWait(wait._driver, 3).until(
            EC.element_to_be_clickable(locator)
        )
        wait._driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        wait._driver.execute_script("arguments[0].click();", el)
        if log_teks:
            log(f"✅ {log_teks}")
        return True
    except:
        if log_teks:
            log(f"⚠️ Skip: {log_teks}")
        return False

def js_click(wait, el, log_teks=""):
    """Klik element via JS."""
    try:
        wait._driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        wait._driver.execute_script("arguments[0].click();", el)
        if log_teks:
            log(f"✅ {log_teks}")
        return True
    except:
        if log_teks:
            log(f"⚠️ Gagal: {log_teks}")
        return False

#==============================
# HELPER: CEK ELEMENT ADA
#==============================
def element_exists(wait, locator, timeout=None):
    """Cek apakah element ada"""
    t = timeout or 2
    try:
        WebDriverWait(wait._driver, t).until(
            EC.presence_of_element_located(locator)
        )
        return True
    except:
        return False

def wait_visible(wait, locator, timeout=None):
    """Tunggu element visible, return element atau None"""
    t = timeout or 2
    try:
        return WebDriverWait(wait._driver, t).until(
            EC.visibility_of_element_located(locator)
        )
    except:
        return None

#==============================
# HELPER: TOMBOL
#==============================
def klik_tombol(wait, teks, parent_xpath=None):
    """Klik tombol berdasarkan teks"""
    base = parent_xpath or "//"
    locator = (By.XPATH, f"{base}button[.//*[contains(normalize-space(), '{teks}')]]")
    return simple_click(wait, locator, f"Tombol: {teks}")

def klik_input_by_row(wait, row_id):
    """Klik Input Data di row tertentu"""
    return simple_click(wait, (By.XPATH, f"//div[@id='{row_id}']//button"),
                       f"Input row: {row_id}")

def klik_input_by_label(wait, nama_layanan):
    """Klik Input Data berdasarkan nama layanan"""
    return simple_click(wait, (
        By.XPATH,
        f"//tr[.//td[contains(., '{nama_layanan}')]]//button[contains(., 'Input Data')]"
    ), f"Input: {nama_layanan}")

#==============================
# HELPER: RADIO BUTTON
#==============================
def pilih_radio(wait, pertanyaan, jawaban):
    """Pilih radio button"""
    try:
        locator = (
            By.XPATH,
            f"//div[.//text()[contains(., '{pertanyaan}')]]"
            f"//label[normalize-space()='{jawaban}']"
        )
        el = WebDriverWait(wait._driver, 3).until(
            EC.element_to_be_clickable(locator)
        )
        wait._driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        wait._driver.execute_script("arguments[0].click();", el)
        log(f"✅ Radio: {pertanyaan} → {jawaban}")
        return True
    except:
        log(f"⚠️ Skip radio: {pertanyaan}")
        return False

#==============================
# HELPER: SURVEYJS RADIO
#==============================
def klik_radio_surveyjs(wait, value):
    """Klik radio SurveyJS"""
    try:
        locator = (
            By.XPATH,
            f"//label[contains(@class,'sd-selectbase__label')][.//input[@value='{value}']]"
        )
        el = WebDriverWait(wait._driver, 3).until(
            EC.element_to_be_clickable(locator)
        )
        wait._driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        wait._driver.execute_script("arguments[0].click();", el)
        return True
    except:
        return False

#==============================
# HELPER: DROPDOWN SURVEYJS
#==============================
def pilih_dropdown_surveyjs(wait, question_id, option_text):
    """Pilih dropdown SurveyJS"""
    try:
        dropdown = WebDriverWait(wait._driver, 3).until(
            EC.element_to_be_clickable((By.ID, question_id))
        )
        wait._driver.execute_script("arguments[0].scrollIntoView({block:'center'});", dropdown)
        wait._driver.execute_script("arguments[0].click();", dropdown)

        list_id = f"{question_id}_list"
        option = WebDriverWait(wait._driver, 3).until(
            EC.visibility_of_element_located((By.ID, list_id))
        )

        option_el = WebDriverWait(wait._driver, 3).until(
            EC.element_to_be_clickable((
                By.XPATH,
                f"//ul[@id='{list_id}']//*[text()='{option_text}']/ancestor::*[self::li or self::div][1]"
            ))
        )
        wait._driver.execute_script("arguments[0].click();", option_el)
        return True
    except Exception as e:
        log(f"⚠️ Dropdown gagal: {question_id} -> {option_text}")
        return False

#==============================
# HELPER: INPUT TEXT
#==============================
def isi_input_surveyjs(wait, xpath_or_id, nilai):
    """Isi input text SurveyJS"""
    try:
        nilai = str(nilai).replace(",", ".")
        locator = (
            (By.ID, xpath_or_id) if not xpath_or_id.startswith("//")
            else (By.XPATH, xpath_or_id)
        )
        field = WebDriverWait(wait._driver, 3).until(
            EC.element_to_be_clickable(locator)
        )
        wait._driver.execute_script("arguments[0].scrollIntoView({block:'center'});", field)
        field.click()
        field.clear()
        field.send_keys(nilai)
        field.send_keys(Keys.TAB)
        return True
    except:
        return False

#==============================
# HELPER: KIRIM
#==============================
def klik_kirim(wait):
    """Klik tombol Kirim"""
    try:
        locator = (By.XPATH, "//*[@id='sv-nav-complete']//input[@type='button']")
        el = WebDriverWait(wait._driver, 3).until(
            EC.element_to_be_clickable(locator)
        )
        wait._driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        wait._driver.execute_script("arguments[0].click();", el)
        time.sleep(2.5)  # Jeda SETELAH klik - agar halaman label selesai load
        log(f"✅ Kirim")
        return True
    except Exception as e:
        log(f"❌ Gagal Kirim")
        return False

#==============================
# HELPER: BACK
#==============================
def klik_back(wait):
    """Klik tombol kembali"""
    try:
        locator = (
            By.XPATH,
            "//img[contains(@class,'cursor-pointer') and contains(@src,'icon-arrow-left')]"
        )
        el = wait_visible(wait, locator)
        if not el:
            return False
        js_click(wait, el)
        return True
    except:
        return False

#==============================
# SEARCH PASIEN
#==============================
def cari_pasien(wait, nama):
    """Cari pasien"""
    try:
        input_nama = WebDriverWait(wait._driver, 3).until(
            EC.element_to_be_clickable((By.ID, "searchNik"))
        )
        wait._driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", input_nama
        )
        input_nama.clear()
        input_nama.send_keys(str(nama))
        input_nama.send_keys(Keys.ENTER)

        # Tunggu hasil dengan timeout sedang
        WebDriverWait(wait._driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//table//tr[td]"))
        )
        return True
    except:
        return False

def pasien_ditemukan(wait):
    """Cek apakah pasien ditemukan"""
    try:
        WebDriverWait(wait._driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//table//tr[td]"))
        )
        return True
    except:
        return False

def klik_mulai(wait, nama=None):
    """Klik tombol Mulai"""
    try:
        # Tunggu baris data muncul
        WebDriverWait(wait._driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//table//tr[td]"))
        )
        # Tunggu UI stabil
        time.sleep(0.5)

        locator = (
            By.XPATH,
            "//table//tr[1]//button[.//div[normalize-space()='Mulai']]"
        )
        btn = WebDriverWait(wait._driver, 3).until(
            EC.element_to_be_clickable(locator)
        )
        js_click(wait, btn, f"Mulai: {nama or 'pasien'}")
        return True
    except:
        log(f"⚠️ Gagal klik Mulai")
        return False

#==============================
# CEK SESSION
#==============================
def cek_session(driver, wait):
    """Cek login session"""
    current_url = driver.current_url.lower()
    log(f"URL: {current_url}")
    if "login" in current_url:
        input(
            "\n🔐 Session habis.\n"
            "Login MANUAL + CAPTCHA, tekan ENTER kalau sudah di DASHBOARD..."
        )

#==============================
# CHECKBOX
#==============================
def centang_lokasi_sama(wait):
    """Centang checkbox lokasi"""
    try:
        locator = (
            By.XPATH,
            "//div[contains(.,'Lokasi sama dengan puskesmas')]"
            "/preceding::div[contains(@class,'check')][1]"
        )
        checkbox = WebDriverWait(wait._driver, 15).until(
            EC.element_to_be_clickable(locator)
        )
        js_click(wait, checkbox, "Checkbox Lokasi")
        return True
    except:
        return False

#==============================
# LOAD / SAVE PROGRESS
#==============================
def load_progress():
    try:
        with open(PROGRESS_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_progress(index):
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(index))

#==============================
# SKRINING (tanpa time.sleep)
#==============================
def skrining_demografi(wait):
    klik_input_by_label(wait, "Demografi Dewasa Perempuan")
    klik_input_by_label(wait, "Demografi Lansia")
    klik_input_by_label(wait, "Demografi Dewasa Laki-Laki")
    pilih_radio(wait, "Status Perkawinan", "Menikah")
    pilih_radio(wait, "Apakah Anda sedang hamil", "Tidak")
    pilih_radio(wait, "Apakah Anda penyandang disabilitas?", "Non disabilitas")
    klik_kirim(wait)

def skrining_kanker_usus(wait):
    klik_input_by_label(wait, "Faktor Risiko Kanker Usus")
    pilih_radio(wait, "kanker kolorektal", "Tidak")
    klik_radio_surveyjs(wait, "PPV00000538")
    klik_kirim(wait)

def skrining_malaria(wait):
    klik_input_by_label(wait, "Faktor Risiko Malaria")
    klik_radio_surveyjs(wait, "PPV00000581")
    klik_radio_surveyjs(wait, "PPV00000591")
    klik_radio_surveyjs(wait, "PPV00000607")
    klik_radio_surveyjs(wait, "PPV00001233")
    klik_kirim(wait)

def skrining_tb(wait):
    klik_input_by_label(wait, "Faktor Risiko TB - Dewasa & Lansia")
    klik_radio_surveyjs(wait, "PPV00000883")
    klik_kirim(wait)

def skrining_cemas_remaja(wait):
    klik_input_by_label(wait, "Gejala Cemas Remaja")
    klik_radio_surveyjs(wait, "PPV00000593")
    klik_radio_surveyjs(wait, "PPV00000599")
    klik_radio_surveyjs(wait, "PPV00000605")
    klik_kirim(wait)

def skrining_depresi_remaja(wait):
    klik_input_by_label(wait, "Gejala Depresi Remaja")
    klik_radio_surveyjs(wait, "PPV00000627")
    klik_radio_surveyjs(wait, "PPV00000629")
    klik_radio_surveyjs(wait, "PPV00000633")
    klik_kirim(wait)

def skrining_reproduksi_putra(wait):
    klik_input_by_label(wait, "Kesehatan Reproduksi Putra - Anak Sekolah")
    klik_radio_surveyjs(wait, "PPV00000589")
    klik_radio_surveyjs(wait, "PPV00000595")
    klik_radio_surveyjs(wait, "PPV00000603")
    klik_kirim(wait)

def skrining_reproduksi_putri(wait):
    klik_input_by_label(wait, "Kesehatan Reproduksi Putri - Anak Sekolah")
    klik_radio_surveyjs(wait, "PPV00000565")
    klik_radio_surveyjs(wait, "PPV00000569")
    klik_radio_surveyjs(wait, "PPV00000571")
    klik_kirim(wait)

def skrining_tingkat_aktivitas_fisik(wait):
    klik_input_by_label(wait, "Kuesioner Tingkat Aktivitas Fisik - Tingkat Aktivitas Fisik")
    isi_input_surveyjs(wait, "sq_100i", "1")
    isi_input_surveyjs(wait, "sq_101i", "1")
    klik_kirim(wait)

def skrining_kebugaran(wait):
    klik_input_by_label(wait, "Kelayakan Tes Kebugaran")
    klik_radio_surveyjs(wait, "PPV00000609")
    klik_radio_surveyjs(wait, "PPV00000639")
    klik_radio_surveyjs(wait, "PPV00000644")
    klik_radio_surveyjs(wait, "PPV00000650")
    klik_kirim(wait)

def skrining_hati(wait):
    klik_input_by_label(wait, "Hati")
    klik_input_by_label(wait, "Faktor Risiko Hepatitis SMP dan SMA")
    klik_radio_surveyjs(wait, "PPV00000350")
    klik_radio_surveyjs(wait, "PPV00000352")
    klik_radio_surveyjs(wait, "PPV00000354")
    klik_radio_surveyjs(wait, "PPV00000356")
    klik_radio_surveyjs(wait, "PPV00000358")
    klik_radio_surveyjs(wait, "PPV00000360")
    klik_radio_surveyjs(wait, "PPV00000362")
    klik_radio_surveyjs(wait, "PPV00000449")
    klik_radio_surveyjs(wait, "PPV00000463")
    klik_kirim(wait)

def skrining_leher_rahim(wait):
    klik_input_by_label(wait, "Kanker Leher Rahim")
    klik_radio_surveyjs(wait, "PPV00000346")
    klik_kirim(wait)

def skrining_kesehatan_jiwa(wait):
    klik_input_by_label(wait, "Kesehatan Jiwa")
    klik_radio_surveyjs(wait, "PPV00000381")
    klik_radio_surveyjs(wait, "PPV00000382")
    klik_radio_surveyjs(wait, "PPV00000383")
    klik_radio_surveyjs(wait, "PPV00000384")
    klik_kirim(wait)

def skrining_kanker_paru(wait):
    klik_input_by_label(wait, "Penapisan Risiko Kanker Paru")
    klik_radio_surveyjs(wait, "PPV00001025")
    klik_radio_surveyjs(wait, "PPV00001027")
    klik_radio_surveyjs(wait, "PPV00001029")
    klik_radio_surveyjs(wait, "PPV00000737")
    klik_radio_surveyjs(wait, "PPV00001031")
    klik_radio_surveyjs(wait, "PPV00001033")
    klik_kirim(wait)

def skrining_merokok(wait):
    klik_input_by_label(wait, "Perilaku Merokok")
    klik_input_by_label(wait, "Perilaku Merokok - Anak Sekolah")
    klik_radio_surveyjs(wait, "PPV00000365")
    time.sleep(1)
    klik_radio_surveyjs(wait, "PPV00000426")
    klik_radio_surveyjs(wait, "PPV00000438")
    klik_kirim(wait)

def skrining_riwayat_imunisasi(wait):
    klik_input_by_label(wait, "Riwayat Imunisasi Tetanus(Status T) - Hanya untuk Catin")
    pilih_dropdown_surveyjs(wait, "sq_100i", "Tidak tahu atau tidak ingat")
    klik_kirim(wait)

def skrining_aktivitas_fisik(wait):
    klik_input_by_label(wait, "Tingkat Aktivitas Fisik (sedang dan berat)")
    pilih_dropdown_surveyjs(wait, "sq_100i", "Tidak")
    pilih_dropdown_surveyjs(wait, "sq_103i", "Tidak")
    pilih_dropdown_surveyjs(wait, "sq_106i", "Tidak")
    pilih_dropdown_surveyjs(wait, "sq_109i", "Tidak")
    pilih_dropdown_surveyjs(wait, "sq_112i", "Tidak")
    pilih_dropdown_surveyjs(wait, "sq_115i", "Tidak")
    klik_kirim(wait)

def proses_bb_tb_lp(wait, df, i):
    klik_input_by_row(wait, "rowfrm000051")
    klik_input_by_row(wait, "rowfrm000093")
    klik_input_by_row(wait, "rowfrm000119")
    isi_input_surveyjs(wait, "sq_100i", df.loc[i, "BB"])
    isi_input_surveyjs(wait, "sq_101i", df.loc[i, "TB"])
    isi_input_surveyjs(wait, "sq_102i", df.loc[i, "LP"])
    pilih_dropdown_surveyjs(wait, "sq_102i", "Gizi Baik")
    klik_kirim(wait)

def proses_gula_darah(wait, df, i):
    klik_input_by_row(wait, "rowfrm000256")
    klik_input_by_row(wait, "rowfrm000197")
    klik_radio_surveyjs(wait, "PPV00000328")
    klik_radio_surveyjs(wait, "PPV00001035")
    isi_input_surveyjs(wait, "//*[@id='sq_102i']", df.loc[i, "GDS"])
    klik_kirim(wait)

def proses_tekanan_darah(wait, df, i):
    klik_input_by_row(wait, "rowfrm000265")
    klik_input_by_row(wait, "rowfrm000266")
    klik_radio_surveyjs(wait, "PPV00000380")
    isi_input_surveyjs(wait, "//*[@id='sq_102i']", df.loc[i, "sistol"])
    isi_input_surveyjs(wait, "//*[@id='sq_103i']", df.loc[i, "diastol"])
    isi_input_surveyjs(wait, "//*[@id='sq_100i']", df.loc[i, "sistol"])
    isi_input_surveyjs(wait, "//*[@id='sq_101i']", df.loc[i, "diastol"])
    klik_kirim(wait)

#==============================
# PROSES SATU PASIEN
#==============================
def proses_pasien(wait, df, i):
    nama = str(df.loc[i, "nama"]).upper()
    log(f"\n===== PASIEN {i+1}/{len(df)} =====")
    log(f"👤 {nama}")

    if not cari_pasien(wait, nama):
        log(f"⛔ Gagal cari: {nama}")
        return "failed"

    if not pasien_ditemukan(wait):
        log(f"⛔ Tidak ditemukan: {nama}")
        return "not_found"

    if not klik_mulai(wait, nama):
        log(f"⛔ Gagal klik Mulai")
        return "failed"

    time.sleep(2)
    klik_tombol(wait, "Mulai Pemeriksaan")
    for attempt in range(3):
        if simple_click(wait, (By.XPATH, "//button[.//*[contains(normalize-space(), 'Simpan')]]"),
                       "Simpan"):
            break
        time.sleep(2)
    time.sleep(2)

    # SKRINING
    skrining_demografi(wait)
    skrining_kanker_usus(wait)
    skrining_malaria(wait)
    skrining_tb(wait)
    skrining_cemas_remaja(wait)
    skrining_depresi_remaja(wait)
    skrining_reproduksi_putra(wait)
    skrining_reproduksi_putri(wait)
    skrining_tingkat_aktivitas_fisik(wait)
    skrining_kebugaran(wait)
    skrining_hati(wait)
    skrining_leher_rahim(wait)
    skrining_kesehatan_jiwa(wait)
    skrining_kanker_paru(wait)
    skrining_merokok(wait)
    skrining_riwayat_imunisasi(wait)
    skrining_aktivitas_fisik(wait)

    # INPUT DATA
    proses_bb_tb_lp(wait, df, i)
    proses_gula_darah(wait, df, i)
    proses_tekanan_darah(wait, df, i)

    # SELESAI
    time.sleep(2)
    # Retry hanya untuk Selesaikan & Konfirmasi
    for attempt in range(3):
        if simple_click(wait, (By.XPATH, "//button[.//*[contains(normalize-space(), 'Selesaikan Layanan')]]"),
                       "Selesaikan Layanan"):
            break
        time.sleep(2)
    time.sleep(2)
    for attempt in range(3):
        if simple_click(wait, (By.XPATH, "//button[.//*[contains(normalize-space(), 'Konfirmasi')]]"),
                       "Konfirmasi"):
            break
        time.sleep(2)
    time.sleep(3)
    klik_back(wait)

    log(f"✅ Selesai: {nama}")
    return "success"

#==============================
# MAIN
#==============================
def main():
    driver, wait = init_browser()
    driver.get(WEBSITE_URL)
    cek_session(driver, wait)

    # CKG UMUM
    try:
        ckg_locator = (By.XPATH, "//button[contains(., 'CKG Umum')]")
        ckg_umum_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(ckg_locator)
        )
        js_click(wait, ckg_umum_btn, "CKG Umum")
    except Exception as e:
        log(f"⚠️ CKG Umum: {e}")

    # MENU PELAYANAN
    try:
        menu_pelayanan = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='menu_pelayanan']/div"))
        )
        js_click(wait, menu_pelayanan, "Menu Pelayanan")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table//tr"))
        )
    except Exception as e:
        log(f"❌ Menu Pelayanan: {e}")
        driver.quit()
        return

    # CHECKBOX
    centang_lokasi_sama(wait)
    klik_tombol(wait, "Simpan")

    # LOAD DATA
    df = pd.read_excel(EXCEL_FILE, sheet_name="data")
    required_cols = ["nama", "BB", "TB", "LP", "GDS", "sistol", "diastol"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        log(f"❌ Kolom missing: {missing}")
        driver.quit()
        return

    start_index = load_progress()
    if start_index > 0:
        log(f"📂 Resume dari index {start_index}")

    stats = {"total": len(df), "sukses": 0, "gagal": 0, "not_found": 0}

    for i in range(start_index, len(df)):
        result = proses_pasien(wait, df, i)
        if result == "success":
            stats["sukses"] += 1
        elif result == "not_found":
            stats["not_found"] += 1
        else:
            stats["gagal"] += 1

        save_progress(i + 1)

        if result != "success":
            try:
                klik_back(wait)
            except:
                pass

    log("\n===== HASIL =====")
    log(f"Total     : {stats['total']}")
    log(f"Sukses    : {stats['sukses']}")
    log(f"Gagal     : {stats['gagal']}")
    log(f"Not found : {stats['not_found']}")

    log("\n✅ Bot selesai!")
    driver.quit()

if __name__ == "__main__":
    main()
