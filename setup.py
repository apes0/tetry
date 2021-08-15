from setuptools import find_packages, setup

with open('readme.md') as f:
    readme = f.read()

with open('requirements.txt') as f:
    requirements = f.read()


source = 'https://github.com/apes0/tetry'

setup(
    url=source,
    name='tetry',
    project_urls={
        'Source': source,
        'Tracker': f'{source}/issues',
    },
    packages=find_packages(
        include=['tetry', 'tetry.api', 'tetry.oldApi', 'tetry.bot', 'tetry.bot.engine']),
    version='0.4.0',
    description='tetr.io api wrapper',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='apes0',
    python_requires='>=3',
    install_requires=requirements
)
