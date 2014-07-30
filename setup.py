
import sys
from shutil import rmtree
from setuptools import setup, find_packages


if sys.argv[:2] == ["setup.py", "bdist_wheel"]:
    # Remove previous build dir when creating a wheel build,
    # since if files have been removed from the project,
    # they'll still be cached in the build dir and end up
    # as part of the build, which is unexpected.
    try:
        rmtree("build")
    except:
        pass


setup(
    name = "django-email-extras",
    version = __import__("email_extras").__version__,
    author = "Stephen McDonald",
    author_email = "steve@jupo.org",
    description = "A Django reusable app providing the ability to "
                  "send PGP encrypted and multipart emails using "
                  "the Django templating system.",
    long_description = open("README.rst").read(),
    url = "https://github.com/stephenmcd/django-email-extras",
    packages = find_packages(),
    zip_safe = False,
    include_package_data = True,
    install_requires=["python-gnupg", "sphinx-me",],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Framework :: Django",
        "Topic :: Communications :: Email",
        "Topic :: Security :: Cryptography",
    ]
)
