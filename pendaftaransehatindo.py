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

# menu_daftarkan = wait.until(
#     EC.element_to_be_clickable(
#         (By.XPATH, "//*[@id='menu_cari/daftarkan_individu']/div")
#     )
# )
# menu_daftarkan.click()

time.sleep(1)
menu_pelayanan = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//*[@id='menu_pelayanan']/div")
    )
)
menu_pelayanan.click()


time.sleep(3)
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
    print("ℹ️ simpan tidak muncul / sudah aktif")

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

klik_inputdata_jika_ada("Tingkat Aktivitas Fisik (sedang dan berat)")

time.sleep(1)
def pilih_dropdown_surveyjs_by_text(question_id, option_text):

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




# ==============================
# PAUSE BIAR BROWSER TIDAK NUTUP
# ==============================
input(
    "\nBrowser siap.\n"
    "Session aktif.\n"
    "Tekan ENTER untuk lanjut ke step berikutnya (radio / form)..."
)
