import json
import logging
import os.path
import pathlib
from pathlib import Path

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
    target_device: dict = None
    target_artifact_path: pathlib.Path = None
    artifacts = {}

    def __init__(self, experiment_path: pathlib.Path, case_id: str, experiment_name: str,
                 target_artifact_path: pathlib.Path = None):
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
        self.target_artifact_path = target_artifact_path
        if not experiment_path.exists() or not os.path.isdir(experiment_path):
            msg = f'{experiment_path} is not a directory'
            log.error(msg)
            raise Exception(msg)
        if not os.path.isfile(self.experiment_details_path):
            msg = f'{self.experiment_details_path} not found'
            log.error(msg)
            raise Exception(msg)

    def __ensure_file_exists(self, details: dict):
        filename: str = details.get('file')
        file_path = f'{self.experiment_path}/{filename}'
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            with open(file_path, mode='w') as out:
                if filename.endswith('.json'):
                    out.write('[]')
                else:
                    out.write('\n')

    def collect(self):
        log.info(f'Reading the experiment details from {self.experiment_details_path}')
        with open(self.experiment_details_path) as f:
            experiment_details = json.load(f)
        target_artifact = None
        if self.target_artifact_path:
            ta = ArtifactCollector(
                case_id=self.case_id,
                artifact_path=self.target_artifact_path,
            )
            target_artifact = ta.collect()
        for file_type, details in experiment_details.items():
            log.info(f'Dispatch collection of the {file_type} artifact')
            self.__ensure_file_exists(details)
            self.__dispatch_collection(file_type, details)
        pcap = self.artifacts.pop('network', None)
        socket_trace = self.artifacts.pop('socket_traces', None)
        sslkeylog = self.artifacts.pop('sslkeylog', None)
        crypto_traces = self.artifacts.pop('crypto_traces', None)
        screen = self.artifacts.pop('screen', None)
        experiment = self.colander_client.create_pirogue_experiment(
            name=self.experiment_name,
            case=self.colander_client.get_case(self.case_id),
            pcap=pcap,
            socket_trace=socket_trace,
            sslkeylog=sslkeylog,
            extra_params={
                'screencast': screen,
                'aes_trace': crypto_traces,
                'target_device': self.target_device,
                'target_artifact': target_artifact,
                'extra_files': list(self.artifacts.values())
            }
        )
        experiment_id = experiment.get('id')
        log.info(f'Your experiment {self.experiment_name} [#{experiment_id}] has been successfully created!')

    def __create_device(self, device_details: dict):
        brand = device_details.get('brand', 'Generic')
        model = device_details.get('model', 'no model')
        imei = device_details.get('imei', 'xxx')
        device_name = f'{brand} - {model} ({imei})'
        case = self.colander_client.get_case(self.case_id)
        devices = self.colander_client.get_devices(case=case, name=device_name)
        if devices:
            device = devices[0]
        else:
            device = self.colander_client.create_device(
                name=device_name,
                case=case,
                device_type=self.colander_client.get_device_type_by_short_name('MOBILE'),
                extra_params={
                    'attributes': device_details
                }
            )
        return device

    def __dispatch_collection(self, file_type: str, details: dict):
        filename = details.pop('file')
        file_path = Path(f'{self.experiment_path}/{filename}')
        if not file_path.exists() or not file_path.is_file():
            msg = f'{file_path} not found'
            log.error(msg)
            raise Exception(msg)
        if file_type == 'network':
            ac = ArtifactCollector(
                case_id=self.case_id,
                artifact_path=file_path,
                artifact_type_name='PCAP',
                attributes=details,
            )
            artifact = ac.collect()
            self.artifacts[file_type] = artifact
        elif file_type == 'socket_traces':
            ac = ArtifactCollector(
                case_id=self.case_id,
                artifact_path=file_path,
                artifact_type_name='SOCKET_T',
                attributes=details,
            )
            artifact = ac.collect()
            self.artifacts[file_type] = artifact
        elif file_type == 'crypto_traces':
            ac = ArtifactCollector(
                case_id=self.case_id,
                artifact_path=file_path,
                artifact_type_name='CRYPTO_T',
                attributes=details,
            )
            artifact = ac.collect()
            self.artifacts[file_type] = artifact
        elif file_type == 'sslkeylog':
            ac = ArtifactCollector(
                case_id=self.case_id,
                artifact_path=file_path,
                artifact_type_name='SSLKEYLOG',
                attributes=details,
            )
            artifact = ac.collect()
            self.artifacts[file_type] = artifact
        elif file_type == 'screen':
            ac = ArtifactCollector(
                case_id=self.case_id,
                artifact_path=file_path,
                artifact_type_name='VIDEO',
                attributes=details,
            )
            artifact = ac.collect()
            self.artifacts[file_type] = artifact
        elif file_type == 'device':
            with file_path.open('r') as f:
                device_details = json.load(f)
            self.target_device = self.__create_device(device_details)
        else:
            ac = ArtifactCollector(
                case_id=self.case_id,
                artifact_path=file_path,
                artifact_type_name='OTHER',
                attributes=details,
            )
            artifact = ac.collect()
            self.artifacts[file_type] = artifact

