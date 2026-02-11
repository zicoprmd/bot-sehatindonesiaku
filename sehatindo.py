from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
from selenium.webdriver.common.keys import Keys
import time 
from selenium.webdriver.common.action_chains import ActionChains

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
wait = WebDriverWait(driver, 1000)

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
    print("✅ Session aktif, langsung dashboard")
############CKGUMUM
try:
    ckg_umum_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'CKG Umum')]")
        )
    )
    ckg_umum_btn.click()
    print("✅ CKG Umum diklik")
except:
    print("ℹ️ CKG Umum tidak muncul / sudah aktif")
############MENU PELAYANAN
menu_pelayanan = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//*[@id='menu_pelayanan']/div")
    )
)
menu_pelayanan.click()
time.sleep(2)

##############clik simpan
try:
    simpan_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Simpan')]")
        )
    )
    simpan_btn.click()
    print("✅ simpan diklik")
except:
    print("ℹ️ simpan tidak muncul / sudah aktif")


# ===== BACA EXCEL =====
df = pd.read_excel("datasehat.xlsx", sheet_name="data")

# ===== AMBIL BARIS PERTAMA DULU (TEST) =====
i = 0
nama = str(df.loc[i, "nama"]).upper()

print("NAMA dari Excel:", nama)

# ===== TUNGGU INPUT MUNCUL =====
wait = WebDriverWait(driver, 1000)

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

    print(f"🔎 Mencari pasien: {nama}")

    # Tunggu tabel hasil muncul
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, "//table")
        )
    )

#==================MULAI BERDASARKAN NAMA SETELAH SEARCH
def klik_mulai_berdasarkan_nama(nama):
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//tr[.//td[normalize-space()='{nama}']]"
                    f"//button[.//div[normalize-space()='Mulai']]"
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

        print(f"✅ Tombol Mulai diklik untuk {nama}")
        return True

    except Exception as e:
        print(f"❌ Gagal klik Mulai untuk {nama}")
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

        print(f"✅ Tombol '{teks_tombol}' diklik")

        return True

    except:
        print(f"ℹ️ Tombol '{teks_tombol}' tidak muncul / sudah dilewati")
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
        print(f"✅ Input Data '{nama_layanan}' diklik")

        return True

    except:
        print(f"ℹ️ Tombol '{nama_layanan}' tidak muncul / sudah dilewati")
        return False

#FUNGSI NAMA LAYANAN
def klik_input_data(nama_layanan):
    btn = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                f"//tr[.//td[contains(., '{nama_layanan}')]]//button[contains(., 'Input Data')]"
            )
        )
    )
    btn.click()
    print(f"✅ Input Data '{nama_layanan}' diklik")

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

        print(f"✅ {pertanyaan} → {jawaban}")

        return True
    except:
        print(f"ℹ️ Tombol '{pertanyaan}' tidak muncul / sudah dilewati")
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
        print("✅ Form dikirim")
        return True
    except:
        print("ℹ️ Tombol kirim tidak muncul / sudah dilewati")
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

        print(f"✅ Radio dengan value {value} sudah diklik")
        return True
    except:
        print(f"ℹ️ Tombol {value} tidak muncul / sudah dilewati")
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

#Faktor Risiko TB - Dewasa & Lansia
def skrining_risiko_TB():
    klik_inputdata_jika_ada("Faktor Risiko TB - Dewasa & Lansia")
    klik_radio_surveyjs_by_value("PPV00000883")
    klik_kirim()

#HATI
def skrining_hati():
    klik_inputdata_jika_ada("Hati")
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
#======================================dropdown



#===============dropdown untuk klik
def pilih_dropdown_surveyjs_by_text(question_id, option_text):
    try:
        # klik dropdown
        dropdown = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, question_id))
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", dropdown
        )
        dropdown.click()

        # tunggu list khusus dropdown ini muncul
        list_id = f"{question_id}_list"

        option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//ul[@id='{list_id}']//li[@role='option']"
                    f"[.//div[normalize-space()='{option_text}']]"
                )
            )
        )

        option.click()

        print(f"✅ Dropdown {question_id} dipilih: {option_text}")
        return True
    except:
        print(f"!ℹ️ Dropdown {question_id} tidak terpilih: {option_text}")
        return False


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

        print(f"✅ Input Data diklik ({row_id})")
        return True
    except:
        print(f"ℹ️ Input tidak bisa diisi ({row_id})")
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

        print(f"✅ Input (SurveyJS) diisi & committed: {nilai}")
        return True
    except:
        print(f"ℹ️ Input tidak bisa diisi")
        return False

#=============BB TB LP================
def proses_bb_tb_lp(df, i):
    try:
        klik_input_data_by_row("rowfrm000051") #perempuan
        klik_input_data_by_row("rowfrm000093") #laki-laki
        time.sleep(2)
        isi_input_text_surveyjs("//*[@id='sq_100i']", df.loc[i, "BB"])   # berat badan
        time.sleep(0.3)
        isi_input_text_surveyjs("//*[@id='sq_101i']", df.loc[i, "TB"])   # tinggi badan
        time.sleep(0.3)
        isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[i, "LP"])   # lingkar perut
        time.sleep(0.3)
        klik_kirim()
        time.sleep(3)
        print("✔ BB TB LP selesai")
    except Exception as e:
        print(f"❌ BB TB LP: {e}")

#=================GULA DARAH==================#
def proses_gula_darah(df, i):
    try:
        klik_input_data_by_row("rowfrm000256")
        klik_radio_surveyjs_by_value("PPV00000328")
        isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[i, "GDS"])
        klik_kirim()
        time.sleep(3)
        print("✔ gula darah selesai")
    except Exception as e:
        print(f"❌ gula darah: {e}")


#==============TEKANAN DARAH=============
def proses_tekanan_darah(df, i):
    try:
        klik_input_data_by_row("rowfrm000265")
        klik_radio_surveyjs_by_value("PPV00000380")
        isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[i, "sistol"])
        isi_input_text_surveyjs("//*[@id='sq_103i']", df.loc[i, "diastol"])
        klik_kirim()
        time.sleep(3)
        print("✔ Tekanan Darah selesai")
    except Exception as e:
        print(f"❌ Tekanan Darah gagal: {e}")


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

    print("🔙 Kembali ke daftar layanan")



#=================================LOOOOOOP
for i in range(len(df)):

    nama = df.loc[i, "nama"].upper()

    try:
        print(f"\n==== PROSES PASIEN: {nama} ====")

        cari_pasien(nama)
        
        if not klik_mulai_berdasarkan_nama(nama):
            print("⛔ Tidak bisa klik Mulai")
            continue

        klik_tombol_jika_ada("Mulai Pemeriksaan")
        time.sleep(1)

        ###########SKRINING
        skrining_demografi()
        skrining_kanker_usus()
        skrining_risiko_TB()
        skrining_hati()
        skrining_leher_rahim()
        skrining_kesehatan_jiwa()
        skrining_kanker_paru()
        skrining_perilaku_merokok()
        skrining_tingkat_aktivitas_fisik()
        ###########INPUT DATA
        proses_bb_tb_lp(df, i)
        proses_gula_darah(df, i)
        proses_tekanan_darah(df, i)

        klik_tombol_jika_ada("Selesaikan Layanan")
        klik_tombol_jika_ada("Konfirmasi")

        print(f"✅ Semua layanan selesai untuk {nama}")
        klik_back_ke_layanan()

    except Exception as e:
        print(f"❌ ERROR pada pasien {nama}: {e}")
        continue



# ==============================
# PAUSE BIAR BROWSER TIDAK NUTUP
# ==============================
input(
    "\nBrowser siap.\n"
    "Session aktif.\n"
    "Tekan ENTER untuk lanjut ke step berikutnya (radio / form)..."
    "KALAU MUNCUL INI SEBENERNYA TANDA UDAH SELESAI SI"
)
