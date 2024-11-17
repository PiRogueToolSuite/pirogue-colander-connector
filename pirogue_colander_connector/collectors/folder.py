import logging
from pathlib import Path

from pirogue_colander_connector.collectors.artifact import ArtifactCollector
from pirogue_colander_connector.collectors.ignore import ColanderIgnoreFile
from pirogue_colander_connector.commands.configure import Configuration

log = logging.getLogger(__name__)


class FolderCollector:
    def __init__(self, folder_path: Path, case_id: str):
        self.folder_path = folder_path.absolute()
        self.colander_ignore = ColanderIgnoreFile(self.folder_path)
        configuration = Configuration()
        if not configuration.is_valid:
            msg = f'You Colander configuration is invalid'
            log.error(msg)
            raise Exception(msg)
        if not self.folder_path.exists() or (not self.folder_path.is_dir()):
            msg = f'The folder {self.folder_path} does not exist'
            log.error(msg)
            raise Exception(msg)
        self.colander_client = configuration.get_colander_client()
        self.case_id = case_id

    def collect(self):
        log.info(f'Listing files contained in {self.folder_path}')
        for f in self.folder_path.iterdir():
            if f.is_file() and not self.colander_ignore.is_ignored(f):
                collector = ArtifactCollector(
                    case_id=self.case_id,
                    artifact_path=f,
                )
                collector.collect()