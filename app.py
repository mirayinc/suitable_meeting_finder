#Bu kod 4 sayfadan oluşan bir Streamlit uygulaması
#Özellikle benim ve yakın arkadaş çevremin kullanacağı şekilde oluşturdum.

import streamlit as st
import datetime
from collections import Counter
import pandas as pd
import altair as alt  # Altair ile pie chart

# Önemli parametreleri belirledim
# Buradaki mekanlar listesine ekleme-çıkarma yapabilirsiniz
baslangic_saati = 10
bitis_saati = 22  # Bizim en sık buluştuğumuz aralık 10-22 arası olduğu için bu şekilde belirledim
mekanlar = ["Fark Etmez", "Kampüs", "Tunalı", "Bahçeli"] 

# strftime("%A") İngilizce gün adlarını dönderiyor
# Gün adlarını Türkçeye çevirmek için
tr_gun_ad = {
    "Monday": "Pazartesi",
    "Tuesday": "Salı",
    "Wednesday": "Çarşamba",
    "Thursday": "Perşembe",
    "Friday": "Cuma",
    "Saturday": "Cumartesi",
    "Sunday": "Pazar"
}

st.set_page_config(
    page_title="Ortak Buluşma Planlayıcı", 
    layout="centered",
    initial_sidebar_state="expanded"
)

toplam_asama = 4
if "step" not in st.session_state:
    st.session_state["step"] = 1

if "kisi_sayisi" not in st.session_state:
    st.session_state["kisi_sayisi"] = 2
if "bulusma_suresi" not in st.session_state:
    st.session_state["bulusma_suresi"] = 2

if "uygunluklar" not in st.session_state:
    st.session_state["uygunluklar"] = {}
    # 2.sayfadaki gün ve saat seçimlerini sakladığımız sözlük.
if "mekan_secimleri" not in st.session_state:
    st.session_state["mekan_secimleri"] = {}
    # 3.sayfada mekan tercihlerini sakladığımız sözlük.

#planlanacak gün sayısını kullanıcı seçsin istedim
if "dynamic_gun_sayisi" not in st.session_state:
    st.session_state["dynamic_gun_sayisi"] = 2  # varsayılan 2

def ileri():
    """
    ileri(): Bir sonraki adıma (sayfaya) geçer. step değerini 1 artırır.
    """
    if st.session_state["step"] < toplam_asama:
        st.session_state["step"] += 1

def geri():
    """
    geri(): Önceki sayfaya döner. step değerini 1 azaltır
    """
    if st.session_state["step"] > 1:
        st.session_state["step"] -= 1

def sayfa_basligi_ve_progress(adim):
    st.title("Ortak Buluşma Planlayıcı")
    ilerleme_orani = adim / toplam_asama
    st.progress(ilerleme_orani)

def zaman_dilimleri(bulusma_suresi):
    """
    10:00 - 22:00 arası, bulusma_suresi saat aralıkları oluşturur 
    (ör. 2 saat → 10.00-12.00, 12.00-14.00, ...).
    """
    dilimler = []
    for baslangic in range(baslangic_saati, bitis_saati, bulusma_suresi):
        bitis = baslangic + bulusma_suresi
        dilimler.append(f"{baslangic:02d}.00-{bitis:02d}.00")
    return dilimler

def sayfa_1():
    sayfa_basligi_ve_progress(1)
    st.header("1) Kaç kişinin buluşacağını ve buluşma süresini belirleyiniz.")

    st.session_state["kisi_sayisi"] = st.number_input(
        "Kişi sayısı:", min_value=2, max_value=7, step=1
    )
    st.session_state["bulusma_suresi"] = st.selectbox(
        "Buluşma süresi (saat):", [2, 3, 4, 6]
    )
    st.session_state["dynamic_gun_sayisi"] = st.selectbox(
        "Kaç gün içinde plan yapmak istersiniz?", [2, 3, 4],
        index=0
    )
    
    st.button("Sonraki Sayfa", on_click=ileri)


def sayfa_2():
    sayfa_basligi_ve_progress(2)
    st.header("2) Herkes uygun olduğu zaman dilimlerini işaretlesin.")

    kisi_sayisi = st.session_state["kisi_sayisi"]
    bulusma_suresi = st.session_state["bulusma_suresi"]
    bloklar = zaman_dilimleri(bulusma_suresi)

    gun_sayisi_local = st.session_state["dynamic_gun_sayisi"]

    gun_listesi = []
    for i in range(gun_sayisi_local):
        gun = datetime.date.today() + datetime.timedelta(days=i)
        gun_en = gun.strftime("%A")
        gun_tr = tr_gun_ad.get(gun_en, gun_en)
        tarih_str = gun.strftime("%d.%m.%Y")
        gun_listesi.append((tarih_str, gun_tr, gun)) 
    for i in range(1, kisi_sayisi + 1):
        st.subheader(f"{i}. Kişi")
        secimler = []
        for (tarih_str, gun_tr, gun_date) in gun_listesi:
            st.write(f"**{tarih_str} {gun_tr}**")
            
            for blok in bloklar:
                bas_saat_str = blok.split("-")[0].split(".")[0]  # "10.00" -> "10"
                bas_saat_int = int(bas_saat_str)

                now = datetime.datetime.now()
                if gun_date == now.date():
                    current_hour = now.hour
                    if bas_saat_int < current_hour:
                        #bu saat aralığını göstermiyoruz
                        continue

                check_key = f"check_kisi_{i}_{tarih_str}_{gun_tr}_{blok}"
                is_checked = st.checkbox(
                    f"{blok}",
                    value=False,
                    key=check_key
                )
                if is_checked:
                    secimler.append((tarih_str, gun_tr, blok))

        st.session_state["uygunluklar"][f"Kişi {i}"] = secimler

    col1, col2 = st.columns(2)
    with col1:
        st.button("Önceki Sayfa", on_click=geri)
    with col2:
        st.button("Sonraki Sayfa", on_click=ileri)

def sayfa_3():
    sayfa_basligi_ve_progress(3)
    st.header("3) Herkes hangi zaman dilimi için neresi müsaitse seçsin")
    st.info("Eğer mekan seçmezseniz, herhangi bi mekana okay olduğunuz kabul edilecektir.")

    kisi_sayisi = st.session_state["kisi_sayisi"]
    uygunluklar = st.session_state["uygunluklar"]

    for i in range(1, kisi_sayisi + 1):
        st.subheader(f"{i}. Kişi Mekan Tercihleri")

        secilen_zamanlar = uygunluklar.get(f"Kişi {i}", [])
        kisi_mekan_dict = st.session_state["mekan_secimleri"].get(f"Kişi {i}", {})

        for (tarih_str, gun_str, saat_blok) in secilen_zamanlar:
            st.write(f"{tarih_str} {gun_str} - {saat_blok}")

            mekan_secimleri = []
            mekan_listesi = [m for m in mekanlar if m != "Fark Etmez"]

            for mekan in mekan_listesi:
                cb_key = f"mekan_cb_{i}_{tarih_str}_{gun_str}_{saat_blok}_{mekan}"
                checked = st.checkbox(mekan, key=cb_key, value=False)
                if checked:
                    mekan_secimleri.append(mekan)

            if not mekan_secimleri:
                mekan_secimleri.append("Fark Etmez")

            kisi_mekan_dict[(tarih_str, gun_str, saat_blok)] = mekan_secimleri

        st.session_state["mekan_secimleri"][f"Kişi {i}"] = kisi_mekan_dict

    col1, col2 = st.columns(2)
    with col1:
        st.button("Önceki Sayfa", on_click=geri)
    with col2:
        st.button("Sonraki Sayfa", on_click=ileri)

def sayfa_4():
    sayfa_basligi_ve_progress(4)
    st.header("Ne zaman ve nerede buluşabiliriz?")

    uygunluklar = st.session_state["uygunluklar"]
    mekan_data = st.session_state["mekan_secimleri"]

    zaman_counter = Counter()

    for kisi_key, zamanlar in uygunluklar.items():
        for z in zamanlar:
            zaman_counter[z] += 1

    if not zaman_counter:
        st.write("Hiç kimse uygun zaman seçmedi.")
        return

    sirali = zaman_counter.most_common()
    max_deger = sirali[0][1]
    en_cok_uylananlar = [(k, v) for (k, v) in sirali if v == max_deger]

    for ((tarih_str, gun_str, blok), kisi_sayisi) in en_cok_uylananlar:
        mekan_counter = Counter()
        for kisi_key, k_dict in mekan_data.items():
            for (zaman_tuple), mekan_listesi in k_dict.items():
                if zaman_tuple == (tarih_str, gun_str, blok):
                    for m in mekan_listesi:
                        mekan_counter[m] += 1
                        
        st.markdown(f"### {tarih_str} {gun_str} Günü \n### {blok} saatleri arasında {kisi_sayisi} kişi uygun.")
        st.markdown("<br>", unsafe_allow_html=True)

        if mekan_counter:
            df = pd.DataFrame(list(mekan_counter.items()), columns=["Mekan", "SecimSayisi"])
            #görselleştirmek de istedim.
            chart = alt.Chart(df).mark_arc().encode(
                theta="SecimSayisi",
                color="Mekan",
                tooltip=["Mekan", "SecimSayisi"]
            ).properties(width=400, height=300)

            st.altair_chart(chart, use_container_width=True)

            mekan_text = [f"{adet} kişi '{mekan_adi}'" for (mekan_adi, adet) in mekan_counter.items()]
            mekan_text_str = ", ".join(mekan_text)
            st.write(f"{mekan_text_str} seçti.")
        else:
            st.write("Henüz mekan seçilmedi.")

        #ekstra boşluk için
        st.markdown("<br>", unsafe_allow_html=True)

    st.info("İsterseniz geri butonuyla değişiklik yapabilirsiniz.")
    st.button("Önceki Sayfa", on_click=geri)

def run_app():
    with st.sidebar:
        st.markdown("### Adımlar")
        step_names = {
            1: "1) Kişi ve Süre",
            2: "2) Zaman Seçimi",
            3: "3) Mekan Seçimi",
            4: "4) Sonuç Ekranı",
        }
        for s in range(1, toplam_asama + 1):
            if s == st.session_state["step"]:
                st.markdown(f"**➡️ {step_names[s]}**")
            else:
                st.markdown(step_names[s])
    if st.session_state["step"] == 1:
        sayfa_1()
    elif st.session_state["step"] == 2:
        sayfa_2()
    elif st.session_state["step"] == 3:
        sayfa_3()
    elif st.session_state["step"] == 4:
        sayfa_4()

run_app()
