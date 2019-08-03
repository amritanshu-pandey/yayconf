import os
import sys

from setuptools import find_packages, setup

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 6)

# This check and everything above must remain compatible with Python 2.7.
if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(
        """
==========================
Unsupported Python version
==========================

This version of yayconf requires Python {}.{}, but you're trying to
install it on Python {}.{}.
""".format(
            *(REQUIRED_PYTHON + CURRENT_PYTHON)
        )
    )
    sys.exit(1)

install_requires = ["pyyaml"]

test_requires = ["flake8", "pytest", "pytest-mock", "pytest-faker"]

extras = {"test": test_requires}

setup(
    name="yayconf",
    version=os.getenv('DRONE_TAG'),
    python_requires=">={}.{}".format(*REQUIRED_PYTHON),
    author="Amritanshu Pandey",
    author_email="amp.msit@gmail.com",
    description=(
        "Yet another yaml based configuration library"
    ),
    license="Apache",
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests", ".testenv"]
    ),
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras,
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: CLI Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
