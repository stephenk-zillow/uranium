"""
Support the following:

* when instantiating a buildout plugin, pass in:
  * (<buildout>, <name of section>, <options passed into section>)

* buildout class must support:
  buildout['buildout']['directory'] == root buildout directory

* must catch zc.builout.UserError (raised when there is an error with user input)

"""
from .compat import DictMixin
import zc.buildout
import logging

LOGGER = logging.getLogger(__name__)


class BuildoutAdapter(DictMixin):
    """
    a class that acts like a buildout object,
    to support buildout recipes.
    """

    def __init__(self, uranium, classloader):
        self._uranium = uranium  # a Uranium instance
        self._classloader = classloader

    def get_part_instance(self, part):
        """ get an instantiated plugin for the part name specified """
        cls = self._get_recipe_class(part.get('recipe'))
        return cls(self, part.name, part)

    @staticmethod
    def install_part(self, part):
        try:
            part.install()
        except zc.buildout.UserError as e:
            LOGGER.error(str(e))

    def __getitem__(self, key):
        if key == "buildout":
            return self._buildout()

    def __setitem__(self, key):
        pass

    def __delitem__(self, key):
        pass

    def _buildout(self):
        """ return a buildout """
        return {
            'directory': self._uranium.root
        }
