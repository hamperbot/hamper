from pyquery import PyQuery as pq
import requests

from hamper.interfaces import ChatCommandPlugin, Command


class NoData(Exception):
    pass


class Weather(ChatCommandPlugin):
    """What's the weather?"""
    name = 'weather'
    priority = 2

    class Weather(Command):
        name = 'weather'
        regex = '^weather\s+(.*)'
        api_url = 'http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?query={0}'  # noqa

        def command(self, bot, comm, groups):
            query = groups[0].strip()
            resp = requests.get(self.api_url.format(query))
            dom = pq(resp.content)
            if not resp.status_code == 200:
                bot.reply(
                    comm,
                    "Error while looking up weather: saw status code %s" %
                    resp.status_code
                )
                return False

            try:
                location = dom('display_location full')[0].text
                if location == ', ':
                    raise NoData()
                cur_weather = dom('weather')[0].text
                temp = dom('temperature_string')[0].text
                relative_humidity = dom('relative_humidity')[0].text
                station = dom('station_id')[0].text
            except (IndexError, NoData):
                bot.reply(comm, "Couldn't find weather for {0}".format(query))
                return False

            weather_resp = (
                "The reported weather for {0} ({1}) is {2} -- "
                "{3} with a relative humidity of {4}"
            ).format(location, station, cur_weather, temp, relative_humidity)

            bot.reply(comm, weather_resp)

            return False


weather = Weather()
