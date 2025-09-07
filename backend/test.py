import random
import csv
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Modelin yolu
model_path = r"C:\db\models--joeddav--xlm-roberta-large-xnli\snapshots\b227ee8435ceadfa86dc1368a34254e2838bf242"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
classifier = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer)

# Ana ve alt kategoriler
main_categories = ["gıda", "elektronik", "otomotiv", "temizlik"]
sub_categories = {
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

# Veriyi oku ve rastgele 5 satır seç
with open("scraped_data_with_subcategories.csv", encoding="utf-8-sig") as f:
    reader = list(csv.DictReader(f))
    random_samples = random.sample(reader, 20) #rastgele 20 tane seçer

# Her bir örnek için tahmin yap
for row in random_samples:
    text = row["Ürün İsmi"]
    true_main = row["Kategori"].lower().replace(" ürünleri", "")
    true_sub = row["Alt Kategori"]

    # Ana kategori tahmini
    result_main = classifier(text, main_categories)
    predicted_main = result_main["labels"][0].lower()

    # Alt kategori tahmini
    result_sub = classifier(text, sub_categories.get(predicted_main, []))
    predicted_sub = result_sub["labels"][0] if result_sub["labels"] else "Belirsiz"

    print("-" * 60)
    print(f"Ürün İsmi: {text}")
    print(f" Gerçek Ana Kategori: {true_main} |  Tahmin: {predicted_main}")
    print(f"Gerçek Alt Kategori: {true_sub} |  Tahmin: {predicted_sub}")
