# These functions help you when things in irc interact with SQA
# When to use uen (unicode encode):
#   - Whenever you are pulling something *FROM THE DB* that will end up on the
#    wire to IRC

# When to use ude (unicode decode):
#   - Whenever you are putting something *INTO THE DB* that was user input from
#   IRC. Note: this applies to values used in any SQA statement, including
#   WHERE cluases


def uen(s):
    return s.encode('utf-8')


def ude(s):
    return s.decode('utf-8')
