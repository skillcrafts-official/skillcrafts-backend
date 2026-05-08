from pathlib import Path
import re


def read_md_section(filename: str, section: str | None = None) -> str:
    """
    Читает Markdown файл или конкретную секцию.

    Args:
        filename: Имя файла в docs/api/ или другой библиотеки
        section: Название секции (например '## Login')

    Returns:
        Текст секции или весь файл
    """
    docs_dir = Path(__file__).parent.parent / "docs"
    file_path = docs_dir / filename

    if not file_path.exists():
        return ""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Убираем BOM если есть (проблема с Windows)
    if content.startswith('\ufeff'):
        content = content[1:]

    if not section:
        return content

    # Экранируем специальные символы в названии раздела
    escaped_section = re.escape(section)

    # Извлекаем конкретную секцию
    pattern = rf'^\#\#\ {escaped_section}\n([\s\S]*?)(?=\n##\s|\Z)'
    match = re.search(pattern, content, re.MULTILINE)

    return match.group(1).strip() if match else ""


if __name__ == '__main__':

    print(read_md_section('auth.md', '## POST /auth/token'))
