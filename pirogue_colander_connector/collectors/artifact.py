import logging
import os.path
import pathlib
from functools import partial

from colander_client.client import Client
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TaskID, TextColumn, BarColumn, TimeRemainingColumn
from rich.prompt import IntPrompt

from pirogue_colander_connector.commands.configure import Configuration

log = logging.getLogger(__name__)


class ArtifactCollector:
    colander_client: Client
    case_id: str
    artifact_path: pathlib.Path
    artifact_type: str
    progress_bar: Progress
    attributes: dict

    def __init__(self, artifact_path: [str, pathlib.Path], case_id: str, artifact_type_name: str = None,
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
        if type(artifact_path) is str:
            if not os.path.exists(artifact_path) or not os.path.isfile(artifact_path):
                msg = f'{artifact_path} is not a file'
                log.error(msg)
                raise Exception(msg)
        elif not artifact_path.exists() or not os.path.isfile(artifact_path):
            msg = f'{artifact_path} is not a file'
            log.error(msg)
            raise Exception(msg)

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
