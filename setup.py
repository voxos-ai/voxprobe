from setuptools import setup, find_packages

setup(
    name='voxprobe',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # TODO: Add your dependencies here
        'argparse',
    ],
    entry_points={
        'console_scripts': [
            'voxprobe=voxprobe.__main__:main',
        ],
    },
)
