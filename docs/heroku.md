# Hamper on Heroku

Hamper was, literally, designed to run on [Heroku][], and tries to follow the
[12 factors][12].

[Heroku]: http://heroku.com
[12]: http://12factor.net/

## Heroku in a Nutshell

Heroku is Process-as-a-Service provider, or PaaS. Given an application as a git
push, it builds and runs the service. It has a free tier which Hamper handily
fits in. There is no need to use the paid-tier of Heroku for this.

## Setup

Most of these steps could also be done in the web interface, but that is harder
to write docs about. Run these commands from inside the hamper repository.

1. [Get a Heroku account](https://id.heroku.com/signup/www-home-top).

2. [Install the Heroku toolbelt](https://toolbelt.heroku.com/standalone).

3. Log in to the toolbelt.
   
   ```bash
   $ heroku auth:login
   ```

4. Create an application. This also includes the database that will be needed.

   ```bash
   $ heroku apps:create hamper-mythmon-test --addons heroku-postgresql
   ```

5. Set some configuration options. You can set multiple at a time, or one at a
   time. Since the app isn't running, it doesn't matter. In the future, you'll
   want to make all desired changes at once, as this triggers an application
   restart.

   ```bash
   $ heroku config:set nickname=my_hamper
   $ heroku config:set plugins='[karma,help,sed]'
   $ heroku config:set server=irc.freenode.net port=6697 ssl=true
   $ heroku config:set channels='["#hamper-testing"]'
   $ heroku config:set PYTHON_EXTRA_REQS=psycopg2==2.5.1
   ```

   Remember that environment variables are parsed as YAML if they are valid as
   such, which is how to specify things like lists of plugins and channels.
   Be careful with `#` in channel names: YAML takes that as a comment, and you
   also have to deal with shell quoting.

6. Push the code to Heroku. Up until this point, Heroku has had no idea what
   code we have been talking about. Note that when you created the app, 
   Heroku created a git remote named `heroku` for you to push to.

   ```bash
   git push heroku master
   ```

   Make sure to commit any changes you may have made to the code, or they won't
   get deployed to Heroku.

6. Start Hamper. This instructs Heroku to run 1 `irc` *dyno* (one Heroku
   process). It is free to run a single dyno, and that is all that
   Hamper needs. Heroku knows what an `irc` process is because it is defined in
   the file named `Procfile`.

   ```bash
   $ heroku ps:scale irc=1
   ```

7. Check the logs. This is not strictly necessary, but it is good to know
   in case anything goes wrong.

   ```bash
   $ heroku logs -t
   ```

   (Press ctrl+c to exit)

Heroku is a much more powerful tool than how it is used here, capable of
hosting complex applications. This, however, is all we need for Hamper.

> #### Note: Extra dependencies
> This is technically a violation of 12 Factor, but it makes hacking on
> hamper much easier. All of the core dependencies for Hamper are listed
> in `requirements.txt`, but to use a Postgresql database, like we did
> above, you also need the Postgresql python drive, psycopg2.
>
> Hamper uses a modified Python buildpack that will install extra Python
> requirements listed in the `$PYTHON_EXTRA_REQS` argument. This gets
> appended directly to `requirements.txt` during the build phase, so
> newlines are needed for any more requirements. This is the mechanism
> by which you could run [external plugins][extplug] on Heroku.

[extplug]: [externalplugins.md]


## Theory

Heroku is based on a theory called "The 12-Factor App". It lists 12 best
practices for scalable maintainable apps. Hamper tries to follow these.


### I. Codebase
> One codebase tracked in revision control, many deploys

The master branch of Hamper is always eligible to push to Heroku. No
extra files need to be checked in or edited.

### II. Dependencies
> Explicitly declare and isolate dependencies

All of Hamper's core dependencies are listed in `requirements.txt`, which
Heroku reads. Sometimes extra requirements are required, which are dealt
with as explained above.

### III. Config
> Store config in the environment

Hamper will pull configuration from enviroment variables, as detailed at
the end of [the config docs][config].

[config]: config.md

### IV. Backing Services
> Treat backing services as attached resources

Hamper uses a database, and it can read the config for that database from
environment variables, such as the one Heroku provides.

### V. Build, release, run
> Strictly separate build and run stages

Heroku forces this pattern, so Hamper works with it.

### VI. Processes
> Execute the app as one or more stateless processes

Hamper most follows this pattern, as it tries to store most state in the
database. Restarting Hamper in place loses very little state, and is
generally safe to do. Some plugins may try and store state in memory,
such as the sed plugin.

### VII. Port binding
> Export services via port binding

Hamper doesn't bind any ports.

### VIII. Concurrency
> Scale out via the process model

Hamper doesn't scale, hasn't shown any need to, nor am I sure how to
scale out an IRC bot.

### IX. Disposability
> Maximize robustness with fast startup and graceful shutdown

Since Hamper is a single process that is intended to run all the time,
this doesn't apply much. However, startup is quick and shutdown is safe.

### X. Dev/prod parity
> Keep development, staging, and production as similar as possible

Hamper deploys roughly the same in production as the recommended set up process.

### XI. Logs
> Treat logs as event streams

Hamper could log better, but when it does log it does so in a Heroku-friendly
way.

### XII. Admin processes
> Run admin/management tasks as one-off processes

Hamper doesn't have an admin tasks yet.

