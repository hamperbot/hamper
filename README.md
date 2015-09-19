Hamper is an IRC bot to amuse us.


Quick Start
-----------

```shell
$ git clone https://github.com/hamperbot/hamper
$ cd hamper
$ virtualenv venv
$ source venv/bin/activate
$ python setup.py develop
$ cp hamper.conf.dist hamper.conf
$ vim hamper.conf
$ hamper
```


Configuration
=============
Make a file named `hamper.conf`. This should be a YAML file containing these
fields:

-   `nickname`
-   `channels`
-   `server`
-   `port`
-   `db` - A database URL as described [here][dburl]

For an example check out `hamper.conf.dist`.


Plugin Development
==================
Read `hamper/plugins/friendly.py`.
To declare a plugin so that it can be used you need to edit *your* plugin's
`setup.py` and add something like the following lines:
```python
setup(
    name='YOUR_PLUGIN',
    # ...More lines here...
    entry_points = {
        'hamperbot.plugins': [
                'plugin_name = module.import.path.to.plugin:PluginClass',
        ],
    },
    # ...Possibly more lines here too...
```
For the new plugin system you no longer need to create an instance of each one
at the bottom.
Once you have declared your class as a plugin you need to install it with
`setup.py`:
```sh
$ python setup.py develop

```
This is so that setuptools can advertise your plugins to Hamper. Hamper uses
setuptools to determine what plugins are available.
Note that if you change your `setup.py`, you'll have to repeat those last two
steps. However, you probably won't have to rebuild the package every time you
change your plugin.

Testing
=======

Hamper uses Twisted's [Trial][] unit testing system, which is an extension of
Python's unittest module. To run the tests, execute `trial hamper' in the top
level directory of hamper.

Using Docker
------------

**requires Docker > 1.3**

This already assumes you've got Docker configured and installed on your system.

To begin you need to build the Docker image for Hamper: `docker build -t hamper .`

Now we can start the container using that image, but first start by copying the
`hamper.env.dist` into `hamper.env` and adjusting settings as necessary.

Now all we need to do is start the container by telling where to read our
settings.

```shell
docker run --env-file ./hamper.env --name hamper hamper
```

This *creates and starts* the container. If you want to re-use the same
database then you should use `docker start hamper` to just *start* an existing
container.  If you want to create a new container with a new config, but the
old database use `docker run --env-file ./hamper.env --volumes-from hamper
--name hamper-new hamper` to create a container with a new name, but import the
volume containing the database from the old container.


This is great and all, but perhaps you want to hack on Hamper and use Docker
simply to run Hamper with your current directory. Here's how to do that:

```shell
docker run -it --env-file ./hamper.env -v $(pwd):/hamper hamper bash
```

This will mount the directory located at `$(pwd)` on the host running Docker
in place of the Hamper project in your container.  When you make changes to the
code, they'll be seen in the container. The reason we run bash is so you can
easily stop and restart the bot with the `hamper` command, however you can
leave out the `bash` command at the end and just stop and start the container.

Then to stop the container type `docker stop hamper`. To start it back up type
`docker start hamper` To see logs of the running container use `docker logs hamper`.
Refer to the [docker docs][docker] for more usage details.

[docker]: http://docs.docker.io/en/latest/
[dburl]: http://www.sqlalchemy.org/docs/core/engines.html#sqlalchemy.create_engine
[trial]: http://twistedmatrix.com/trac/wiki/TwistedTrial
