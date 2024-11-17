import argparse
import logging
import pathlib

from rich.logging import RichHandler
from rich.prompt import Prompt

from pirogue_colander_connector.collectors.artifact import ArtifactCollector
from pirogue_colander_connector.collectors.experiment import ExperimentCollector
from pirogue_colander_connector.collectors.folder import FolderCollector
from pirogue_colander_connector.commands.configure import Configuration

log = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level='INFO',
        format='[%(name)s] %(message)s',
        handlers=[RichHandler(show_path=False, log_time_format='%X')]
    )
    arg_parser = argparse.ArgumentParser(prog='colander', description='PiRogue Colander connector')
    subparsers = arg_parser.add_subparsers(dest='func')
    # Config
    config_group = subparsers.add_parser(
        'config',
        help='Edit Colander configuration')
    config_group.add_argument(
        '-u',
        '--base_url',
        required=True,
        help='Specify the base URL of your Colander server'
    )
    config_group.add_argument(
        '-k',
        '--api_key',
        required=True,
        help='Specify your Colander API key'
    )
    # Collect artifact
    collect_artifact_group = subparsers.add_parser(
        'collect-artifact',
        help='Upload an artifact to Colander')
    collect_artifact_group.add_argument(
        'path',
        type=pathlib.Path,
        help='Specify the path of the file or folder you want to be uploaded to Colander'
    )
    collect_artifact_group.add_argument(
        '-c',
        '--case_id',
        required=True,
        help='Specify the ID of the case you created in Colander'
    )
    # Collect PiRogue experiment
    collect_experiment_group = subparsers.add_parser(
        'collect-experiment',
        help='Upload an entire PiRogue experiment to Colander')
    collect_experiment_group.add_argument(
        'path',
        type=pathlib.Path)
    collect_experiment_group.add_argument(
        '-c',
        '--case_id',
        required=True,
        help='Specify the ID of the case you created in Colander'
    )
    collect_experiment_group.add_argument(
        '-t',
        '--target_artifact',
        required=False,
        help='Specify the artifact you executed during this experiment',
        type=pathlib.Path
    )

    args = arg_parser.parse_args()
    if not args.func:
        arg_parser.print_help()
        return

    if args.func == 'config':
        config = Configuration()
        config.write_configuration_file(args.base_url, args.api_key)
    elif args.func == 'collect-artifact':
        if args.path.is_file():
            ac = ArtifactCollector(args.path, args.case_id)
            ac.collect()
        elif args.path.is_dir():
            fc = FolderCollector(args.path, args.case_id)
            fc.collect()
    elif args.func == 'collect-experiment':
        experiment_name = Prompt.ask('Enter the name of your experiment')
        ec = ExperimentCollector(args.path, args.case_id, experiment_name, target_artifact_path=args.target_artifact)
        ec.collect()
