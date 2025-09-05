from flask import Flask, request, jsonify  #Flask framework'ünden temel sınıflar
from flask_cors import CORS #CORS: farklı origin'lerden gelen isteklere izin verir
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import csv
import random

#Flask uygulamasını oluştur ve CORS'u aktif et
app = Flask(__name__)
CORS(app)
# Modelin yerel yolu
model_path = r"C:\db\models--joeddav--xlm-roberta-large-xnli\snapshots\b227ee8435ceadfa86dc1368a34254e2838bf242"  # Burayı kendi model yolunuzla değiştirin

# Yerel model ve tokenizer yükleniyor
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

#Zero shot sınıflandırma pipeline'ı
classifier = pipeline(
    "zero-shot-classification",
    model=model,
    tokenizer=tokenizer
)

# Main categories
category_labels = ["gıda", "elektronik", "otomotiv", "temizlik"]

# Subcategories
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

# Load product data
def load_data(filename="scraped_data_with_subcategories.csv"):
    product_data = []
    with open(filename, mode="r", encoding="utf-8") as file: #okuma modunda aç
        reader = csv.reader(file) #okuyucu nesnesi
        next(reader)  # ilk satırı (başlığı) atla
        for row in reader:
            product_data.append((row[0], row[1], row[2], row[3]))  #listeye tuple olarak ekleniyor
    return product_data

product_data = load_data()


#e posta gönderme (gmail SMTP kullanır)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, to_email):
    sender_email = "yerlikesif@gmail.com"
    app_password = "hmrb bbzs qrrp nlxo"  # Google’dan aldığın uygulama şifresi

    msg = MIMEMultipart() #MIME çok parçalı mesaj
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain")) #plain:HTML değil

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:  #465: SMTP protokolü için güvenli (şifreli) bağlantı kurulan port numarasıdır.
        server.login(sender_email, app_password)
        server.sendmail(sender_email, to_email, msg.as_string())


@app.route('/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        subject = data.get("subject")
        message = data.get("message")

        # Veriyi terminalde göster (test için)
        print(f"İletişim mesajı:\nAd: {name}\nEmail: {email}\nTelefon: {phone}\nKonu: {subject}\nMesaj: {message}")

        # CSV’ye kaydetmek
        with open("contact_messages.csv", "a", newline="", encoding="utf-8") as file:  #a: append: sonuna ekle olanlara dokunma
            writer = csv.writer(file)
            writer.writerow([name, email, phone, subject, message])

        full_message = (
            f"İsim: {name}\n"
            f"Email: {email}\n"
            f"Telefon: {phone}\n"
            f"Konu: {subject}\n\n"
            f"Mesaj:\n{message}"
        )
        send_email(subject=f"Yeni İletişim: {subject}",
                   body=full_message,
                   to_email="yerlikesif@gmail.com")
        return jsonify({"message": "Mesaj başarıyla gönderildi ve e‑posta yollandı!"}), 200

    except Exception as e:
        print("Hata:", e)
        return jsonify({"error": "Bir hata oluştu."}), 500



@app.route('/process', methods=['POST'])
def process():
    try:
        user_input = request.json.get('input', '').strip()   #Eğer 'input' anahtarı yoksa, boş bir string '' döner.
        if not user_input:
            return jsonify({"message": "Lütfen geçerli bir girdi sağlayın."}), 400

        # Predict main category
        category_result = classifier(user_input, category_labels)
        top_category = category_result["labels"][0].lower()

        # Predict subcategory
        alt_labels = alt_category_labels.get(top_category, [])
        alt_category_result = classifier(user_input, alt_labels)
        top_alt_category = alt_category_result["labels"][0]

        # Filter matching products
        matched = [
            {"product": p[0], "brand": p[1], "subcategory": p[3]}
            for p in product_data
            if top_category in p[2].lower() and top_alt_category in p[3]
        ]

        random.shuffle(matched)
        unique_products = list({item["product"] for item in matched[:10]})

        if unique_products:
            message = (
                f"En iyi kategori: {top_category.capitalize()}\n"
                f"Alt kategori: {top_alt_category}\n"
            )
        else:
            message = (
                f"En iyi kategori: {top_category.capitalize()} - Alt kategori: {top_alt_category}.\n"
                "Bu kategoriye uygun ürün bulunamadı."
            )

        return jsonify({
            "message": message,
            "products": unique_products,
            "category": top_category.capitalize(),
            "subcategory": top_alt_category
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#app başlatılıyor
if __name__ == '__main__':
    app.run(debug=True)
