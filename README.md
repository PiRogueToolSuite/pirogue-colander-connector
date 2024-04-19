<div align="center">
<img width="60px" src="https://pts-project.org/android-chrome-512x512.png">
<h1>Colander connector for PiRogue</h1>
<p>
CLI interface to transfer data from the PiRogue to Colander. Have a look to our guides to <a href="https://pts-project.org/guides/" alt="Learn more about PiRogue">learn more how to use the PiRogue</a>.
</p>
<p>
License: GPLv3
</p>
<p>
<a href="https://pts-project.org">Website</a> | 
<a href="https://pts-project.org/docs/colander/overview/">Documentation</a> | 
<a href="https://discord.gg/qGX73GYNdp">Support</a>
</p>
</div>


# Colander connector for PiRogue
CLI interface to transfer data from the PiRogue to Colander.

## Install the connector
This connector is provided as a Debian package and is not installed by default. To install it, run the following command on your PiRogue:
```
sudo apt update
sudo apt install pirogue-colander-connector
```

## Configure the connector
Once installed, the first step before using it to collect artifacts or PiRogue experiments is to configure it by specifying both Colander base URL and your API key. To do so, run the following command on your PiRogue:

```
pirogue-colander config -u "<URL of your Colander server>" -k "<your Colander API key>"
```

## Collect a single artifact/file
To upload an artifact/file to your Colander server, run the following command:
```
pirogue-colander collect-artifact -c "<destination case ID>" <path of the file to be uploaded>
```

## Collect a PiRogue experiment
A PiRogue experiment is the output of the following commands:
* `pirogue-intercept-single`
* `pirogue-intercept-gated`

The command listed above generate a directory containing multiple files. To upload the entire experiment, use the following command on your PiRogue:

```
pirogue-colander collect-experiment -c "<destination case ID>" <path to the directory containing the outputs your experiment> 
```

Alternatively, you can also specify the artifact that has been executed during this experiment (usually an APK or a XAPK)

```
pirogue-colander collect-experiment -c "<destination case ID>" -t <path to the target artifact/file> <path to the directory containing the outputs your experiment> 
```