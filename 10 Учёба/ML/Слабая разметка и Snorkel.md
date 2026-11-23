# Слабая разметка и Snorkel

[[10 Учёба/ML/ML|ML]]

Weak supervision создаёт приблизительные метки из правил, словарей или ответов моделей. В Data Programming эти правила оформляют как функции разметки. LabelModel объединяет их шумные ответы, оценивая надёжность источников.

Зависимости для примера — `pip install snorkel numpy`.

```python
import numpy as np
from snorkel.labeling.model import LabelModel

# Строки соответствуют объектам, столбцы — трём правилам.
# -1 означает воздержание, 0 и 1 — классы.
labels = np.array([
    [1, 1, -1], [1, -1, 1], [1, 1, 1], [1, 0, 1],
    [0, 0, -1], [0, -1, 0], [0, 0, 0], [0, 1, 0],
])
model = LabelModel(cardinality=2, verbose=False)
model.fit(L_train=labels, n_epochs=20, seed=42)
print(model.predict_proba(L=labels).round(2))
```

Столбец также может содержать ответы LLM с заданным набором меток. Так можно получить разметку для обучения меньшей модели. Качество полученных меток оценивают на вручную размеченной выборке.

## Откуда берутся метки

![[99 Система/Вложения/Screenshot 2026-11-20 at 16.19.06.png]]

В supervised learning даны метки, в semi-supervised их дополняют неразмеченными данными, а в self-supervised сигнал извлекают из структуры самих данных. В active learning модель предлагает примеры для ручной разметки.

[Документация](https://snorkel.readthedocs.io/en/latest/packages/_autosummary/labeling/snorkel.labeling.model.label_model.LabelModel.html)
