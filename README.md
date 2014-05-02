Hamper is an IRC bot to amuse us.


Quick Start
-----------

```shell
$ git clone https://github.com/hamperbot/hamper
$ cd hamper
$ virtualenv venv
$ source venv/bin/activate
$ python setup.py install
$ cp hamper.conf.dist hamper.conf
$ vim hamper.conf
$ ./scripts/hamper
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

[dburl]: http://www.sqlalchemy.org/docs/core/engines.html#sqlalchemy.create_engine

Plugin Development
==================
Read `hamper/plugins/friendly.py`. Add a file to `hamper/plugins`, and write
plugins in it. Don't forget to create an instance of each one at the bottom.


Using Docker
------------

This already assumes you've got docker configured and installed on your system.

To begin you need to build the docker image for hamper: `docker build -t <yourname>/hamper .`

Now we can start the container using that image, but first start by copying the
`hamper.env.dist` into `hamper.env` and adjusting settings as necessary.

Now all we need to do is start the container by telling where to read our
settings, and we should also create a volume so that if we're using a sqlite,
it database will exist after the container gets stopped.


````shell
# replace ~/hamper_db with where you want hamper's database file to be stored
docker run -d -v ~/hamper_db:/var/lib/hamper --env-file ./hamper.env --name hamper <yourname>/hamper
````

This would create a folder at `~/hamper_db` on your computer, and if you're
using the default config, you'll find a sqlite file `hamper.db` in that folder.

This is great and all, but perhaps you want to hack on hamper and use docker.
Here's how to do that:

````shell
docker run -it --env-file ./hamper.env - /path/to/hamper:/hamper -v ~/hamper_db:/var/lib/hamper --name hamper ecnahc515/hamper bash
````

This will open up a bash prompt and mount your hamper project repo (in this
example at `/path/to/hamper`) in place of the hamper project in your container.
When you make changes to the code, they'll be seen in the container. The reason
we run bash is so you can easily stop and restart the bot with the hamper
command, however you can leave out the `bash` command at the end and just stop
and start the container.

Then to stop the container type `docker stop hamper`. To start it back up type
`docker start hamper` To see logs of the running container use `docker logs hamper`.
Refer to the [docker docs][docker] for more usage detail details.

[docker]: http://docs.docker.io/en/latest/
