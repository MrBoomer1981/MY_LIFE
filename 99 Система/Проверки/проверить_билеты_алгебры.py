#!/usr/bin/env python3
"""Проверяет названия и навигацию билетов; не изменяет файлы и не выполняет Git."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


def validate(vault: Path, registry: dict | None = None) -> list[str]:
    errors: list[str] = []
    if registry is None:
        registry = json.loads(
            (vault / '99 Система/Проверки/Реестр билетов по алгебре.json').read_text(encoding='utf-8')
        )
    tickets = registry['tickets']
    numbers = [t['number'] for t in tickets]
    if numbers != list(range(1, 31)):
        errors.append('Номера и порядок должны быть ровно 1–30, без пропусков и повторов.')
    digest = hashlib.sha256('\n'.join(t['title'] for t in tickets).encode()).hexdigest()
    if digest != registry['approved_titles_sha256']:
        errors.append('Названия отличаются от списка, подтверждённого пользователем.')
    source = vault / registry['source']
    if not source.is_file():
        errors.append('Исходный PDF отсутствует.')
    elif hashlib.sha256(source.read_bytes()).hexdigest() != registry['source_sha256']:
        errors.append('Исходный PDF изменился: нужна новая содержательная сверка билетов.')
    index_path = vault / registry['index']
    if not index_path.is_file():
        return errors + ['Официальный указатель отсутствует.']
    index = index_path.read_text(encoding='utf-8')
    expected_headings = [f"{t['number']}. {t['title']}" for t in tickets]
    actual_headings = re.findall(r'^## (\d+\. .+)$', index, re.MULTILINE)
    if actual_headings != expected_headings:
        errors.append('Заголовки указателя не совпадают с точными названиями и порядком эталона.')
    overview = (vault / '10 Учёба/Линейная алгебра/Линейная алгебра.md').read_text(encoding='utf-8')
    for t in tickets:
        number, title = t['number'], t['title']
        if t['source_ticket'] != number or not t.get('source_title') or not t.get('scope'):
            errors.append(f'Билет {number}: не указана или нарушена привязка к исходному билету.')
        expected = f"{number}. [[Билеты по алгебре#{number}. {title}|{title}]]"
        if overview.splitlines().count(expected) != 1:
            errors.append(f'Билет {number}: в обзоре нужен один пункт с точным названием и ссылкой.')
        note = vault / t['note']
        if not note.is_file():
            errors.append(f'Билет {number}: заметка не найдена: {t["note"]}')
            continue
        body = note.read_text(encoding='utf-8')
        if not t['sections'] or len(t['sections']) != len(set(t['sections'])):
            errors.append(f'Билет {number}: отсутствуют разделы либо есть повторы.')
        headings = re.findall(r'^## (.+)$', body, re.MULTILINE)
        for heading in t['sections']:
            if headings.count(heading) != 1:
                errors.append(f'Билет {number}: заголовок должен существовать однозначно: {heading}')
            expected_link = f'[[{note.stem}#{heading}|{heading}]]'
            # Проверяем ссылки именно внутри нужного билета, а не случайное совпадение в другом.
            ticket_head = f'## {number}. {title}\n'
            if ticket_head in index:
                section = index.split(ticket_head, 1)[1].split('\n## ', 1)[0]
                if expected_link not in section:
                    errors.append(f'Билет {number}: в его разделе нет ссылки на «{heading}».')
        reverse = f'[[Билеты по алгебре#{number}. {title}|Билет {number}. {title}]]'
        if reverse not in body:
            errors.append(f'Билет {number}: нет обратной связи с точным названием.')
    return errors


def main() -> int:
    vault = Path(__file__).resolve().parents[2]
    registry = json.loads((vault / '99 Система/Проверки/Реестр билетов по алгебре.json').read_text(encoding='utf-8'))
    errors = validate(vault, registry)
    if errors:
        print('Сверка билетов не пройдена:', file=sys.stderr)
        for error in errors:
            print('- ' + error, file=sys.stderr)
        return 1
    count = sum(len(t['sections']) for t in registry['tickets'])
    print(f'Проверено: 30 точных названий, номера 1–30, исходный PDF, {count} привязки к разделам и обратные ссылки.')
    print('Содержательная сверка определений, доказательств и примеров выполняется отдельно по правилам базы.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
