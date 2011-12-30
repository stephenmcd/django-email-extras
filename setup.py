
from setuptools import setup


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
    packages = ["email_extras",],
    zip_safe = False,
    include_package_data = True,
    install_requires=["python-gnupg", "sphinx-me",],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Communications :: Email",
        "Topic :: Security :: Cryptography",
    ]
)
