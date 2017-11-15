import os
from uranium import task_requires


def main(build):
    build.packages.install(".", develop=True)


@task_requires("main")
def test(build):
    """ execute tests """
    build.packages.install_list([
        "pytest==2.9.2",
        "pytest-cov",
        "httpretty==0.8.10"
    ])
    build.executables.run([
        "py.test", os.path.join(build.root, "tests"),
        "--cov", "uranium",
        "--cov-config", "coverage.cfg",
    ] + build.options.args)


@task_requires("main")
def build_docs(build):
    """ build documentation """
    build.packages.install_list([
        "Babel", "Sphinx", "sphinx_rtd_theme"
    ])
    return build.executables.run([
        "sphinx-build", "docs",
        os.path.join("docs", "_build")
    ] + build.options.args)[0]


def publish(build):
    """ distribute the uranium package """
    build.packages.install("wheel")
    build.executables.run([
        "python", "setup.py",
        "bdist_wheel", "--universal", "upload", "--release"
    ])
