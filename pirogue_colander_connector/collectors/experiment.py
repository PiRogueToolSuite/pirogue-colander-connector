import json
import os.path
import pathlib
import logging

from colander_client.client import Client

from pirogue_colander_connector.collectors.artifact import ArtifactCollector
from pirogue_colander_connector.commands.configure import Configuration

log = logging.getLogger(__name__)


class ExperimentCollector:
    colander_client: Client
    case_id: str
    experiment_path: pathlib.Path
    experiment_details_path: str
    experiment_name: str
    artifacts = {}

    def __init__(self, experiment_path: pathlib.Path, case_id: str, experiment_name: str):
        configuration = Configuration()
        if not configuration.is_valid:
            msg = f'You Colander configuration is invalid'
            log.error(msg)
            return
        self.colander_client = configuration.get_colander_client()
        self.experiment_path = experiment_path
        self.case_id = case_id
        self.experiment_name = experiment_name
        self.experiment_details_path = f'{experiment_path}/experiment.json'
        if not experiment_path.exists() or not os.path.isdir(experiment_path):
            msg = f'{experiment_path} is not a directory'
            log.error(msg)
            raise Exception(msg)
        if not os.path.isfile(self.experiment_details_path):
            msg = f'{self.experiment_details_path} not found'
            log.error(msg)
            raise Exception(msg)

    def collect(self):
        log.info(f'Reading the experiment details from {self.experiment_details_path}')
        with open(self.experiment_details_path) as f:
            experiment_details = json.load(f)
        for file_type, details in experiment_details.items():
            log.info(f'Dispatch collection of the {file_type} artifact')
            self.__dispatch_collection(file_type, details)
        pcap = self.artifacts.get('network', None)
        socket_trace = self.artifacts.get('socket_traces', None)
        sslkeylog = self.artifacts.get('sslkeylog', None)
        crypto_traces = self.artifacts.get('crypto_traces', None)
        screen = self.artifacts.get('screen', None)
        experiment = self.colander_client.create_pirogue_experiment(
            name=self.experiment_name,
            case=self.colander_client.get_case(self.case_id),
            pcap=pcap,
            socket_trace=socket_trace,
            sslkeylog=sslkeylog,
            extra_params={
                'screencast': screen,
                'aes_trace': crypto_traces,
                'target_artifact': None
            }
        )

    def __dispatch_collection(self, file_type: str, details: dict):
        filename = details.pop('file')
        file_path = f'{self.experiment_path}/{filename}'
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            msg = f'{file_path} not found'
            log.error(msg)
            raise Exception(msg)
        if file_type == 'network':
            ac = ArtifactCollector(
                case_id=self.case_id,
                artifact_path=f'{self.experiment_path}/{filename}',
                artifact_type_name='PCAP',
                attributes=details,
            )
            artifact = ac.collect()
            self.artifacts[file_type] = artifact
        elif file_type == 'socket_traces':
            ac = ArtifactCollector(
                case_id=self.case_id,
                artifact_path=f'{self.experiment_path}/{filename}',
                artifact_type_name='SOCKET_T',
                attributes=details,
            )
            artifact = ac.collect()
            self.artifacts[file_type] = artifact
        elif file_type == 'crypto_traces':
            ac = ArtifactCollector(
                case_id=self.case_id,
                artifact_path=f'{self.experiment_path}/{filename}',
                artifact_type_name='CRYPTO_T',
                attributes=details,
            )
            artifact = ac.collect()
            self.artifacts[file_type] = artifact
        elif file_type == 'sslkeylog':
            ac = ArtifactCollector(
                case_id=self.case_id,
                artifact_path=f'{self.experiment_path}/{filename}',
                artifact_type_name='SSLKEYLOG',
                attributes=details,
            )
            artifact = ac.collect()
            self.artifacts[file_type] = artifact
        elif file_type == 'screen':
            ac = ArtifactCollector(
                case_id=self.case_id,
                artifact_path=f'{self.experiment_path}/{filename}',
                artifact_type_name='VIDEO',
                attributes=details,
            )
            artifact = ac.collect()
            self.artifacts[file_type] = artifact
