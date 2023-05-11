import argparse
import logging
import pathlib
from typing import OrderedDict

from rich.logging import RichHandler
from rich.prompt import Prompt, IntPrompt

from pirogue_colander_connector.collectors.artifact import ArtifactCollector
from pirogue_colander_connector.collectors.experiment import ExperimentCollector
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
        'file',
        type=pathlib.Path)
    collect_artifact_group.add_argument(
        '-i',
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
        '-i',
        '--case_id',
        required=True,
        help='Specify the ID of the case you created in Colander'
    )

    args = arg_parser.parse_args()
    if not args.func:
        arg_parser.print_help()
        return

    if args.func == 'config':
        config = Configuration()
        config.write_configuration_file(args.base_url, args.api_key)
    elif args.func == 'collect-artifact':
        config = Configuration()
        client = config.get_colander_client()
        artifact_types: list[OrderedDict] = client.get_artifact_types()
        user_choices = []
        index = 0
        print('Select the type of the artifact you are about to upload:')
        for t in artifact_types:
            name = t.get('name')
            print(f'{index} - {name}')
            user_choices.append((t.get('id'), t.get('name'), t.get('short_name')))
            index += 1
        choice = IntPrompt.ask('Enter the number corresponding to the type you want to use')
        if 0 > choice or choice > len(user_choices):
            log.error('Invalid choice')
            return
        print(f'You have selected {user_choices[choice][1]}')
        ac = ArtifactCollector(args.file, args.case_id, user_choices[choice][2])
        ac.collect()
    elif args.func == 'collect-experiment':
        experiment_name = Prompt.ask('Enter the name of your experiment')
        ec = ExperimentCollector(args.path, args.case_id, experiment_name)
        ec.collect()
