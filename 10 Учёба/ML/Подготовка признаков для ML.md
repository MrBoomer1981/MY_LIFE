# Подготовка признаков для ML

[[10 Учёба/ML/ML|ML]]

Encoding меняет представление признака, например марки автомобиля. Feature extraction извлекает числовые признаки из текста, например TF-IDF. Feature engineering создаёт производные признаки, например пробег за год. Обучаемые преобразования подгоняют на тренировочных данных.

Зависимости для примера — `pip install scikit-learn`.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(handle_unknown="ignore")
encoder.fit([["BMW"], ["Audi"], ["Volvo"]])
print(encoder.transform([["BMW"]]).toarray())

vectorizer = TfidfVectorizer()
vectorizer.fit(["хороший товар", "плохая доставка"])
print(vectorizer.transform(["хорошая доставка"]).shape)

def mileage_per_year(mileage, age_years):
    return mileage / age_years if age_years > 0 else None

print(mileage_per_year(60_000, 3))  # 20000.0
```

## Сравнение подходов

![[99 Система/Вложения/Screenshot 2026-11-22 at 11.01.44.png]]

Для отзыва TF-IDF превращает текст в признаки `X`. Метку `y`, например 0 или 1, задаёт разметка. Подробнее в [[Слабая разметка и Snorkel]].

[Документация](https://scikit-learn.org/stable/api/index.html)
