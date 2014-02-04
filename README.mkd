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

To begin, start by copying the `hamper.conf.dist` into `hamper.conf` and adjusting
settings as necessary. Then all you need to do is run `docker build -t <yourname>/hamper .`
and you that will build a new Docker image to be used.

To use this container run `docker run -t -i <yourname>/hamper`, this will
startup hamper in the container.
