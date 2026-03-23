import os
import shutil
import math
import sys

# 1. Gerekli bilgileri kullanıcıdan al
try:
    source_folder = input("Lütfen görsellerin bulunduğu ana klasörün yolunu girin: ")

    # Girilen yolun geçerli bir klasör olup olmadığını kontrol et
    if not os.path.isdir(source_folder):
        print(f"\nHata: '{source_folder}' adında bir klasör bulunamadı veya bu bir klasör değil.")
        sys.exit() # Programı sonlandır

    num_folders = int(input("Kaç adet alt klasöre ayırmak istiyorsunuz?: "))
    if num_folders <= 0:
        print("\nHata: Klasör sayısı 0'dan büyük olmalıdır.")
        sys.exit()

except ValueError:
    print("\nHata: Lütfen klasör sayısı için geçerli bir tamsayı girin.")
    sys.exit()
except Exception as e:
    print(f"Beklenmedik bir hata oluştu: {e}")
    sys.exit()


# 2. Sadece görsel dosyalarını listele (diğer dosyaları ve klasörleri yoksay)
try:
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
    all_files_in_source = os.listdir(source_folder)
    
    # Dosya olup olmadığını ve uzantısının listede olup olmadığını kontrol et
    image_files = [f for f in all_files_in_source 
                   if os.path.isfile(os.path.join(source_folder, f)) and os.path.splitext(f)[1].lower() in image_extensions]

    if not image_files:
        print("\nHata: Belirtilen klasörde hiç görsel dosyası bulunamadı.")
        sys.exit()

except Exception as e:
    print(f"Dosyalar okunurken bir hata oluştu: {e}")
    sys.exit()

# 3. Hesaplamaları yap
total_images = len(image_files)
# math.ceil kullanarak bölme sonucunu yukarı yuvarla, böylece hiçbir dosya dışarıda kalmaz
images_per_folder = math.ceil(total_images / num_folders)

print("\n" + "="*40)
print("İŞLEM ÖZETİ")
print(f"-> Toplam {total_images} adet görsel bulundu.")
print(f"-> {num_folders} adet yeni klasör oluşturulacak.")
print(f"-> Her bir klasöre en fazla {images_per_folder} adet görsel dağıtılacak.")
print("="*40 + "\n")


# 4. Klasörleri oluştur ve dosyaları taşı
try:
    for i in range(num_folders):
        # Yeni klasör adını ve yolunu oluştur (Grup_1, Grup_2, ...)
        folder_name = f"Grup_{i + 1}"
        destination_path = os.path.join(source_folder, folder_name)

        # Klasör yoksa oluştur
        os.makedirs(destination_path, exist_ok=True)

        # Bu klasöre taşınacak dosyaları listeden ayır (slice)
        start_index = i * images_per_folder
        end_index = start_index + images_per_folder
        files_to_move = image_files[start_index:end_index]

        # Dosyaları taşı
        for file_name in files_to_move:
            source_file_path = os.path.join(source_folder, file_name)
            destination_file_path = os.path.join(destination_path, file_name)
            shutil.move(source_file_path, destination_file_path)
            print(f"'{file_name}' -> '{folder_name}' klasörüne taşındı.")

    print("\nİşlem başarıyla tamamlandı!")

except Exception as e:
    print(f"\nDosyalar taşınırken bir hata oluştu: {e}")