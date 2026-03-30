from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
from selenium.webdriver.common.keys import Keys
import time
import logging
from selenium.webdriver.common.action_chains import ActionChains

#==============================
# LOGGING FILE
#==============================
import logging

logging.basicConfig(
    filename="bot_sehatindo.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log(msg):
    print(msg)
    logging.info(msg)
#===============================

# ==============================
# KONFIGURASI EDGE PROFILE
# ==============================
edge_options = Options()
edge_options.add_argument(
    r"--user-data-dir=C:\Users\ThinkPad\AppData\Local\Microsoft\Edge\User Data"
)
edge_options.add_argument("--profile-directory=Default")

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
#=====================MASUK DASHBOARD
if "login" in current_url:
    input(
        "\n🔐 Session habis.\n"
        "Silakan LOGIN MANUAL + CAPTCHA di Edge.\n\n"
        "Jika sudah masuk DASHBOARD, tekan ENTER di sini..."
    )
else:
    log("✅ Session aktif, langsung dashboard")
############CKGUMUM
try:
    ckg_umum_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'CKG Umum')]")
        )
    )
    ckg_umum_btn.click()
    log("✅ CKG Umum diklik")
except:
    log("ℹ️ CKG Umum tidak muncul / sudah aktif")
############MENU PELAYANAN
menu_pelayanan = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//*[@id='menu_pelayanan']/div")
    )
)
menu_pelayanan.click()
time.sleep(8)

#############chekbox same location
def centang_lokasi_sama():

    checkbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH,
             "//div[contains(.,'Lokasi sama dengan puskesmas')]/preceding::div[contains(@class,'check')][1]")
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", checkbox
    )

    ActionChains(driver).move_to_element(checkbox).click().perform()

    log("✅ Checkbox 'Lokasi sama dengan puskesmas' dicentang")

centang_lokasi_sama()

##############clik simpan
try:
    simpan_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Simpan')]")
        )
    )
    simpan_btn.click()
    log("✅ simpan diklik")
except:
    log("ℹ️ simpan tidak muncul / sudah aktif")


# ===== BACA EXCEL =====
df = pd.read_excel("datasehat.xlsx", sheet_name="data")

# ===== AMBIL BARIS PERTAMA DULU (TEST) =====
i = 0
nama = str(df.loc[i, "nama"]).upper()



# ===== TUNGGU INPUT MUNCUL =====


def cari_pasien(nama):
    input_nama = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "searchNik"))
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", input_nama
    )

    input_nama.clear()
    input_nama.send_keys(str(nama))
    input_nama.send_keys(Keys.ENTER)

    log(f"🔎 Mencari pasien: {nama}")

    # Tunggu tabel hasil muncul
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, "//table")
        )
    )

def pasien_ditemukan():

    try:
        WebDriverWait(driver,5).until(
            EC.presence_of_element_located(
                (By.XPATH,"//table//tr")
            )
        )
        return True
    except:
        return False

#==================MULAI BERDASARKAN NAMA SETELAH SEARCH
def xpath_literal(s):
    if "'" not in s:
        return f"'{s}'"
    if '"' not in s:
        return f'"{s}"'
    return "concat('" + s.replace("'", "',\"'\",'") + "')"

def klik_mulai_berdasarkan_nama(nama):
    try:
        nama_xpath = xpath_literal(nama)

        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//table//tr[1]//button[.//div[normalize-space()='Mulai']]"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", btn
        )

        ActionChains(driver)\
            .move_to_element(btn)\
            .pause(0.2)\
            .click()\
            .perform()

        log(f"✅ Tombol Mulai diklik untuk {nama}")
        return True

    except Exception as e:
        log(f"❌ Gagal klik Mulai untuk {nama}")
        return False

def klik_tombol_jika_ada(teks_tombol):
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//button[.//text()[contains(., '{teks_tombol}')]]"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", btn
        )

        ActionChains(driver)\
            .move_to_element(btn)\
            .pause(0.2)\
            .click()\
            .perform()

        log(f"✅ Tombol '{teks_tombol}' diklik")

        return True

    except:
        log(f"ℹ️ Tombol '{teks_tombol}' tidak muncul / sudah dilewati")
        return False


#NAMALAYANAN SKRINING
def klik_inputdata_jika_ada(nama_layanan):
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//tr[.//td[contains(., '{nama_layanan}')]]//button[contains(., 'Input Data')]"
                )
            )
        )
        btn.click()
        log(f"✅ Input Data '{nama_layanan}' diklik")

        return True

    except:
        log(f"ℹ️ Tombol '{nama_layanan}' tidak muncul / sudah dilewati")
        return False


#demografiprempuan
def pilih_radio_demografi(pertanyaan, jawaban):
    try:
        radio = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//div[.//text()[contains(., '{pertanyaan}')]]"
                    f"//label[normalize-space()='{jawaban}']"
                )
            )
        )

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", radio)
        driver.execute_script("arguments[0].click();", radio)

        log(f"✅ {pertanyaan} → {jawaban}")

        return True
    except:
        log(f"ℹ️ Tombol '{pertanyaan}' tidak muncul / sudah dilewati")
        return False


#KIRIMBUTTON
def klik_kirim():
    try:
        kirim_btn = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='sv-nav-complete']//input[@type='button']")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", kirim_btn)
        driver.execute_script("arguments[0].click();", kirim_btn)
        log("✅ Form dikirim")
        return True
    except:
        log("ℹ️ Tombol kirim tidak muncul / sudah dilewati")
        return False


#RADIOSRUVEYJS
def klik_radio_surveyjs_by_value(value):
    try:
        label = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    f"//label[contains(@class,'sd-selectbase__label')][.//input[@value='{value}']]"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", label
        )

        ActionChains(driver)\
            .move_to_element(label)\
            .pause(0.2)\
            .click()\
            .perform()

        log(f"✅ Radio dengan value {value} sudah diklik")
        return True
    except:
        log(f"ℹ️ Tombol {value} tidak muncul / sudah dilewati")
        return False


#====================DEMOGRAFI
def skrining_demografi():
    klik_inputdata_jika_ada("Demografi Dewasa Perempuan")
    klik_inputdata_jika_ada("Demografi Lansia")
    klik_inputdata_jika_ada("Demografi Dewasa Laki-Laki")
    pilih_radio_demografi("Status Perkawinan", "Menikah")
    pilih_radio_demografi("Apakah Anda sedang hamil", "Tidak")
    pilih_radio_demografi("Apakah Anda penyandang disabilitas?", "Non disabilitas")
    klik_kirim() #function klik kirim...

####################kanker-usus
def skrining_kanker_usus():
    klik_inputdata_jika_ada("Faktor Risiko Kanker Usus")
    pilih_radio_demografi("kanker kolorektal", "Tidak")
    klik_radio_surveyjs_by_value("PPV00000538")
    klik_kirim()

#Faktor Risiko Malaria
def skrining_risiko_malaria():
    klik_inputdata_jika_ada("Faktor Risiko Malaria")
    klik_radio_surveyjs_by_value("PPV00000581")
    klik_radio_surveyjs_by_value("PPV00000591")
    klik_radio_surveyjs_by_value("PPV00000607")
    klik_radio_surveyjs_by_value("PPV00001233")
    klik_kirim()

#Faktor Risiko TB - Dewasa & Lansia
def skrining_risiko_TB():
    klik_inputdata_jika_ada("Faktor Risiko TB - Dewasa & Lansia")
    klik_radio_surveyjs_by_value("PPV00000883")
    klik_kirim()

#Gejala Cemas Remaja
def skrining_gejala_cemas_remaja():
    klik_inputdata_jika_ada("Gejala Cemas Remaja")
    klik_radio_surveyjs_by_value("PPV00000883")
    klik_kirim()

#HATI
def skrining_hati():
    klik_inputdata_jika_ada("Hati")
    klik_inputdata_jika_ada("Faktor Risiko Hepatitis SMP dan SMA")
    time.sleep(1)
    klik_radio_surveyjs_by_value("PPV00000350")
    klik_radio_surveyjs_by_value("PPV00000352")
    klik_radio_surveyjs_by_value("PPV00000354")
    klik_radio_surveyjs_by_value("PPV00000356")
    klik_radio_surveyjs_by_value("PPV00000358")
    klik_radio_surveyjs_by_value("PPV00000360")
    klik_radio_surveyjs_by_value("PPV00000362")
    klik_radio_surveyjs_by_value("PPV00000449")
    klik_radio_surveyjs_by_value("PPV00000463")
    klik_kirim()

#kanker leher rahim
def skrining_leher_rahim():
    klik_inputdata_jika_ada("Kanker Leher Rahim")
    klik_radio_surveyjs_by_value("PPV00000346")
    klik_kirim()

#kesehatan jiwa
def skrining_kesehatan_jiwa():
    klik_inputdata_jika_ada("Kesehatan Jiwa")
    klik_radio_surveyjs_by_value("PPV00000381")
    klik_radio_surveyjs_by_value("PPV00000382")
    klik_radio_surveyjs_by_value("PPV00000383")
    klik_radio_surveyjs_by_value("PPV00000384")
    klik_kirim()

#kanker paru
def skrining_kanker_paru():
    klik_inputdata_jika_ada("Penapisan Risiko Kanker Paru")
    klik_radio_surveyjs_by_value("PPV00001025")
    klik_radio_surveyjs_by_value("PPV00001027")
    klik_radio_surveyjs_by_value("PPV00001029")
    klik_radio_surveyjs_by_value("PPV00000737")
    klik_radio_surveyjs_by_value("PPV00001031")
    klik_radio_surveyjs_by_value("PPV00001033")
    klik_kirim()


#perilaku merokok
def skrining_perilaku_merokok():
    klik_inputdata_jika_ada("Perilaku Merokok")
    klik_radio_surveyjs_by_value("PPV00000365")
    klik_radio_surveyjs_by_value("PPV00000426")
    klik_radio_surveyjs_by_value("PPV00000438")
    klik_kirim()
#======================================dropdown SURVEY JS
def pilih_dropdown_surveyjs_by_text(question_id, option_text):
    try:
        # ===== tunggu dropdown clickable =====
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, question_id))
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", dropdown
        )
        time.sleep(0.3)

        # ===== klik pakai JS (lebih stabil) =====
        driver.execute_script("arguments[0].focus();", dropdown)
        driver.execute_script("arguments[0].click();", dropdown)

        list_id = f"{question_id}_list"

        # ===== tunggu dropdown aktif =====
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, list_id))
        )

        # ===== ambil option yang BENAR =====
        option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//ul[@id='{list_id}']//*[text()='{option_text}']/ancestor::*[self::li or self::div][1]"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", option
        )
        time.sleep(0.2)

        # ===== klik option =====
        try:
            option.click()
        except:
            driver.execute_script("arguments[0].click();", option)

        # ===== commit perubahan =====
        driver.execute_script("arguments[0].blur();", dropdown)

        log(f"✅ Dropdown {question_id} dipilih: {option_text}")
        return True

    except Exception as e:
        log(f"❌ Dropdown ERROR {question_id}: {e}")
        return False
#=====================================DROPDOWN BY LABEL
def pilih_dropdown_by_label(label_text, option_text):
    try:
        container = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[contains(., '{label_text}')]")
            )
        )

        dropdown = container.find_element(By.XPATH, ".//div[contains(@class,'sd-dropdown')]")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", dropdown)
        dropdown.click()

        option = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[contains(@class,'sd-item')]//span[text()='{option_text}']")
            )
        )

        option.click()

        log(f"✅ Dropdown '{label_text}' → {option_text}")
        return True
    except Exception as e:
        log(f"❌ Dropdown '{label_text}' gagal: {e}")
        return False



#===============dropdown untuk klik
# def pilih_dropdown_surveyjs_by_text(question_id, option_text):
#     try:
#         # ===== klik dropdown (pakai ActionChains) =====
#         dropdown = WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.ID, question_id))
#         )

#         driver.execute_script(
#             "arguments[0].scrollIntoView({block:'center'});", dropdown
#         )

#         ActionChains(driver)\
#             .move_to_element(dropdown)\
#             .pause(0.2)\
#             .click()\
#             .perform()

#         # ===== tunggu list muncul =====
#         list_id = f"{question_id}_list"

#         WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.ID, list_id))
#         )

#         # ===== ambil option =====
#         option = WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located(
#                 (
#                     By.XPATH,
#                     f"//ul[@id='{list_id}']//li[@role='option']"
#                     f"[.//div[normalize-space()='{option_text}']]"
#                 )
#             )
#         )

#         # ===== klik option (pakai ActionChains) =====
#         ActionChains(driver)\
#             .move_to_element(option)\
#             .pause(0.2)\
#             .click()\
#             .perform()

#         log(f"✅ Dropdown {question_id} dipilih: {option_text}")
#         return True

#     except Exception as e:
#         log(f"ℹ️ Dropdown {question_id} gagal: {option_text} | {e}")
#         return False


#=======================skrining aktifitas fisik
def skrining_tingkat_aktivitas_fisik():
    klik_inputdata_jika_ada("Tingkat Aktivitas Fisik (sedang dan berat)")
    time.sleep(0.5)
    pilih_dropdown_surveyjs_by_text("sq_100i", "Tidak")
    time.sleep(1)
    pilih_dropdown_surveyjs_by_text("sq_103i", "Tidak")
    time.sleep(1)
    pilih_dropdown_surveyjs_by_text("sq_106i", "Tidak")
    time.sleep(1)
    pilih_dropdown_surveyjs_by_text("sq_109i", "Tidak")
    time.sleep(1)
    pilih_dropdown_surveyjs_by_text("sq_112i", "Tidak")
    time.sleep(1)
    pilih_dropdown_surveyjs_by_text("sq_115i", "Tidak")
    klik_kirim()
    time.sleep(3)


#gizi BB-TB-LP
def klik_input_data_by_row(row_id):
    try :
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//div[@id='{row_id}']//button"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", btn
        )

        ActionChains(driver).move_to_element(btn).click().perform()

        log(f"✅ Input Data diklik ({row_id})")
        return True
    except:
        log(f"ℹ️ Input tidak bisa diisi ({row_id})")
        return False


#=================UNTUK INPUT TEXT=============
def normalize_number(val):
    return str(val).replace(",", ".")

def isi_input_text_surveyjs(xpath_input, nilai):
    try:
        nilai = normalize_number(nilai)

        field = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, xpath_input))
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", field
        )

        field.click()
        field.clear()
        field.send_keys(nilai)
        field.send_keys(Keys.TAB)   # 🔥 INI KUNCINYA

        log(f"✅ Input (SurveyJS) diisi & committed: {nilai}")
        return True
    except:
        log(f"ℹ️ Input tidak bisa diisi")
        return False

#=============BB TB LP================
def proses_bb_tb_lp(df, i):
    try:
        klik_input_data_by_row("rowfrm000051") #perempuan
        klik_input_data_by_row("rowfrm000093") #laki-laki
        klik_input_data_by_row("rowfrm000119") #gizi anak sekolah
        time.sleep(2)
        isi_input_text_surveyjs("//*[@id='sq_100i']", df.loc[i, "BB"])   # berat badan
        time.sleep(0.3)
        isi_input_text_surveyjs("//*[@id='sq_101i']", df.loc[i, "TB"])   # tinggi badan
        time.sleep(0.3)
        isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[i, "LP"])   # lingkar perut
        time.sleep(0.6)
        pilih_dropdown_surveyjs_by_text("sq_102i", "Obesitas")
        # pilih_dropdown_by_label("Pilih hasil IMT/U", "Gizi Buruk") GAGAL TIDAK BISA PAKAI LABEL
        time.sleep(1)
        klik_kirim()
        time.sleep(3)
        log("✔ BB TB LP selesai")
    except Exception as e:
        log(f"❌ BB TB LP: {e}")

#=================GULA DARAH==================#
def proses_gula_darah(df, i):
    try:
        klik_input_data_by_row("rowfrm000256") #dewasa
        klik_input_data_by_row("rowfrm000197") #remaja
        klik_radio_surveyjs_by_value("PPV00000328")
        klik_radio_surveyjs_by_value("PPV00001035") # ramaja
        isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[i, "GDS"])
        klik_kirim()
        time.sleep(3)
        log("✔ gula darah selesai")
    except Exception as e:
        log(f"❌ gula darah: {e}")


#==============TEKANAN DARAH=============
def proses_tekanan_darah(df, i):
    try:
        klik_input_data_by_row("rowfrm000265") #dewasa
        klik_input_data_by_row("rowfrm000266") #remaja
        klik_radio_surveyjs_by_value("PPV00000380")
        isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[i, "sistol"])
        isi_input_text_surveyjs("//*[@id='sq_103i']", df.loc[i, "diastol"])
        isi_input_text_surveyjs("//*[@id='sq_100i']", df.loc[i, "sistol"]) #remaja
        isi_input_text_surveyjs("//*[@id='sq_101i']", df.loc[i, "diastol"]) #remaja
        klik_kirim()
        time.sleep(3)
        log("✔ Tekanan Darah selesai")
    except Exception as e:
        log(f"❌ Tekanan Darah gagal: {e}")


#balik ke layanan untuk search nik
def klik_back_ke_layanan():
    back_img = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//img[contains(@class,'cursor-pointer') and contains(@src,'icon-arrow-left')]"
            )
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", back_img
    )

    ActionChains(driver)\
        .move_to_element(back_img)\
        .pause(0.2)\
        .click()\
        .perform()

    log("🔙 Kembali ke daftar layanan")
#KLIK SEDANG PEMERIKSAAN TAB
def klik_tab_sedang_pemeriksaan():
    try:
        tab = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(@class,'cursor-pointer') and normalize-space()='Sedang Pemeriksaan']"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", tab
        )

        ActionChains(driver)\
            .move_to_element(tab)\
            .pause(0.2)\
            .click()\
            .perform()

        # tunggu tabel reload
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//table//tr")
            )
        )

        print("📂 Tab 'Sedang Pemeriksaan' aktif")
        return True

    except Exception as e:
        print("❌ Gagal klik tab Sedang Pemeriksaan:", e)
        return False

#KLIK SELESAI PEMERIKSAAN TAB
def klik_tab_selesai_pemeriksaan():
    try:
        tab = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(@class,'cursor-pointer') and normalize-space()='Selesai Pemeriksaan']"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", tab
        )

        ActionChains(driver)\
            .move_to_element(tab)\
            .pause(0.2)\
            .click()\
            .perform()

        # tunggu tabel reload
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//table//tr")
            )
        )

        print("📂 Tab 'Selesai Pemeriksaan' aktif")
        return True

    except Exception as e:
        print("❌ Gagal klik tab Selesai Pemeriksaan:", e)
        return False
#===============================statistik hasil run
stats = {
    "total": len(df),
    "sukses": 0,
    "gagal": 0,
    "pasien_tidak_ditemukan": 0
}

#=================================LOOOOOOP
for i in range(len(df)):

    nama = df.loc[i, "nama"].upper()

    log(f"\n===== PASIEN {i+1}/{len(df)} =====")
    log(f"👤 {nama}")

    try:

        klik_tab_sedang_pemeriksaan()
        cari_pasien(nama)
        time.sleep(1)

        if not pasien_ditemukan():
            log(f"⛔ Pasien tidak ditemukan: {nama}")
            stats["pasien_tidak_ditemukan"] += 1
            continue

        if not klik_mulai_berdasarkan_nama(nama):
            log("⛔ Tidak bisa klik Mulai")
            stats['gagal'] += 1
            continue

        klik_tombol_jika_ada("Mulai Pemeriksaan")
        time.sleep(1)

        # ======= SKRINING =======
        # skrining_demografi()
        # skrining_kanker_usus()
        # skrining_risiko_TB()
        # skrining_hati()
        # skrining_leher_rahim()
        # skrining_kesehatan_jiwa()
        # skrining_kanker_paru()
        # skrining_perilaku_merokok()
        # skrining_tingkat_aktivitas_fisik()
        # ======= INPUT DATA ======
        proses_bb_tb_lp(df, i)
        proses_gula_darah(df, i)
        proses_tekanan_darah(df, i)

        time.sleep(2)
        klik_tombol_jika_ada("Selesaikan Layanan")
        time.sleep(2)
        klik_tombol_jika_ada("Konfirmasi")
        time.sleep(2)

        klik_back_ke_layanan()

        stats["sukses"] += 1

        log("✅ Pasien selesai")

    except Exception as e:

        log(f"❌ ERROR pasien {nama}: {e}")
        stats["gagal"] += 1

        try:
            klik_back_ke_layanan()
        except:
            pass
# ==============================
log("\n===== HASIL BOT =====")

log(f"Total pasien : {stats['total']}")
log(f"Sukses       : {stats['sukses']}")
log(f"Gagal        : {stats['gagal']}")
log(f"Tidak ketemu : {stats['pasien_tidak_ditemukan']}")


# ==============================
# PAUSE BIAR BROWSER TIDAK NUTUP
# ==============================
input(
    "\nBrowser siap.\n"
    "Session aktif.\n"
    "Tekan ENTER untuk lanjut ke step berikutnya (radio / form)...\n"
    "KALAU MUNCUL INI SEBENERNYA TANDA UDAH SELESAI SI"
)
