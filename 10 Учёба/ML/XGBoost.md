# XGBoost

[[10 Учёба/ML/ML|ML]]

Градиентный бустинг на деревьях для табличных задач. `XGBClassifier` обучает классификатор, а `predict` возвращает классы новых строк. Пример использует числовые признаки.

Зависимости для примера — `pip install xgboost scikit-learn`.

```python
import numpy as np
from xgboost import XGBClassifier

X = np.arange(8).reshape(-1, 1)
y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
model = XGBClassifier(n_estimators=10, max_depth=2, n_jobs=1)
model.fit(X, y)
print(model.predict(np.array([[1], [6]])))
```

[Документация](https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBClassifier)
