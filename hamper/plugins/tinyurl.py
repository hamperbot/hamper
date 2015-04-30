import re
import requests

from hamper.interfaces import ChatPlugin


class Tinyurl(ChatPlugin):
    name = 'tinyurl'
    priority = 0

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
        self.api_url = 'http://tinyurl.com/api-create.php?url={0}'
        self.config = loader.config.get('tinyurl', {})

        defaults = {
            'excluded-urls': ['imgur.com', 'gist.github.com', 'pastebin.com'],
            'min-length': 40,
        }
        for key, val in defaults.items():
            self.config.setdefault(key, val)

    def message(self, bot, comm):
        match = self.regex.search(comm['message'])
        # Found a url
        if match:
            long_url = match.group(0)

            # Only shorten urls which are longer than a tinyurl url
            if len(long_url) < self.config['min-length']:
                return False

            # Don't shorten url's which are in the exclude list
            for item in self.config['excluded-urls']:
                if item in long_url.lower():
                    return False

            # tinyurl requires a valid URI
            if not match.group('prot'):
                long_url = 'http://' + long_url

            resp = requests.get(self.api_url.format(long_url))
            data = resp.content

            if resp.status_code == 200:
                bot.reply(
                    comm,
                    "{0}'s shortened url is {1}" .format(comm['user'], data)
                )
            else:
                bot.reply(
                    comm, "Error while shortening URL: saw status code %s" %
                    resp.status_code
                )

        # Always let the other plugins run
        return False
