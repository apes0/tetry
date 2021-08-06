from setuptools import find_packages, setup

with open('readme.md') as f:
    readme = f.read()


setup(
    name='tetry',
    packages=find_packages(
        include=['tetry', 'tetry.api', 'tetry.oldApi', 'tetry.bot', 'tetry.bot.engine']),
    version='0.3',
    description='tetr.io api wrapper',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='apes0',
    python_requires='>=3',
    install_requires=['requests', 'msgpack', 'trio', 'trio-websockets']
)
