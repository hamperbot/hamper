from hamper.interfaces import ChatCommandPlugin, Command

try:
    # Python 2
    import HTMLParser
    html = HTMLParser.HTMLParser()
except ImportError:
    # Python 3
    import html.parser
    html = html.parser.HTMLParser()

import re
import requests
import json


class Lookup(ChatCommandPlugin):
    name = 'lookup'
    priority = 2

    short_desc = 'lookup <something> - look something up'
    long_desc = ('lookup and cite <something> - look something up and cite a '
                 'source\n')

    # Inspired by http://googlesystem.blogspot.com/2009/12/on-googles-unofficial-dictionary-api.html # noqa
    search_url = "http://www.google.com/dictionary/json?callback=dict_api.callbacks.id100&q={query}&sl=en&tl=en&restrict=pr%2Cde&client=te"  # noqa

    def setup(self, loader):
        super(Lookup, self).setup(loader)

    class Lookup(Command):
        name = 'lookup'
        regex = '^(lookup\s+and\s+cite|lookup)\s*(\d+)?\s+(.*)'

        def command(self, bot, comm, groups):
            lookup_type = groups[0]
            def_num = int(groups[1]) if groups[1] else 1
            query = groups[2]

            resp = requests.get(self.plugin.search_url.format(query=query))
            if resp.status_code != 200:
                raise Exception(
                    "Lookup Error: A non 200 status code was returned"
                )

            # We have actually asked for this cruft to be tacked onto our JSON
            # response. When I tried to remove the callback parameter from the
            # URL the api broke, so I'm going to leave it. Put it down, and
            # walk away...
            # Strip off the JS callback
            gr = resp.content.strip('dict_api.callbacks.id100(')
            gr = gr.strip(',200,null)')

            gr = gr.replace('\\x', "\u00")  # Google uses javascript JSON crap
            gr = json.loads(gr)

            if 'primaries' in gr:
                entries = gr['primaries'][0]['entries']
            elif 'webDefinitions' in gr:
                entries = gr['webDefinitions'][0]['entries']
            else:
                bot.reply(comm, "No definition found")
                return False

            seen = 0
            definition = None
            url = None
            for entry in entries:
                if not entry['type'] == 'meaning':
                    continue

                for term in entry['terms']:
                    if term['type'] == 'url':
                        url = re.sub('<[^<]+?>', '', term['text'])
                    else:
                        seen += 1
                        if not definition and seen == def_num:
                            definition = term['text']

            if not definition or def_num > seen:
                bot.reply(
                    comm,
                    "Looks like there might not be %s definitions" % def_num
                )
            else:
                bot.reply(
                    comm, "%s (%s/%s)" % (
                        html.unescape(definition), def_num, seen
                    )
                )
                if 'cite' in lookup_type:
                    if url:
                        bot.reply(comm, html.unescape(url))
                    else:
                        bot.reply(comm, '[No citation]')

            # Always let the other plugins run
            return False
