import csv
import random
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Modelin yerel yolu
model_path = r"C:\db\models--joeddav--xlm-roberta-large-xnli\snapshots\b227ee8435ceadfa86dc1368a34254e2838bf242"

# Model ve tokenizer yükleniyor
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

# Sıfırdan sınıflandırma pipeline'ı
classifier = pipeline(
    "zero-shot-classification",
    model=model,
    tokenizer=tokenizer
)

# Ana kategoriler
category_labels = ["gıda", "elektronik", "otomotiv", "temizlik"]

# Alt kategoriler
alt_category_labels = {
    "gıda": ["Meyve Suyu", "İçecek", "Çikolata", "Kraker", "Bisküvi", 'Soğuk çay', "Soda", "Süt", "Kek", 'Atıştırmalık',
             "Yağ", "Dondurma", 'Enerji İçeceği', "Şekerleme", "Su", "Kahve", "Kahvaltılık", "İçecek", 'Yoğurt', 'Et', "Sıcak İçecek",
             "Çay", "Gazlı İçecek", "Diğer Gıda"],
    "elektronik": ["Beyaz Eşya", "Televizyon", "Ses Sistemi / Kulaklık", "Küçük Ev Aletleri",
                   "Küçük Mutfak Aletleri", "Klima", "Diğer Elektronik"],
    "temizlik": ["Çamaşır Temizliği", "Kişisel Temizlik", 'Banyo Temizliği', "Oda Kokusu", "Bulaşık Temizliği",
                 "Yüzey Temizliği", 'Makine Temizleyici', 'Mutfak', 'Temizlik bezi/Süngeri/Paspas',
                 'Genel Temizlik', "Diğer Temizlik"],
    "otomotiv": ["Otomotiv / Savunma"]
}

# CSV'den ürün verilerini oku
def load_data(filename="scraped_data_with_subcategories.csv"):
    data = []
    try:
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if len(row) >= 4:
                    data.append((row[0], row[1], row[2], row[3]))
    except Exception as e:
        print("Veri yükleme hatası:", e)
    return data

product_data = load_data()

def classify_and_recommend(user_input):
    # Ana kategori tahmini
    category_result = classifier(user_input, category_labels)
    top_category = category_result["labels"][0].lower()

    # Alt kategori tahmini
    alt_candidates = alt_category_labels.get(top_category, [])
    alt_result = classifier(user_input, alt_candidates) if alt_candidates else {"labels": ["Bilinmiyor"]}
    top_subcategory = alt_result["labels"][0]

    # Ürün eşleştirme
    matched = [
        {"product": p[0], "brand": p[1], "subcategory": p[3]}
        for p in product_data
        if top_category in p[2].lower() and top_subcategory in p[3]
    ]

    random.shuffle(matched)
    unique_products = list({item["product"] for item in matched[:5]})

    return top_category, top_subcategory, unique_products

# Konsoldan kullanıcı girdisi alma
if __name__ == "__main__":
    print("Ürün öneri sistemine hoş geldiniz!")
    while True:
        user_input = input("Bir ürün, kategori veya marka girin (çıkmak için q): ").strip()
        if user_input.lower() == "q":
            print("Programdan çıkılıyor.")
            break

        category, subcategory, products = classify_and_recommend(user_input)
        print("\n--- Sonuçlar ---")
        print(f"Ana kategori: {category.title()}")
        print(f"Alt kategori: {subcategory}")

        if products:
            print("\nÖnerilen Ürünler:")
            for i, prod in enumerate(products, 1):
                print(f"{i}. {prod}")
        else:
            print("Bu kategoriye uygun ürün bulunamadı.")
        print("\n")
