---
тип: теория
направление: Python
создано: 2026-10-31
---

[[Python]]

# Python — сигнатуры и связывание аргументов

> [!abstract] Суть
> Сигнатура определяет, каким параметрам соответствуют аргументы вызова. Правильная форма вызова ещё не означает правильные типы и значения.

## Пять видов параметров

```python
def attack(pokemon, /, move, *targets, crit=False, **effects):
    ...
```

| Параметр | `inspect.Parameter.kind` | Принимает |
|---|---|---|
| `pokemon` перед `/` | `POSITIONAL_ONLY` | Только позиционный аргумент |
| `move` | `POSITIONAL_OR_KEYWORD` | Позиционный либо именованный |
| `*targets` | `VAR_POSITIONAL` | Остальные позиционные, собирая кортеж |
| `crit` после `*targets` или отдельной `*` | `KEYWORD_ONLY` | Только именованный |
| `**effects` | `VAR_KEYWORD` | Остальные именованные, собирая словарь |

Позиционные-only параметры описаны PEP 570, keyword-only — PEP 3102. В обычной записи вызова позиционные аргументы идут до именованных: `attack(pokemon="X", "Ember")` синтаксически неверно. Распаковка при вызове имеет собственные правила; это ограничение примера не следует переносить на все сочетания `*` и именованных аргументов.

## Куда попадает флаг

```python
attack("Pikachu", "Thunderbolt", "Onix", True)
# targets == ('Onix', True), crit == False

attack("Pikachu", "Thunderbolt", "Onix", crit=True)
```

`*targets` собирает все оставшиеся позиционные аргументы, не угадывая смысл `True`. В варианте `def attack(p, m, *, crit=False)` дополнительный позиционный аргумент запрещён и вызов `attack(p, m, True)` даёт `TypeError`.

Аналогично `dispatch(monster, *doors, urgent=False)` при `dispatch("Sulley", "A7", True)` получает `doors=('A7', True)`, `urgent=False`. При `dispatch("Mike")` кортеж дверей пуст — это допустимо. В сигнатуре `dispatch(monster, /, door)` попытка `dispatch(monster="Mike", door="A7")` не связывается, тело не выполняется.

## Positional-only имя и словарь kwargs

```python
def identify(pokemon, /, **effects):
    return pokemon, effects

identify("Pikachu", pokemon="Meowth")
# ('Pikachu', {'pokemon': 'Meowth'})
```

Имя positional-only параметра не используется при распределении именованных аргументов, поэтому одноимённый ключ может попасть в `**effects`. В исходном PDF пример с таким результатом сокращён; здесь показана соответствующая сигнатура. Для полной `attack` выше дополнительно требуется `move`.

## Сборка и распаковка

В определении `*args` и `**kwargs` собирают аргументы; при вызове `*team` и `**status` распаковывают:

```python
attack("Charmander", "Ember", *team, **status)
```

Сборка не копирует сами переданные объекты. Два вызова `pack(*doors)` из примера дают разные непустые кортежи результатов `a` и `b`, но `a[0] is b[0]` истинно, если передан один объект. Утверждение о разных кортежах не следует обобщать на пустой кортеж и все оптимизации реализации.

## bind без выполнения тела

```python
from inspect import signature

def dispatch(monster, *doors, urgent=False, **effects):
    return monster, doors, urgent, effects

sig = signature(dispatch)
bound = sig.bind("Sulley", "A7", True)
# bound.arguments == {'monster': 'Sulley', 'doors': ('A7', True)}
bound.apply_defaults()
# добавлены urgent=False и effects={}
result = dispatch(*bound.args, **bound.kwargs)
```

`signature(fn).parameters` содержит параметры с их `.kind`. `bind()` проверяет форму и распределяет аргументы, не вызывая функцию; `apply_defaults()` добавляет пропущенные значения по умолчанию и пустые собирательные параметры. Сам вызов происходит только в последней строке.

Успешный `bind` не гарантирует, что дверь является строкой. Это проверяется телом, например `if not isinstance(door, str): raise ValueError(...)`. Аннотация `value: int` описывает ожидаемый тип, но сама не запрещает строку: функция без явной проверки может вернуть `"trainee"` как есть.

Связанные темы: [[Python — области видимости и функции]], [[Python — значения по умолчанию]], [[Python — декораторы и композиция]].

## Источник

[[PYTHON.pdf]] — конспект лекций 2–7 ФТИИ ИТМО. Материал переработан по темам, без упражнений и заданий.
