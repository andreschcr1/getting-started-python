from glob import glob
import os

import nox

REPO_TOOLS_REQ = \
    'git+https://github.com/GoogleCloudPlatform/python-repo-tools.git'

DIRS = [
    # Hello world doesn't have system tests, just a lint test which will be
    # covered by the global lint here.
    # '1-hello-world',
    '2-structured-data',
    '3-binary-data',
    '4-auth',
    '5-logging',
    '6-pubsub',
    '7-gce',
]

PYTEST_COMMON_ARGS = ['--junitxml=sponge_log.xml']


@nox.session
def check_requirements(session):
    session.install(REPO_TOOLS_REQ)

    if 'update' in session.posargs:
        command = 'update-requirements'
    else:
        command = 'check-requirements'

    for reqfile in glob('**/requirements*.txt'):
        session.run('gcp-devrel-py-tools', command, reqfile)


@nox.session
def lint(session):
    session.install('flake8', 'flake8-import-order')
    session.run(
        'flake8', '--exclude=env,.nox,._config.py,.tox',
        '--import-order-style=google', '.')


def run_test(session, dir):
    session.install('-r', 'requirements.txt')
    session.chdir(dir)
    if os.path.exists('requirements.txt'):
        session.install('-r', 'requirements.txt')

    session.env['PYTHONPATH'] = os.getcwd()
    session.run(
        'pytest',
        *(PYTEST_COMMON_ARGS + session.posargs),
        # Pytest will return 5 when no tests are collected. This can happen
        # on travis where slow and flaky tests are excluded.
        # See http://doc.pytest.org/en/latest/_modules/_pytest/main.html
        success_codes=[0, 5])


@nox.session
@nox.parametrize('dir', DIRS)
def run_tests(session, dir=None):
    """Run all tests for all directories (slow!)"""
    run_test(session, dir)


@nox.session
@nox.parametrize('dir', DIRS)
def travis(session, dir=None):
    """On travis, only run the py3.4 and cloudsql tests."""
    run_tests(
        session,
        dir=dir)
