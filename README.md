Hamper is an IRC bot to amuse us.


Quick Start
-----------

```shell
$ git clone https://github.com/mythmon/hamper
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
# replace /host/path/to/db with where you want hamper's database file to be stored
$ HAMPER=$(docker run -d -v /host/path/to/db:/var/lib/hamper --env-file ./hamper.env <yourname>/hamper)
````

This would create a folder at `/host/path/to/db/` on your computer, and if
you're using the default config, you'll find a file `hamper.db` in that folder.

Then to stop the container type `docker stop $HAMPER`. To see logs of the
running container use `docker logs $HAMPER`. You can get the id by using
`docker ps` or `echo $HAMPER`. Refer to the [docker docs][docker] for more
usage detail details.

[docker]: http://docs.docker.io/en/latest/
