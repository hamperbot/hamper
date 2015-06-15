import requests
import json

from hamper.interfaces import ChatCommandPlugin, Command


class Timez(ChatCommandPlugin):
    name = 'timez'
    priority = 2

    def setup(self, loader):
        try:
            self.api_key = loader.config['timez']['api-key']
        except (KeyError, TypeError):
            self.api_key = None

        api_url = "http://api.worldweatheronline.com/free/v1/tz.ashx"
        self.api_url = "%s?key=%s&q=%%s&format=json" % (api_url, self.api_key)
        super(Timez, self).setup(loader)

    class Timez(Command):
        ''' '''
        name = 'timez'
        regex = '^timez (.*)'

        long_desc = short_desc = (
            "timez <something> - Look up time for [ZIP code | City, State (US Only) | "
            "City Name, State, Country | City Name, Country | "
            "Airport Code | IP "
        )

        def command(self, bot, comm, groups):
            if not self.plugin.api_key:
                bot.reply(
                    comm, "This plugin is missconfigured. Its missing an API "
                    "key. Go register one at "
                    "http://developer.worldweatheronline.com/apps/register"
                )
                return

            query = comm['message'].strip('timez ')
            resp = requests.get(self.plugin.api_url % query)
            if resp.status_code != 200:
                bot.reply(comm, "Error: A non 200 status code was returned")

            jresp = json.loads(resp.text)

            try:
                tz = jresp['data']['time_zone'][0]
                bot.reply(
                    comm,
                    "For %s, local time is %s at UTC offset %s" % (
                        query, tz['localtime'], tz['utcOffset']
                    )
                )
            except KeyError:
                bot.reply(
                    comm, "Sorry, the internet didn't understand your request."
                )

            # Always let the other plugins run
            return False
