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
ckg = 12
nama = str(df.loc[ckg, "nama"])

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
                    f"//tr[.//td[contains(., '{nama}')]]"
                    f"//button[.//text()[contains(., 'Mulai')]]"
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

#RADIOSRUVEYJS
def klik_radio_surveyjs_by_value(value):
    try:
        label = WebDriverWait(driver, 4).until(
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

#INPUTFORMMMMM
klik_input_data_by_row("rowfrm000051")

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
        field.send_keys(Keys.TAB)

        print(f"✅ Input (SurveyJS) diisi & committed: {nilai}")
        return True
    except:
        print(f"ℹ️ Input tidak bisa diisi")
        return False


isi_input_text_surveyjs("//*[@id='sq_100i']", df.loc[ckg, "BB"])   # berat badan
time.sleep(1)
isi_input_text_surveyjs("//*[@id='sq_101i']", df.loc[ckg, "TB"])   # tinggi badan
time.sleep(1)
isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[ckg, "LP"])   # lingkar perut
time.sleep(1)
klik_kirim()
time.sleep(2)

klik_input_data_by_row("rowfrm000256")
klik_radio_surveyjs_by_value("PPV00000328")
isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[ckg, "GDS"])
klik_kirim()
time.sleep(2)

klik_input_data_by_row("rowfrm000265")
klik_radio_surveyjs_by_value("PPV00000380")
isi_input_text_surveyjs("//*[@id='sq_102i']", df.loc[ckg, "sistol"])
isi_input_text_surveyjs("//*[@id='sq_103i']", df.loc[ckg, "diastol"])
klik_kirim()
time.sleep(2)




# ==============================
# PAUSE BIAR BROWSER TIDAK NUTUP
# ==============================
input(
    "\nBrowser siap.\n"
    "Session aktif.\n"
    "Tekan ENTER untuk lanjut ke step berikutnya (radio / form)..."
)
