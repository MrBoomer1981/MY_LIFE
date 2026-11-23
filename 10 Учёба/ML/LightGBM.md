# LightGBM

[[10 Учёба/ML/ML|ML]]

Градиентный бустинг на деревьях с ростом по листьям. `num_leaves` ограничивает число листьев в дереве. Маленькое `min_child_samples` позволяет деревьям делиться на этой учебной выборке.

Зависимости для примера — `pip install lightgbm scikit-learn pandas`.

```python
import pandas as pd
from lightgbm import LGBMClassifier

X = pd.DataFrame({"value": [1, 2, 3, 4, 10, 11, 12, 13]})
y = [0, 0, 0, 0, 1, 1, 1, 1]
model = LGBMClassifier(n_estimators=10, num_leaves=4, min_child_samples=1,
                       verbosity=-1, n_jobs=1)
model.fit(X, y)
print(model.predict(pd.DataFrame({"value": [2, 12]})))
```

На macOS библиотеке LightGBM может потребоваться OpenMP. Установка описана в [руководстве LightGBM](https://lightgbm.readthedocs.io/en/stable/Installation-Guide.html).

[Документация](https://lightgbm.readthedocs.io/en/stable/pythonapi/lightgbm.LGBMClassifier.html)
