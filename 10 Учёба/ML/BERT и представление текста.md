# BERT и представление текста

[[10 Учёба/ML/ML|ML]]

BERT — предобученная нейросеть, которая вычисляет контекстные представления токенов. Токенизатор превращает текст в тензоры, `model(**inputs)` возвращает представления. Для классификации нужны обученная классификационная голова или отдельный классификатор.

Зависимости для примера — `pip install torch transformers`.

```python
import torch
from transformers import AutoModel, AutoTokenizer

checkpoint = "google-bert/bert-base-multilingual-cased"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModel.from_pretrained(checkpoint).eval()
inputs = tokenizer("Хороший товар", return_tensors="pt", truncation=True)

with torch.inference_mode():
    tokens = model(**inputs).last_hidden_state

print(tokens.shape)  # (1, число токенов, 768)
```

Первый запуск загружает токенизатор и веса модели из Hugging Face.

[Документация](https://huggingface.co/docs/transformers/model_doc/bert)
