from ..lib.asserts import get_assert_function
from ..exceptions import PackageException
from .versions import Versions
from .pippuppet import PipPuppet
import virtualenv

p_assert = get_assert_function(PackageException)

DEFAULT_INDEX_URLS = ['https://pypi.python.org/simple/']


class Packages(object):
    """
    this is the public API for downloading packages into an environment.

    unless otherwise specified, all properties in this class are
    mutable: updating them will take immediate effect.
    """

    def __init__(self, virtualenv_dir=None, pip_executable=None):
        self._virtualenv_dir = virtualenv_dir
        self._pip = PipPuppet("pip")
        self._versions = Versions()
        self._index_urls = list(DEFAULT_INDEX_URLS)

    @property
    def versions(self):
        """versions is a dictionary object of <package_name, version_spec> pairs.

        when a request is made to install a package, it will use the
        version specified in this dictionary.

        * if the package installation specifies a version, it will override
        the version specified here.

        .. code:: python

            # this sets the version to be used in this dictionary to 0.2.3.
            packages.install("uranium", version="==0.2.3")

        TODO: this will also contain entries to packages installed without a specified version.
        the version installed will be updated here.
        """
        # TODO: create a version dictionary,
        # to assert version specs.
        return self._versions

    @property
    def constraints(self):
        """ versions, specified as a list of constraint syntax. """
        constraints = [
            "{0}{1}".format(k, v) for k, v in self.versions.items()
        ]

    @property
    def index_urls(self):
        """
        index urls is a list of the urls that Packages queries when
        looking for packages.
        """
        return self._index_urls

    @index_urls.setter
    def index_urls(self, value):
        p_assert(isinstance(value, list),
                 "only lists can be set as a value for indexes")
        self._index_urls = value

    def install_list(self, requirement_list, upgrade=False, install_options=None):
        """ install a list of requirements """
        self._pip.install(
            requirements=requirement_list,
            constraints=self.constraints,
            upgrade=upgrade,
            install_options=install_options,
            prefix=self._virtualenv_dir
        )
        for package, details in self._pip.installed_packages.items():
            self.versions[package] = "==" + details["version"]

        # if virtualenv dir is set, we should make the environment relocatable.
        # this will fix issues with commands not being usable by the
        # uranium via build.executables.run
        if self._virtualenv_dir:
            virtualenv.make_environment_relocatable(self._virtualenv_dir)

    def install(self, name, version=None, develop=False,
                upgrade=False, install_options=None):
        """
        install is used when installing a python package into the environment.

        if version is set, the specified version of the package will be installed.
        The specified version should be a full `PEP 440`_ version specifier (i.e. "==1.2.0")

        .. _`PEP 440`: https://www.python.org/dev/peps/pep-0440/

        if develop is set to True, the package will be installed as editable: the source
        in the directory passed will be used when using that package.

        if install_options is provided, it should be a list of options, like
        ["--prefix=/opt/srv", "--install-lib=/opt/srv/lib"]
        """
        if self._is_package_already_installed(name, version):
            return
        p_assert(
            not (develop and version),
            "unable to set both version and develop flags when installing packages"
        )
        if name in self.versions:
            if version is None:
                version = self.versions[name]
            del self.versions[name]
        if develop:
            requirement = "-e " + name
        elif version:
            requirement = name + version
        else:
            requirement = name
        self.install_list([requirement], upgrade=upgrade,
                           install_options=install_options)

    def uninstall(self, package_name):
        """
        uninstall is used when uninstalling a python package from a environment.
        """
        p_assert(
            self._is_package_already_installed(package_name, None),
            "package {package} doesn't exist".format(package=package_name)
        )
        self._pip.uninstall(package_name)

    @staticmethod
    def _is_package_already_installed(name, version):
        import pkg_resources
        try:
            package_name = name
            if version:
                package_name += version
            pkg_resources.get_distribution(package_name)
            return True
        except Exception:
            pass
        return False
