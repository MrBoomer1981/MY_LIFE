#!/usr/bin/env python3
"""Проверяет размещение учебных тем и ссылки; файлы не изменяет.

Проверка структуры не подтверждает полноту теории и правильность доказательств.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


LINK = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]')
HEADING = re.compile(r'^(#{1,6})\s+(.+?)\s*#*\s*$')
APPENDIX = re.compile(
    r'^(?:дополнения?|продолжение|новые материалы|новые лекции)(?:$|\s+[—–-])'
    r'|(?:дополнение|дополнения|продолжение)\s+по\s+(?:рукопис|лекци|материал)'
    r'|\b20\d{2}-\d{2}-\d{2}\b', re.IGNORECASE
)
SOURCES = re.compile(r'^(?:полные\s+)?источники?\b', re.IGNORECASE)
# Этот раздел содержит обратные ссылки, а не продолжение учебной теории.
NAVIGATION = {'Соответствие официальным билетам'}


def markdown_lines(text: str) -> list[str]:
    """Примеры кода не являются заголовками и ссылками учебной заметки."""
    lines: list[str] = []
    fence = ''
    for line in text.splitlines():
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if marker:
            value = marker[1]
            if not fence:
                fence = value
            elif value[0] == fence[0] and len(value) >= len(fence):
                fence = ''
            continue
        if not fence:
            lines.append(line)
    return lines


def headings(text: str) -> list[str]:
    return [m[2] for line in markdown_lines(text) if (m := HEADING.match(line))]


def validate(vault: Path, overview: Path, coverage: Path | None = None) -> list[str]:
    errors: list[str] = []
    course = overview.parent
    files = list(vault.rglob('*'))
    by_name: dict[str, list[Path]] = {}
    for path in files:
        if path.is_file():
            by_name.setdefault(path.name, []).append(path)

    def resolve(target: str, document: Path = overview) -> tuple[Path | None, str]:
        name, _, anchor = target.partition('#')
        if not name:
            return document, anchor
        relative = Path(name)
        if not relative.suffix:
            relative = relative.with_suffix('.md')
        for candidate in (vault / relative, document.parent / relative, course / relative):
            if candidate.is_file():
                return candidate, anchor
        matches = by_name.get(relative.name, [])
        return (matches[0] if len(matches) == 1 else None), anchor

    bodies = {p: p.read_text(encoding='utf-8') for p in course.rglob('*.md')}
    overview_body = bodies[overview]
    normal: set[Path] = set()
    detailed: set[Path] = set()
    section = ''
    for line in markdown_lines(overview_body):
        match = HEADING.match(line)
        if match and len(match[1]) == 2:
            section = match[2]
        for target in LINK.findall(line):
            note, _ = resolve(target)
            if note not in bodies or note == overview:
                continue
            if not SOURCES.match(section) and not APPENDIX.search(section):
                normal.add(note)
                if section == 'Подробные темы':
                    detailed.add(note)

    for note, body in bodies.items():
        name = str(note.relative_to(vault))
        source_section_seen = False
        for line in markdown_lines(body):
            if not (match := HEADING.match(line)):
                continue
            title = match[2]
            if APPENDIX.search(title):
                errors.append(f'{name}: материал сгруппирован по пакету/дате: «{title}».')
            if len(match[1]) == 2:
                if SOURCES.match(title):
                    source_section_seen = True
                elif source_section_seen and title not in NAVIGATION:
                    errors.append(f'{name}: тематический раздел «{title}» стоит после источников.')
        if note != overview and note not in normal:
            errors.append(f'{name}: нет ссылки в основном тематическом оглавлении курса.')

    link_documents = dict(bodies)
    if coverage is not None:
        link_documents[coverage] = coverage.read_text(encoding='utf-8')
    for document, body in link_documents.items():
        for target in LINK.findall('\n'.join(markdown_lines(body))):
            note, anchor = resolve(target, document)
            if note is None:
                errors.append(f'{document.name}: отсутствует или неоднозначна ссылка [[{target}]].')
                continue
            if anchor and note.suffix == '.md':
                text = note.read_text(encoding='utf-8')
                if anchor.startswith('^'):
                    exists = anchor in text
                else:
                    exists = anchor in headings(text)
                if not exists:
                    errors.append(f'{document.name}: не найден раздел [[{target}]].')
            if document == coverage and note in bodies and note != overview:
                required = detailed if 'Подробные темы' in headings(overview_body) else normal
                if note not in required:
                    errors.append(f'{note.name}: тема из сверки отсутствует в основном списке подробных тем.')

    for canvas in course.rglob('*.canvas'):
        try:
            data = json.loads(canvas.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            errors.append(f'{canvas.name}: некорректный JSON.')
            continue
        ids = {node['id'] for node in data.get('nodes', [])}
        for node in data.get('nodes', []):
            if node.get('type') == 'file' and not (vault / node['file']).is_file():
                errors.append(f'{canvas.name}: отсутствует файл {node["file"]}.')
        for edge in data.get('edges', []):
            if edge['fromNode'] not in ids or edge['toNode'] not in ids:
                errors.append(f'{canvas.name}: связь с отсутствующим узлом {edge["id"]}.')
    return list(dict.fromkeys(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('overview', help='Путь к обзору курса от корня хранилища')
    parser.add_argument('--покрытие', dest='coverage', help='Таблица сверки источников с темами (Markdown)')
    args = parser.parse_args()
    vault = Path(__file__).resolve().parents[2]
    overview = (vault / args.overview).resolve()
    coverage = (vault / args.coverage).resolve() if args.coverage else None
    if not overview.is_relative_to(vault / '10 Учёба') or not overview.is_file():
        parser.error('Нужен существующий обзор курса внутри 10 Учёба/.')
    if coverage is not None and not coverage.is_file():
        parser.error('Файл таблицы сверки не найден.')
    errors = validate(vault, overview, coverage)
    if errors:
        print('Тематическая интеграция не пройдена:', file=sys.stderr)
        for error in errors:
            print('- ' + error, file=sys.stderr)
        return 1
    print('Оглавление, размещение разделов, ссылки и Canvas: OK.')
    print('Полнота содержания и доказательства сверяются с оригиналами отдельно.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
