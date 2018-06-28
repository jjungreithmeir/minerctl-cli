# minerctl CLI tool

This small tool is used to remotely configure or debug a mining container.
Simply install the tool with `pip` (if you have added the python packages to your `PATH`) or use a tool like [pipsi](https://github.com/mitsuhiko/pipsi).

 To use the tool simply enter `minerctl` and follow the instructions. First you need to set the backend address & port via the `-b` option. Additionally, you must pass the location of your private key file with the `-k` option, in order for the tool to correctly sign the requests. The respective public key has to be stored in the backend (for more information view the backend documentation in the repository).

 After this short setup process, you should be able to query information with `minerctl` and the appropriate handles (use `-h` or `--help` for more information) or update the miner configs with `minerctl set` and the respective options.
