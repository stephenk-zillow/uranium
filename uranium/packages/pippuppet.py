import json
import logging
import os
import subprocess
import tempfile
from contextlib import contextmanager

LOG = logging.getLogger(__name__)

class PipPuppet(object):
    """ a class that manipulates pip's command line. """

    def __init__(self, pip_executable, verbose=True):
        self._executable = pip_executable
        self._verbose = verbose

    def install(self, **kwargs):
        with self._setup_args(**kwargs) as args:
            output = self._exec("install", *args)
            if self._verbose:
                LOG.info(output.decode())

    def uninstall(package_name):
        """
        a convenience function to uninstall a package.
        """
        output = self._exec("uninstall", "package_name", "--yes")
        if self._verbose:
            LOG.info(output.decode())

    @contextmanager
    def _setup_args(self, requirements=None, constraints=None, upgrade=False,
                    install_options=None, prefix=None, index_urls=None):
        """
        :param constraints: List: a list of constraint specifiers.
        """
        args = []
        if upgrade:
            args.append("--upgrade")

        if prefix:
            args += ["--prefix", prefix]

        if install_options:
            args += ["--install-options", install_options]

        if index_urls:
            args += ["-i", index_urls[0]]
            args += ["--trusted-host", _get_netloc(index_urls[0])]
            for url in index_urls[1:]:
                args += ["--extra-index-url", url]
                args += ["--trusted-host", _get_netloc(url)]

        if constraints:
            _, constraints_path = tempfile.mkstemp()
            with open(constraints_path, "w+") as fh:
                fh.write("\n".join(constraints))
            fh.close()
            args += ["-c", constraints_path]

        if requirements:
            _, requirements_path = tempfile.mkstemp()
            with open(requirements_path, "w+") as fh:
                fh.write("\n".join(requirements))
            fh.close()
            args += ["-r", requirements_path]

        yield args

        if constraints:
            os.unlink(constraints_path)
        if requirements:
            os.unlink(requirements_path)

    @property
    def installed_packages(self):
        """
        return back a python dictionary of installed packages,
        and their detailed information:

            {
                "requests": {"version": "2.14"}
            }
        """
        # requires pip9+
        package_list = json.loads(self._exec("list", "--format=json"))
        result = {}
        for package_details in package_list:
            name = package_details.pop("name")
            result[name] = package_details
        return result

    def _exec(self, *command_list):
        """ execute the specified command """
        command = [self._executable] + list(command_list)
        return subprocess.check_output(command)

def _get_netloc(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc
