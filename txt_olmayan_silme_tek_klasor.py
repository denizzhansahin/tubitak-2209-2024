import os

# --- BU ALANI KENDİ BİLGİLERİNİZE GÖRE DÜZENLEYİN ---

# Veri setinizin bulunduğu ana klasör.
# Tüm resim (.jpg, .png vb.) ve etiket (.txt) dosyaları bu klasörde olmalıdır.
# Örnek: r"C:\YOLO_Projesi\dataset"
dataset_base_path = r"/Users/denizhan/Desktop/MakeleProjesi/zaman_damgali_frameler/"

# --- KODUN GERİ KALANINI DEĞİŞTİRMENİZE GEREK YOK ---

def etiketsiz_resimleri_temizle():
    """
    Belirtilen klasör içinde, karşılığı olan bir .txt etiket dosyası olmayan
    görsel dosyalarını bulur ve siler.
    """
    
    # Klasörün var olup olmadığını kontrol et
    if not os.path.isdir(dataset_base_path):
        print(f"HATA: Belirtilen yol '{dataset_base_path}' bulunamadı veya bir klasör değil.")
        print("Lütfen 'dataset_base_path' değişkenini doğru ayarladığınızdan emin olun.")
        return

    print("--- Etiketi Olmayan Resimleri Temizleme Aracı ---")
    
    # Kullanıcı onayı al
    onay = input(f"UYARI: '{dataset_base_path}' klasöründeki etiketsiz resimler kalıcı olarak silinecektir.\n"
                 "Bu işlem geri alınamaz. Devam etmeden önce yedek aldığınızdan emin olun.\n"
                 "Devam etmek için 'evet' yazın: ")
    if onay.lower() != 'evet':
        print("İşlem kullanıcı tarafından iptal edildi.")
        return

    # Desteklenen resim dosyası uzantıları
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    try:
        # Klasördeki tüm dosyaları listele
        all_files = os.listdir(dataset_base_path)
        
        # Etiket dosyalarının uzantısız isimlerini bir sete kaydet (daha hızlı arama için)
        label_files_basenames = {os.path.splitext(f)[0] for f in all_files if f.endswith('.txt')}
        
    except FileNotFoundError:
        # Bu senaryo yukarıdaki isdir kontrolü ile pek olası değil ama güvenlik için kalabilir.
        print(f"HATA: Klasör taranırken bir sorun oluştu: {dataset_base_path}")
        return

    silinen_resim_sayisi = 0
    toplam_resim_sayisi = 0

    # Klasördeki her bir dosyayı kontrol et
    for filename in all_files:
        # Dosyanın uzantısını ve adını al
        basename, extension = os.path.splitext(filename)
        extension = extension.lower() # Uzantıyı küçük harfe çevir

        # Eğer dosya desteklenen bir resim uzantısına sahipse
        if extension in image_extensions:
            toplam_resim_sayisi += 1
            
            # Eğer resmin ismi, etiket isimleri setinde yoksa, bu "yetim" bir resimdir.
            if basename not in label_files_basenames:
                filepath = os.path.join(dataset_base_path, filename)
                try:
                    os.remove(filepath)
                    print(f"SİLİNDİ (etiket yok): {filename}")
                    silinen_resim_sayisi += 1
                except Exception as e:
                    print(f"HATA: '{filename}' silinirken bir sorun oluştu: {e}")

    print("\n--- İşlem Tamamlandı ---")
    print(f"Toplam {toplam_resim_sayisi} resim dosyası incelendi.")
    if silinen_resim_sayisi == 0:
        print("Temizlenecek etiketsiz resim bulunamadı. Tüm resimlerin bir etiketi var.")
    else:
        print(f"Toplam {silinen_resim_sayisi} adet etiketsiz resim dosyası silindi.")
    print("--------------------------")


if __name__ == "__main__":
    etiketsiz_resimleri_temizle()

