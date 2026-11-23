# CatBoost

[[10 Учёба/ML/ML|ML]]

Градиентный бустинг на деревьях для табличных задач. Вызов `fit(..., cat_features=[0])` отмечает первый столбец как категориальный. Пример обучает бинарный классификатор и предсказывает класс для новой строки.

Зависимости для примера — `pip install catboost`.

```python
from catboost import CatBoostClassifier

X = [["city", 10], ["city", 12], ["village", 35], ["village", 48]]
y = [0, 0, 1, 1]
model = CatBoostClassifier(iterations=10, verbose=False, allow_writing_files=False)
model.fit(X, y, cat_features=[0])
print(model.predict([["city", 11]]))
```

[Документация](https://catboost.ai/docs/en/concepts/python-reference_catboostclassifier)
