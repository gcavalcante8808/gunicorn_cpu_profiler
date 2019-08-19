[![](https://images.microbadger.com/badges/image/gcavalcante8808/gunicorn_cpu_profiler.svg)](https://microbadger.com/images/gcavalcante8808/gunicorn_cpu_profiler "Get your own image badge on microbadger.com")
[![](https://images.microbadger.com/badges/version/gcavalcante8808/gunicorn_cpu_profiler.svg)](https://microbadger.com/images/gcavalcante8808/gunicorn_cpu_profiler "Get your own version badge on microbadger.com")
[![](https://images.microbadger.com/badges/commit/gcavalcante8808/gunicorn_cpu_profiler.svg)](https://microbadger.com/images/gcavalcante8808/gunicorn_cpu_profiler "Get your own commit badge on microbadger.com")

# Gunicorn Cpu Monitor

This is a simples project that aims to provide an ondemand cpu_profiler for gunicorn worker processes and its threads by using Uber [Pyflame](https://github.com/uber/pyflame) tools.

## How To use

Just spin a container pointing to the gunicorn container that will be profiled:

```
    docker run -it --rm -e FLAMECHARTS_FOLDER=/charts -v $(pwd)/charts:/charts --pid="container:gunicorn_container" gcavalcante8808/gunicorn_cpu_monitor
```

After a few seconds, some files with pattern "/<FLAMECHARTS_FOLDER>/proccess_<PID>.profile" will be dumped into the volume mounted on `FLAMECHARTS_FOLDER`.

These files can be viewed with Chrome Dev Tools Performance analizer (https://developers.google.com/web/tools/chrome-devtools/evaluate-performance).

## Using with Docker-compose

With a working docker-compose.yaml file, you can just create an `docker-compose.override.yaml` with the following statements:

```
version: <SAME_VERSION_OF_DOCKER_COMPOSE_DOT_YAML>

services:

  cpu_monitor:
    image: gcavalcante8808/gunicorn_cpu_profiler
    pid: "service:<GUNICORN_COMPOSE_SERVICE>"
    command: ["/usr/local/bin/dumb-init","python","gunicorn_cpu_monitor.py"]
    cap_add:
      - SYS_PTRACE
    environment:
      FLAMECHARTS_FOLDER: /charts
    volumes:
     - /my-folder:/charts
    depends_on:
      - <GUNICORN_COMPOSE_SERVICE>
```

Update `<GUNICORN_COMPOSE_SERVICE>` to point to your gunicorn service and `<SAME_VERSION_OF_DOCKER_COMPOSE_DOT_YAML>` to use the same version of your `docker-compose.yaml` original file,
otherwise docker-compose will return errors about the version.

For more information about docker-compose file override, take a look at `https://docs.docker.com/compose/extends`.

## Settings

The following environment variables can be used to tune or change program`s behaviour:

 * FLAMECHARTS_FOLDER: Folder where flamecharts json files will be created;
 * CPU_THRESHOLD: By Default, all processes that have more than 90 percent usage of a processor are profilled;
 * SCAN_INTERVAL: By Default, the scan for threads will occur every 60 seconds;
 * GUNICORN_PARENT_PID:  By Default, the cpu_monitor will try to use the first pid that is a child from pid `1`. This is a behaviour when you are using an supervisor or an minimal init system to initialize your gunicorn instance.


Author
------

Author: Gabriel Abdalla Cavalcante Silva (gabriel.cavalcante88@gmail.com)
