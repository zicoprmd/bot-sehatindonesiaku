from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
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
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'CKG Umum')]")
        )
    )
    ckg_umum_btn.click()
    print("✅ CKG Umum diklik")
except:
    print("ℹ️ CKG Umum tidak muncul / sudah aktif")

menu_pendaftaran = wait.until(
    EC.element_to_be_clickable(
        (By.ID, "menu_cari/daftarkan_individu")
    )
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
    field = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "nik"))
    )

    field.clear()
    field.send_keys(str(nik))

    print("✅ NIK diisi")

def isi_nama(nama):
    field = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Masukkan nama lengkap']"))
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
                "[.//div[contains(text(),'Pilih tanggal lahir')]]"
            )
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", field
    )

    field.click()

    print("📅 Datepicker dibuka")

def pilih_tanggal_otomatis(tanggal_str):

    target = datetime.strptime(tanggal_str, "%Y-%m-%d")
    target_year = target.year
    target_month = target.month

    buka_datepicker_tgl_lahir()

    bulan_map = {
        "Jan":1, "Feb":2, "Mar":3, "Apr":4,
        "May":5, "Jun":6, "Jul":7, "Aug":8,
        "Sep":9, "Oct":10, "Nov":11, "Dec":12
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
                    By.CSS_SELECTOR,
                    "button.mx-btn-icon-double-left"
                ).click()
            else:
                driver.find_element(
                    By.CSS_SELECTOR,
                    "button.mx-btn-icon-double-right"
                ).click()

            time.sleep(0.2)
            continue

        # jika tahun sudah cocok tapi bulan belum
        if current_month != target_month:
            if current_month > target_month:
                driver.find_element(
                    By.CSS_SELECTOR,
                    "button.mx-btn-icon-left"
                ).click()
            else:
                driver.find_element(
                    By.CSS_SELECTOR,
                    "button.mx-btn-icon-right"
                ).click()

            time.sleep(0.2)
            continue

        # jika tahun & bulan sudah cocok
        break

    # klik tanggal
    tanggal_element = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//td[@title='{tanggal_str}']")
        )
    )

    tanggal_element.click()

    print(f"✅ Tanggal dipilih: {tanggal_str}")


def pilih_jenis_kelamin(jenis):

    dropdown = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//div[contains(text(),'Jenis Kelamin')]/following::div[contains(@class,'font-medium')][1]"
            )
        )
    )

    ActionChains(driver)\
        .move_to_element(dropdown)\
        .pause(0.2)\
        .click()\
        .perform()

    print("🔽 Dropdown jenis kelamin dibuka (real click)")

    # Tunggu popup benar-benar muncul
    option = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//div[contains(@class,'absolute')]//div[normalize-space()='{jenis}']"
            )
        )
    )

    ActionChains(driver)\
        .move_to_element(option)\
        .pause(0.2)\
        .click()\
        .perform()

    print(f"✅ Jenis kelamin dipilih: {jenis}")

def isi_nomor_whatsapp(no_whatsapp):
    field = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Masukkan nomor whatsapp']"))
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
                "//div[contains(text(),'Pekerjaan')]/following::div[contains(@class,'cursor-pointer')][1]"
            )
        )
    )

    ActionChains(driver)\
        .move_to_element(field)\
        .pause(0.2)\
        .click()\
        .perform()

    print("📂 Dropdown pekerjaan dibuka")
    time.sleep(2)
    # 2️⃣ Tunggu modal muncul dan klik berdasarkan text
    option = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//div[normalize-space()='{nama_pekerjaan}']")
        )
    )

    ActionChains(driver)\
        .move_to_element(option)\
        .pause(0.2)\
        .click()\
        .perform()

    print(f"✅ Pekerjaan dipilih: {nama_pekerjaan}")







isi_nik(nik)
isi_nama(nama)
pilih_tanggal_otomatis(tanggal_str)
pilih_jenis_kelamin(jenis)
isi_nomor_whatsapp(no_whatsapp)
pilih_pekerjaan(nama_pekerjaan)



#=====================berenti dulu
input("berenti dulu disini")








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




# ==============================
# PAUSE BIAR BROWSER TIDAK NUTUP
# ==============================
input(
    "\nBrowser siap.\n"
    "Session aktif.\n"
    "Tekan ENTER untuk lanjut ke step berikutnya (radio / form)..."
)
