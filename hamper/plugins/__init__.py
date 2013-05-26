# This allows twisted.plugin to autodiscover plugins in this module.
# See: https://twistedmatrix.com/documents/12.2.0/core/howto/plugin.html
from twisted.plugin import pluginPackagePaths
__path__.extend(pluginPackagePaths(__name__))
__all__ = []
