
from distutils.core import setup
 
 
setup(
    name = "django-email-extras",
    version = __import__("email_extras").__version__,
    author = "Stephen McDonald",
    author_email = "stephen.mc@gmail.com",
    description = "A Django reusable app providing the ability to send PGP " \
        "encrypted and multipart emails using the Django templating system.",
    long_description = open("README.rst").read(),
    url = "http://bitbucket.org/citrus/django-email-extras",
    packages = ["email_extras",],
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

