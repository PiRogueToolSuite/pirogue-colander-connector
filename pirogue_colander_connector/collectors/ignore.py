from pathlib import Path
from fnmatch import fnmatch


class ColanderIgnoreFile:
    ignore_file_name = '.colander_ignore'
    default_ignore_patterns = {
        ignore_file_name,
        '*.metadata.json',
        '*.pid',
        '*.tsr',
        '*.tsq',
        '*.crt',
        '*.pem',
        '*.md',
    }

    def __init__(self, path: Path) -> None:
        self.path: Path = path
        self.ignored_patterns: set[str] = self.default_ignore_patterns
        if path.is_file():
            self.ignore_file_path = path.parent / self.ignore_file_name
        else:
            self.ignore_file_path: Path = self.path / self.ignore_file_name
        self.load_ignore_file()

    def is_ignored(self, path: Path) -> bool:
        for pattern in self.ignored_patterns:
            if fnmatch(path.name, pattern):
                return True
            elif fnmatch(str(path), pattern):
                return True
        return False

    def add_ignored_pattern(self, pattern: str) -> None:
        self.ignored_patterns.add(pattern)

    def save_ignore_file(self):
        with self.ignore_file_path.open('w') as file:
            for ignore_file in self.ignored_patterns:
                file.write(f'{str(ignore_file)}\n')

    def load_ignore_file(self):
        if self.ignore_file_path.exists() and self.ignore_file_path.is_file():
            with self.ignore_file_path.open() as f:
                for line in f.readlines():
                    if line.startswith('#') or not line.strip():
                        continue
                    self.ignored_patterns.add(line.strip())
