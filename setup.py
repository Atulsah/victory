from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in victory/__init__.py
from victory import __version__ as version

setup(
	name="victory",
	version=version,
	description="Custom Reporting and Custom Doctype",
	author="Atul Sah",
	author_email="atul.sah7@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
