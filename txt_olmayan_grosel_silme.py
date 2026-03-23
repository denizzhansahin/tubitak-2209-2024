import os

# --- BU ALANI KENDİ BİLGİLERİNİZE GÖRE DÜZENLEYİN ---

# Veri setinizin ana klasörü.
# Bu klasörün içinde 'images' ve 'labels' alt klasörleri bulunmalıdır.
# Örnek: r"C:\YOLO_Projesi\dataset"
dataset_base_path = r"/Users/denizhan/Desktop/MakeleProjesi/zaman_damgali_frameler/yeni1636-10ekim2025Grup_1"

# --- KODUN GERİ KALANINI DEĞİŞTİRMENİZE GEREK YOK ---

def etiketsiz_resimleri_temizle():
    """
    'images' klasöründe olup, 'labels' klasöründe karşılığı olmayan
    görsel dosyalarını bulur ve siler.
    """
    
    # images ve labels klasörlerinin tam yollarını oluştur
    images_path = os.path.join(dataset_base_path, "images")
    labels_path = os.path.join(dataset_base_path, "labels")

    # Klasörlerin var olup olmadığını kontrol et
    if not os.path.isdir(images_path) or not os.path.isdir(labels_path):
        print(f"HATA: '{dataset_base_path}' yolu içinde 'images' ve/veya 'labels' klasörleri bulunamadı.")
        print("Lütfen 'dataset_base_path' değişkenini doğru ayarladığınızdan emin olun.")
        return

    print("--- Etiketi Olmayan Resimleri Temizleme Aracı ---")
    
    # Kullanıcı onayı al
    onay = input(f"UYARI: '{images_path}' klasöründeki etiketsiz resimler kalıcı olarak silinecektir.\n"
                 "Bu işlem geri alınamaz. Devam etmeden önce yedek aldığınızdan emin olun.\n"
                 "Devam etmek için 'evet' yazın: ")
    if onay.lower() != 'evet':
        print("İşlem kullanıcı tarafından iptal edildi.")
        return

    # Etiket dosyalarının uzantısız isimlerini bir sete kaydet (daha hızlı arama için)
    try:
        label_files_basenames = {os.path.splitext(f)[0] for f in os.listdir(labels_path) if f.endswith('.txt')}
    except FileNotFoundError:
        print(f"HATA: Etiket klasörü bulunamadı: {labels_path}")
        return

    silinen_resim_sayisi = 0
    toplam_resim_sayisi = 0

    # Resim klasöründeki her bir dosyayı kontrol et
    try:
        image_files_list = os.listdir(images_path)
        toplam_resim_sayisi = len(image_files_list)
        for image_filename in image_files_list:
            # Resim dosyasının uzantısız ismini al
            image_basename = os.path.splitext(image_filename)[0]
            
            # Eğer resmin ismi, etiket isimleri setinde yoksa, bu "yetim" bir resimdir.
            if image_basename not in label_files_basenames:
                image_filepath = os.path.join(images_path, image_filename)
                try:
                    os.remove(image_filepath)
                    print(f"SİLİNDİ (etiket yok): {image_filename}")
                    silinen_resim_sayisi += 1
                except Exception as e:
                    print(f"HATA: '{image_filename}' silinirken bir sorun oluştu: {e}")
    except FileNotFoundError:
        print(f"HATA: Resim klasörü bulunamadı: {images_path}")
        return

    print("\n--- İşlem Tamamlandı ---")
    print(f"Toplam {toplam_resim_sayisi} resim dosyası incelendi.")
    if silinen_resim_sayisi == 0:
        print("Temizlenecek etiketsiz resim bulunamadı. Tüm resimlerin bir etiketi var.")
    else:
        print(f"Toplam {silinen_resim_sayisi} adet etiketsiz resim dosyası silindi.")
    print("--------------------------")


if __name__ == "__main__":
    etiketsiz_resimleri_temizle()