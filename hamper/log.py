import logging


class ColorizingStreamHandler(logging.StreamHandler):
    """StreamHandler that colorizes log out based on level.

     Copyright (C) 2010-2012 Vinay Sajip. All rights reserved. Licensed under
     the new BSD license. From https://gist.github.com/758430.

     """

    # color names to indices
    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
    }

    level = logging.DEBUG

    # levels to (background, foreground)
    level_map = {
        logging.DEBUG: (None, 'blue'),
        logging.INFO: (None, None),
        logging.WARNING: (None, 'yellow'),
        logging.ERROR: (None, 'red'),
        logging.CRITICAL: ('red', 'white'),
    }
    csi = '\x1b['
    reset = '\x1b[0m'

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if not self.is_tty:
                stream.write(message)
            else:
                self.output_colorized(message)
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def output_colorized(self, message):
        self.stream.write(message)

    def colorize(self, message, record):
        if record.levelno in self.level_map:
            bg, fg = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))
            if params:
                message = ''.join((self.csi, ';'.join(params),
                                   'm', message, self.reset))
        return message

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            # Don't colorize any traceback
            parts = message.split('\n', 1)
            parts[0] = self.colorize(parts[0], record)
            message = '\n'.join(parts)
        return message


config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(levelname)s %(module)s %(message)s',
        }
    },
    'filters': {},
    'handlers': {
        'color': {
            'level': 'DEBUG',
            'class': 'hamper.log.ColorizingStreamHandler',
            'formatter': 'default',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'hamper': {
            'handlers': ['color'],
            'propogate': True,
            'level': 'DEBUG',
        },
        'bravo': {
            'handlers': ['color'],
            'propogate': True,
            'level': 'DEBUG',
        }
    }
}


def setup_logging():
    h = logging.getLogger('hamper')
    h.setLevel(logging.DEBUG)
    h.addHandler(ColorizingStreamHandler())
