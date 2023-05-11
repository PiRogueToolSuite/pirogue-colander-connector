from setuptools import find_packages, setup

install_required = [
    'colander-client',
    'rich'
]

setup(
    name="pirogue-colander-connector",
    version="1.0.0",
    author="U+039b",
    author_email="hello@pts-project.org",
    description="CLI interface to transfer data from the PiRogue to Colander",
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
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: OS Independent",
    ],
)
