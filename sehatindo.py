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

if "login" in current_url:
    input(
        "\n🔐 Session habis.\n"
        "Silakan LOGIN MANUAL + CAPTCHA di Edge.\n\n"
        "Jika sudah masuk DASHBOARD, tekan ENTER di sini..."
    )
else:
    print("✅ Session aktif, langsung dashboard")

# ==============================
# HANDLE CHECKBOX VERIFY (JIKA ADA)
# ==============================
# try:
#     verify_checkbox = wait.until(
#         EC.presence_of_element_located((By.ID, "verify"))
#     )

#     if not verify_checkbox.is_selected():
#         driver.execute_script(
#             "document.getElementById('verify').click();"
#         )
#         print("✅ Checkbox verify dicentang")
#     else:
#         print("ℹ️ Checkbox verify sudah dicentang")

# except TimeoutException:
#     print("ℹ️ Tidak ada checkbox verify")

#clik ckg umum terus pelayanan
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

menu_pelayanan = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//*[@id='menu_pelayanan']/div")
    )
)
menu_pelayanan.click()
time.sleep(2)

#clik simpan
try:
    simpan_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Simpan')]")
        )
    )
    simpan_btn.click()
    print("✅ simpan diklik")
except:
    print("ℹ️ CKG Umum tidak muncul / sudah aktif")

# ===== BACA EXCEL =====
df = pd.read_excel("datasehat.xlsx", sheet_name="data")

# ===== AMBIL BARIS PERTAMA DULU (TEST) =====
ckg = 1
nama = str(df.loc[ckg, "nama"]).upper()

print("NAMA dari Excel:", nama)

# ===== TUNGGU INPUT MUNCUL =====
wait = WebDriverWait(driver, 1000)

input_nama = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//*[@id='searchNik']"))
)

# ===== ISI INPUT =====
input_nama.clear()
input_nama.send_keys(nama)

print("✅ NAMA berhasil diinput")
input_nama.send_keys(Keys.ENTER)

#mulaibutton
# mulai_btn = wait.until(
#     EC.element_to_be_clickable(
#         (By.XPATH, "//button[contains(., 'Mulai')]")
#     )
# )
# mulai_btn.click()

# print("✅ Tombol Mulai diklik")

#clik mulaipemeriksaan dipake nanti saja kalau sudah production
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

time.sleep(0.5)
klik_mulai_berdasarkan_nama(nama)

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

klik_tombol_jika_ada("Mulai Pemeriksaan")
time.sleep(1)


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

klik_inputdata_jika_ada("Demografi Dewasa Perempuan")
klik_inputdata_jika_ada("Demografi Lansia")
klik_inputdata_jika_ada("Demografi Dewasa Laki-Laki")

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

pilih_radio_demografi("Status Perkawinan", "Menikah")
pilih_radio_demografi("Apakah Anda sedang hamil", "Tidak")
pilih_radio_demografi("Apakah Anda penyandang disabilitas?", "Non disabilitas")

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

klik_kirim() #function klik kirim...

klik_inputdata_jika_ada("Faktor Risiko Kanker Usus")
pilih_radio_demografi("kanker kolorektal", "Tidak")

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
klik_radio_surveyjs_by_value("PPV00000538")
klik_kirim()

#Faktor Risiko TB - Dewasa & Lansia
klik_inputdata_jika_ada("Faktor Risiko TB - Dewasa & Lansia")
klik_radio_surveyjs_by_value("PPV00000883")
klik_kirim()

#HATI
klik_inputdata_jika_ada("Hati")
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
klik_inputdata_jika_ada("Kanker Leher Rahim")
klik_radio_surveyjs_by_value("PPV00000346")
klik_kirim()

#kesehatan jiwa
klik_inputdata_jika_ada("Kesehatan Jiwa")
klik_radio_surveyjs_by_value("PPV00000381")
klik_radio_surveyjs_by_value("PPV00000382")
klik_radio_surveyjs_by_value("PPV00000383")
klik_radio_surveyjs_by_value("PPV00000384")
klik_kirim()

#kanker paru
klik_inputdata_jika_ada("Penapisan Risiko Kanker Paru")
klik_radio_surveyjs_by_value("PPV00001025")
klik_radio_surveyjs_by_value("PPV00001027")
klik_radio_surveyjs_by_value("PPV00001029")
klik_radio_surveyjs_by_value("PPV00000737")
klik_radio_surveyjs_by_value("PPV00001031")
klik_radio_surveyjs_by_value("PPV00001033")
klik_kirim()


#perilaku merokok
klik_inputdata_jika_ada("Perilaku Merokok")
klik_radio_surveyjs_by_value("PPV00000365")
klik_radio_surveyjs_by_value("PPV00000426")
klik_radio_surveyjs_by_value("PPV00000438")
klik_kirim()



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

time.sleep(4)
klik_input_data_by_row("rowfrm000051")
time.sleep(2)

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


isi_input_text_surveyjs("//*[@id='sq_100i']", df.loc[ckg, "BB"])   # berat badan
time.sleep(0.3)
isi_input_text_surveyjs("//*[@id='sq_101i']", df.loc[ckg, "TB"])   # tinggi badan
time.sleep(0.3)
isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[ckg, "LP"])   # lingkar perut
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

klik_tombol_jika_ada("Selesaikan Layanan")
klik_tombol_jika_ada("Konfirmasi")

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

klik_back_ke_layanan()



# ==============================
# PAUSE BIAR BROWSER TIDAK NUTUP
# ==============================
input(
    "\nBrowser siap.\n"
    "Session aktif.\n"
    "Tekan ENTER untuk lanjut ke step berikutnya (radio / form)..."
)
