from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline, XLMRobertaTokenizer
import csv
import random

app = Flask(__name__)
CORS(app)

# Hugging Face zero-shot classification pipeline
tokenizer = XLMRobertaTokenizer.from_pretrained("joeddav/xlm-roberta-large-xnli")
classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli", tokenizer=tokenizer)

# Categories
category_labels = ["gıda", "elektronik", "otomotiv", "temizlik"]

# Load product data from CSV
def load_data(filename="scraped_data.csv"):
    product_data = []
    with open(filename, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            product_data.append((row[0], row[1], row[2]))  # Product name, brand, category
    return product_data

product_data = load_data()

@app.route('/process', methods=['POST'])
def process():
    try:
        # Get user input
        user_input = request.json.get('input', '').strip()
        if not user_input:
            return jsonify({"message": "Lütfen geçerli bir girdi sağlayın."}), 400

        # Predict category using zero-shot classification
        category_result = classifier(user_input, category_labels)
        top_category = category_result["labels"][0]

        # Filter products by top predicted category
        matched_products = [
            {"product": product[0], "brand": product[1]}
            for product in product_data
            if top_category.lower() in product[2].lower()
        ]

        # Shuffle and get up to 10 unique products
        random.shuffle(matched_products)
        seen = set()
        unique_products = []
        for item in matched_products:
            if item["product"] not in seen:
                unique_products.append(item)
                seen.add(item["product"])
            if len(unique_products) == 10:
                break

        if unique_products:
            return jsonify({
                "message": f"En iyi kategori: {top_category}",
                "user_input": user_input,
                "category": top_category,
                "products": [item["product"] for item in unique_products]
            })
        else:
            return jsonify({
                "message": f"En iyi kategori: {top_category}. Ancak bu kategoriye uygun ürün bulunamadı.",
                "user_input": user_input,
                "category": top_category,
                "products": []
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
