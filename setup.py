from setuptools import setup

setup(
    name='therminator_client',
    version='0.0.1',
    description='The therminator client',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Hardware',
    ],
    url='https://github.com/jparker/therminator_client',
    author='John Parker',
    author_email='jparker@urgetopunt.com',
    license='MIT',
    packages=['therminator'],
    install_requires=[
        'PyYAML',
        'requests',
    ],
    zip_safe=False,
)
