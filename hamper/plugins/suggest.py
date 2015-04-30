from hamper.interfaces import ChatCommandPlugin, Command

import requests
import json


class Suggest(ChatCommandPlugin):
    name = 'suggest'
    priority = 2

    short_desc = 'suggest <something> - suggest a phrase given something'
    long_desc = (
        'suggest <number> <something> - suggest the <number>th phrase given '
        'something\n'
        'This pluggin is similar to the suggestion engine found on a smart '
        'phone.\n'
        'You can use it to correct the spelling of difficult words.\n'
    )

    search_url = "http://suggestqueries.google.com/complete/search?client=firefox&q={query}"  # noqa

    def setup(self, loader):
        super(Suggest, self).setup(loader)

    class Suggest(Command):
        name = 'suggest'
        regex = '^suggest\s*(\d+)?\s+(.*)'

        def command(self, bot, comm, groups):
            query = groups[1]
            s_num = int(groups[0]) if groups[0] else 1

            resp = requests.get(self.plugin.search_url.format(query=query))
            if resp.status_code != 200:
                raise Exception(
                    "Suggest Error: A non 200 status code was returned"
                )

            gr = json.loads(resp.content)
            o_query, suggestions = gr
            if not suggestions:
                bot.reply(comm, "No suggestions found.")
            else:
                try:
                    bot.reply(
                        comm, "%s (%s/%s)" % (
                            suggestions[s_num - 1], s_num, len(suggestions)
                        )
                    )
                except IndexError:
                    bot.reply(
                        comm, "Suggestion number #%s does not exist" % s_num
                    )

            # Always let the other plugins run
            return False
