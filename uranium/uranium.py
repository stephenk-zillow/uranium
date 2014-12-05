import logging
import os
from .classloader import ClassLoader
from .config import load_config_from_file
from .pip_manager import PipManager
from .buildout_adapter import BuildoutAdapter
from .phases import (AFTER_EGGS, BEFORE_EGGS)

LOGGER = logging.getLogger(__name__)


class UraniumException(Exception):
    pass


class Uranium(object):

    def __init__(self, file_path):
        self._root = os.path.abspath(os.curdir)
        self._config = load_config_from_file(file_path)

        self._pip = PipManager(index_urls=self._config.indexes)
        self._classloader = ClassLoader(self._pip)

        self._buildout = BuildoutAdapter(self)

        errors = self._config.validate()
        if errors:
            for error in errors:
                LOGGER.error(error)
            raise UraniumException("uranium.yaml is not valid.")

    @property
    def root(self):
        return self._root

    @property
    def phases(self):
        return self.config.get('phases', {})

    def run(self):
        self._run_phase(BEFORE_EGGS)
        self._install_eggs()
        self._run_phase(AFTER_EGGS)

    def run_phase(self, phase):
        part_names = self.phases.get(phase.key, [])
        for name in part_names:
            self._run_part(name, phase)

    def _install_eggs(self):
        develop_eggs = self._config.get('develop-eggs')
        if develop_eggs:
            self._pip.add_develop_eggs(develop_eggs)
        self._pip.install()

        eggs = self._config.get('eggs')
        if eggs:
            self._pip.add_eggs(eggs)
        self._pip.install()

    def _run_part(self, name, phase):
        part = self.config.get_part(name)
        if part.is_recipe:
            section_instance = self._buildout.get_part_instance(part)
            self._buildout.install_part(section_instance)
        elif part.is_isotope:
            pass
