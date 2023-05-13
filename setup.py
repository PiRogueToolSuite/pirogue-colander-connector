from setuptools import find_packages, setup
from pathlib import Path

pwd = Path(__file__).parent
long_description = (pwd / "README.md").read_text()

install_required = [
    'colander-client',
    'rich==9.11.0'
]

setup(
    name="pirogue-colander-connector",
    version="1.0.1",
    author="U+039b",
    author_email="hello@pts-project.org",
    description="CLI interface to transfer data from the PiRogue to Colander",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/PiRogueToolSuite/pirogue-colander-connector",
    install_requires=install_required,
    packages=find_packages(),
    zip_safe=True,
    entry_points={
        "console_scripts": [
            "pirogue-colander = pirogue_colander_connector.commands.entrypoint:main"
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3',
        'Natural Language :: English',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
