import json
import logging
from functools import partial
from pathlib import Path

from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TaskID, TextColumn, BarColumn, TimeRemainingColumn
from rich.prompt import IntPrompt

from pirogue_colander_connector.commands.configure import Configuration

log = logging.getLogger(__name__)


class ArtifactCollector:
    def __init__(self, artifact_path: Path, case_id: str, artifact_type_name: str = None,
                 attributes=None):
        configuration = Configuration()
        if not configuration.is_valid:
            msg = f'You Colander configuration is invalid'
            log.error(msg)
            return
        self.colander_client = configuration.get_colander_client()
        self.artifact_path = artifact_path
        self.case_id = case_id
        self.attributes = attributes or {}
        self.artifact_type = None
        self._load_extra_attributes()

        if not artifact_type_name:
            artifact_type_name = self.ask_type()
            self.artifact_type = self.colander_client.get_artifact_type_by_short_name(artifact_type_name)
            if not self.artifact_type:
                log.error('Unable to determine the type of the artifact.')
                return
        else:
            self.artifact_type = self.colander_client.get_artifact_type_by_short_name(artifact_type_name)

        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TimeElapsedColumn(),
        )
        self.progress.start()
        if not self.artifact_path.exists() or not self.artifact_path.is_file():
            msg = f'{self.artifact_path} is not a file'
            log.error(msg)
            raise Exception(msg)

    def _load_extra_attributes(self):
        # Load extra attributes from the metadata file if it exists
        metadata_file_path = self.artifact_path.parent / (self.artifact_path.name + '.metadata.json')
        if metadata_file_path.exists() and metadata_file_path.is_file():
            with metadata_file_path.open('r') as f:
                metadata = json.load(f)
            self.attributes.update(metadata)

    def ask_type(self):
        artifact_types = self.colander_client.get_artifact_types()
        user_choices = []
        index = 0
        print(f'Select the type of the artifact for the file {self.artifact_path}:')
        for t in artifact_types:
            name = t.get('name')
            print(f'{index} - {name}')
            user_choices.append((t.get('id'), t.get('name'), t.get('short_name')))
            index += 1
        choice = IntPrompt.ask('Enter the number corresponding to the type you want to use')
        if 0 > choice or choice > len(user_choices):
            log.error('Invalid choice')
            return None
        print(f'You have selected {user_choices[choice][1]}')
        return user_choices[choice][2]

    def collect(self):
        log.info(f'Start the upload of {self.artifact_path}')
        case = self.colander_client.get_case(self.case_id)
        task_id = self.progress.add_task(f'[purple] Processing {self.artifact_path}', visible=True)
        partial_cb = partial(ArtifactCollector.upload_progress_callback, progress=self.progress, task_id=task_id)
        artifact = self.colander_client.upload_artifact(
            self.artifact_path,
            case=case,
            artifact_type=self.artifact_type,
            progress_callback=partial_cb,
            extra_params={
                'attributes': self.attributes,
            }
        )
        self.progress.stop()
        return artifact

    @staticmethod
    def upload_progress_callback(what, percent, status, progress: Progress, task_id: TaskID):
        progress.update(task_id, advance=percent, total=100, description=f'{what} - {status}', visible=True)
