import re
import urllib
import urllib2
import json

from hamper.interfaces import ChatPlugin


class Bitly(ChatPlugin):
    name = 'bitly'
    priority = 2

    # Regex is taken from:
    # http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    regex = ur"""
    (                       # Capture 1: entire matched URL
      (?:
        (?P<prot>https?://)     # http or https protocol
        |                       #   or
        www\d{0,3}[.]           # "www.", "www1.", "www2." ... "www999."
        |                           #   or
        [a-z0-9.\-]+[.][a-z]{2,4}/  # looks like domain name
                                    # followed by a slash
      )
      (?:                                  # One or more:
        [^\s()<>]+                         # Run of non-space, non-()<>
        |                                  # or
        \(([^\s()<>]+|(\([^\s()<>]+\)))*\) # balanced parens, up to 2 levels
      )+
      (?:                                  # End with:
        \(([^\s()<>]+|(\([^\s()<>]+\)))*\) # balanced parens, up to 2 levels
        |                                  # or
        [^\s`!()\[\]{};:'".,<>?]           # not a space or one of
                                           # these punct chars
      )
    )
    """

    def setup(self, loader):
        self.regex = re.compile(self.regex, re.VERBOSE | re.IGNORECASE | re.U)
        self.api_url = 'https://api-ssl.bitly.com/v3/shorten'
        self.username = loader.config['bitly']['login']
        self.api_key = loader.config['bitly']['api_key']
        # If an exclude value is found in the url
        # it will not be shortened
        self.excludes = ['imgur.com', 'gist.github.com', 'pastebin.com']
        # Make sure they've configured the bitly config values.
        try:
            self.username = loader.config['bitly']['login']
            self.api_key = loader.config['bitly']['api_key']
        except KeyError:
            print ('\nTo use the bitly plugin you need to set your bitly login'
                   '\nand api_key in your config file.\n'
                   'Example:\n'
                   'bitly:\n'
                   "    login: '123456789000'\n"
                   "    api_key: '1234678901234567890123467890123456'\n")
            quit()

    def message(self, bot, comm):
        match = self.regex.search(comm['message'])
        # Found a url
        if match:
            # base url isn't % encoded, python 2.7 doesn't do this well, and I
            # couldn't figure it out.
            long_url = match.group(0)

            # Only shorten urls which are longer than a bitly url (12 chars)
            if len(long_url) <= 12:
                return False

            # Don't shorten url's which are in the exclude list
            for item in self.excludes:
                if item in long_url.lower():
                    return False

            # Bitly requires a valid URI
            if not match.group('prot'):
                long_url = 'http://' + long_url

            # Bitly requires valid % encoded urls
            params = urllib.urlencode({'login': self.username,
                                       'apiKey': self.api_key,
                                       'longUrl': long_url})
            req = urllib2.Request(self.api_url, data=params)
            response = urllib2.urlopen(req)
            data = json.load(response)

            if data['status_txt'] == 'OK':
                bot.reply(comm, "{0[user]}'s shortened url is {1[url]}"
                          .format(comm, data['data']))

        # Always let the other plugins run
        return False
