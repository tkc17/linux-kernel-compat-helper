import re
import subprocess

from setuptools import setup, find_packages
# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

lat_tag_name = ""
# Only for tox where git is not available
version = "1.0"
try:
    lat_tag_name = subprocess.check_output("git tag | tail -1", shell=True, encoding="UTF-8").strip()
except CalledProcessError as ce:
    print (ce)

if lat_tag_name:
    # Ignore numbers in the test (vx.y/testx.y)
    version_m= re.search(r"^[^0-9]+(.*)", lat_tag_name)
    if version_m:
        version = version_m.group(1)

setup(
    version=version,
    long_description=long_description,
    long_description_content_type='text/markdown'
)
