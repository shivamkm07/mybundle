# Dapr Installer Bundle
Dapr Installer Bundle contains CLI, runtime and dashboard packaged together. This eliminates the need to download binaries as well as docker images when initializing Dapr locally.

## Setup
Each release of Dapr Installer Bundle includes various OSes and architectures. These packages can be manually downloaded and used to initialize dapr locally.

1. Download the [Dapr Installer Bundle](https://github.com/dapr/installer-bundle/releases)
2. Unpack it (e.g. daprbundle_linux_amd64.tar.gz, daprbundle_windows_amd64.zip)
3. Move to the bundle directory and use the init command to initialize dapr:

### Initialize Dapr

**Windows**
``` powershell
cd .\daprbundle
.\dapr init --from-dir .
```

**Linux**
``` bash
cd ./daprbundle
./dapr init --from-dir .

> if you run your docker cmds with sudo, you need to use "**sudo ./dapr init**"
```

**MacOS**
``` bash
cd ./daprbundle
./dapr init --from-dir .
```

Output should look like as follows:
```bash
  Making the jump to hyperspace...
ℹ️  Installing runtime version latest
↘  Extracting binaries and setting up components... Loaded image: daprio/dapr:$version
✅  Extracting binaries and setting up components...
✅  Extracted binaries and completed components set up.
ℹ️  daprd binary has been installed to $HOME/.dapr/bin.
ℹ️  dapr_placement container is running.
ℹ️  Use `docker ps` to check running containers.
✅  Success! Dapr is up and running. To get started, go here: https://aka.ms/dapr-getting-started
```
> Note: To see that Dapr has been installed successfully, from a command prompt run the `docker ps` command and check that the `daprio/dapr:$version` container is up and running.

This step creates the following defaults:

1. Dapr runtime and dashboard binaries are installed under $HOME/.dapr/bin for Mac, Linux and %USERPROFILE%\.dapr\bin for Windows.
2. components folder which is later used during `dapr run` unless the `--components-path` option is provided. For Linux/MacOS, the default components folder path is `$HOME/.dapr/components` and for Windows it is `%USERPROFILE%\.dapr\components`.
3. component files in the components folder called `pubsub.yaml` and `statestore.yaml`.
4. default config file `$HOME/.dapr/config.yaml` for Linux/MacOS or for Windows at `%USERPROFILE%\.dapr\config.yaml` to enable tracing on `dapr init` call. Can be overridden with the `--config` flag on `dapr run`.

> Note: To emulate *online* dapr initialization, using `dapr init`, you can also download redis/zipkin containers as follows:
```
1. docker run --name "dapr_zipkin" --restart always -d -p 9411:9411 openzipkin/zipkin
2. docker run --name "dapr_redis" --restart always -d -p 6379:6379 redislabs/rejson
```

### Slim Init
Alternatively to the above, to have the CLI not install any default configuration files or run Docker containers, use the `--slim` flag with the init command. Only Dapr binaries will be installed.


**Windows**
``` powershell
cd .\daprbundle
.\dapr init --from-dir . --slim
```

**Linux**
``` bash
cd ./daprbundle
./dapr init --from-dir . --slim
```

**MacOS**
``` bash
cd ./daprbundle
./dapr init --from-dir . --slim
```

Output should look like this:
```bash
⌛  Making the jump to hyperspace...
ℹ️  Installing runtime version latest
↙  Extracting binaries and setting up components... 
✅  Extracting binaries and setting up components...
✅  Extracted binaries and completed components set up.
ℹ️  daprd binary has been installed to $HOME.dapr/bin.
ℹ️  placement binary has been installed to $HOME/.dapr/bin.
✅  Success! Dapr is up and running. To get started, go here: https://aka.ms/dapr-getting-started
```

>Note: When initializing Dapr with the `--slim` flag only the Dapr runtime binary and the placement service binary are installed. An empty default components folder is created with no default configuration files. During `dapr run` user should use `--components-path` to point to a components directory with custom configurations files or alternatively place these files in the default directory. For Linux/MacOS, the default components directory path is `$HOME/.dapr/components` and for Windows it is `%USERPROFILE%\.dapr\components`.

To install Dapr CLI for further use, copy `daprbundle/dapr` binary to the desired location:
   * For Linux/MacOS - `/usr/local/bin`
   * For Windows, create a directory and add this to your System PATH. For example create a directory called `c:\dapr` and add this directory to your path, by editing your system environment variable.