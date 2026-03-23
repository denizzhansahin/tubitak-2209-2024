import os
import glob
import shutil

# --- BU ALANLARI KENDİ BİLGİLERİNİZE GÖRE DÜZENLEYİN ---

# Veri setinizin bulunduğu ana klasör. 
# TÜM resim (.jpg, .png vb.) ve etiket (.txt) dosyaları bu klasörde olmalıdır.
dataset_base_path = r"/Users/denizhan/Desktop/MakeleProjesi/zaman_damgali_frameler/Grup_1"

# Sınıf isimlerinin bulunduğu .txt dosyasının yolu
# Bu dosya da ana veri seti klasöründe olabilir veya farklı bir yerde.
classes_file_path = r"/Users/denizhan/Desktop/MakeleProjesi/zaman_damgali_frameler/class.txt"

# SAKLAMAK İSTEDİĞİNİZ ETİKETLERİN LİSTESİ
# classes.txt dosyanızdaki isimlerle birebir aynı olmalı.
etiketleri_sakla = ["atesli_silah", "kesici_alet", "kilic", "patlayici"]

# İstenmeyen verilerin taşınacağı YENİ klasörün adı
# Bu klasör, 'dataset_base_path' içinde oluşturulacaktır.
hedef_klasor_adi = "istenmeyen_veriler"

# --- KODUN GERİ KALANINI DEĞİŞTİRMENİZE GEREK YOK ---

def sinif_isimlerini_oku(dosya_yolu):
    """Sınıf dosyasını okur ve sınıf isimlerinin bir listesini döndürür."""
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"HATA: Sınıf dosyası bulunamadı! Yol: {dosya_yolu}")
        return None

def filtrele_ve_tasi():
    """Veri setini, istenen etiketlere göre ayıklar ve istenmeyenleri taşır."""
    
    source_path = dataset_base_path

    if not os.path.isdir(source_path):
        print(f"HATA: '{source_path}' klasörü bulunamadı. Lütfen yolu kontrol edin.")
        return

    # Hedef (istenmeyen veriler) klasör yollarını oluştur
    # Taşınan verilerin düzenli olması için burada alt klasörler oluşturulur.
    target_base_path = os.path.join(dataset_base_path, hedef_klasor_adi)
    target_labels_path = os.path.join(target_base_path, "labels")
    target_images_path = os.path.join(target_base_path, "images")

    os.makedirs(target_labels_path, exist_ok=True)
    os.makedirs(target_images_path, exist_ok=True)
    print(f"İstenmeyen veriler '{target_base_path}' klasörüne taşınacak.")

    all_classes = sinif_isimlerini_oku(classes_file_path)
    if not all_classes: return

    try:
        saklanacak_indeksler = {all_classes.index(isim) for isim in etiketleri_sakla}
    except ValueError as e:
        print(f"HATA: 'etiketleri_sakla' listesindeki bir etiket ('{e.args[0].split(' is not in list')[0]}') sınıf dosyasında bulunamadı.")
        return

    print(f"Saklanacak etiketler: {', '.join(etiketleri_sakla)}")
    print("-------------------------------------------")
    
    tasinan_dosya_sayisi = 0
    degistirilen_dosya_sayisi = 0
    
    # Desteklenen resim uzantıları
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    # Tüm dosyaları tara
    for filename in os.listdir(source_path):
        # Sadece etiket dosyalarını (.txt) işle, sınıf dosyasını atla
        if not filename.endswith(".txt") or filename == os.path.basename(classes_file_path):
            continue

        label_filepath_source = os.path.join(source_path, filename)
        
        with open(label_filepath_source, 'r') as f:
            lines = f.readlines()

        saklanacak_satirlar = []
        for line in lines:
            try:
                class_index = int(line.split()[0])
                if class_index in saklanacak_indeksler:
                    saklanacak_satirlar.append(line)
            except (ValueError, IndexError):
                continue
        
        # Durum 1: Dosyada saklanacak etiket yoksa, dosyayı ve resmi TAŞI
        if not saklanacak_satirlar and lines: # Boş etiket dosyalarını taşıma
            # Etiket dosyasını taşı
            try:
                shutil.move(label_filepath_source, os.path.join(target_labels_path, filename))
            except FileNotFoundError:
                continue # Başka bir işlem tarafından zaten taşınmış olabilir, devam et
            
            # İlgili resmi bul ve taşı
            base_name = os.path.splitext(filename)[0]
            potential_files = glob.glob(os.path.join(source_path, base_name + '.*'))
            image_moved = False
            for file_path in potential_files:
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in image_extensions:
                    shutil.move(file_path, os.path.join(target_images_path, os.path.basename(file_path)))
                    print(f"TAŞINDI: {filename} ve {os.path.basename(file_path)}")
                    image_moved = True
            
            if image_moved:
                tasinan_dosya_sayisi += 1

        # Durum 2: Dosya içeriği değiştiyse (istenmeyen etiketler çıkarıldıysa) dosyayı GÜNCELLE
        elif len(saklanacak_satirlar) < len(lines):
            with open(label_filepath_source, 'w') as f:
                f.writelines(saklanacak_satirlar)
            print(f"DEĞİŞTİRİLDİ: {filename} (istenmeyen etiketler temizlendi)")
            degistirilen_dosya_sayisi += 1

    print("\n--- İşlem Tamamlandı ---")
    print(f"İncelenen etiket dosyası sayısı yaklaşık olarak: {len([f for f in os.listdir(source_path) if f.endswith('.txt')])}")
    print(f"'{hedef_klasor_adi}' klasörüne taşınan resim/etiket çifti: {tasinan_dosya_sayisi}")
    print(f"İçeriği güncellenerek korunan etiket dosyası: {degistirilen_dosya_sayisi}")
    print("--------------------------")


if __name__ == "__main__":
    filtrele_ve_tasi()