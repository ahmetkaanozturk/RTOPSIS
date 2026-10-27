# R-CZ-TOPSIS İnternetsiz (Air-Gapped) ve Kurum İçi Dağıtım Kılavuzu

Bu kılavuz, R-CZ-TOPSIS karar destek platformunun internet bağlantısı bulunmayan izole askeri ağlara veya kurum içi yerel sunuculara (on-premise / air-gapped) güvenli kurulum ve sertifikasyon hazırlık adımlarını içerir.

---

## 1. Dağıtım İlkeleri

1. **Sıfır Dış Ağ Bağımlılığı (Zero External Dependencies):**
   Sistem çalışırken hiçbir CDN, harici telemetri, bulut API veya analitik servisi çağırmaz. Tüm hesaplamalar yerel CPU belleğinde gerçekleşir.
2. **Konteyner ve Bağımsız Çalışma:**
   Python 3.10+ ve NumPy/Pandas/Streamlit tabanlı standart taşınabilir ortamda çalışır.
3. **Deterministik Bağımlılık Kilidi:**
   Paketler `requirements.txt` üzerinden hash kontrollü kurulabilir.

---

## 2. Çevrimdışı (Offline) Paket Hazırlığı

İnternet erişimi olan güvenli bir derleme makinesinde paketler indirilir:

```bash
# 1. Tüm bağımlılıkları çevrimdışı tekerlek (wheel) klasörüne indirin:
pip wheel -r requirements.txt -w ./offline_packages

# 2. RTOPSIS proje klasörünü ve offline_packages klasörünü arşivleyin:
tar -czvf rtopsis_airgap_bundle.tar.gz RTOPSIS/ offline_packages/
```

---

## 3. İzole / Air-Gapped Hedef Makinede Kurulum

Arşiv izole ortama güvenli optik/veri aktarım prosedürleri (güvenli USB/CD) ile taşındıktan sonra:

```bash
# 1. Sanal ortam oluşturun:
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Çevrimdışı paketleri yerel klasörden yükleyin (internet olmadan):
pip install --no-index --find-links=./offline_packages -r requirements.txt

# 3. Paket bütünlüğünü doğrulayın:
python -m pip check
```

---

## 4. Güvenlik Sertleştirmesi (Hardening)

Kurumsal ağda veya çok kullanıcılı ortamda çalıştırılacaksa `.streamlit/config.toml` dosyası sertleştirilmelidir:

```toml
[server]
headless = true
port = 8501
address = "127.0.0.1"          # Yalnızca yerel loopback veya kurum güvenlik duvarı arkasındaki IP
enableCORS = true              # Üretimde CORS koruması aktif edilmelidir
enableXsrfProtection = true    # Üretimde XSRF koruması kesinlikle açık olmalıdır

[browser]
gatherUsageStats = false       # Telemetri veri gönderimini kapatır
```

---

## 5. Doğrulama ve Sağlık Testi (Verification Smoke Test)

Kurulum tamamlandıktan sonra izole ortamda sistemin matematiksel ve operasyonel doğruluğunu kanıtlamak için test paketi çalıştırılır:

```bash
python -m pytest test_invariants.py test_enterprise_profiles.py test_conformance.py test_smoke_scenarios.py -v
```

Beklenen çıktı: Tüm invariant, profil, conformance ve smoke senaryo testlerinin tam başarıyla (`PASSED`) sonuçlanmasıdır.

