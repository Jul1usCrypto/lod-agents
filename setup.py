# MIT License
# Copyright (c) 2020 MiscellaneousStuff
# Copyright (c) 2025 League of Degens
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""LoD Agent SDK — AI agents for League of Degens."""
from setuptools import setup

description = """LoD Agent SDK — League of Degens AI Agent Toolkit

The LoD Agent SDK is the Python component of the League of Degens AI ecosystem.
Built on pylol by MiscellaneousStuff (MIT License), it provides a reinforcement
learning environment where AI agents can play League of Degens matches — receiving
structured game state and sending actions through a simple Python API.

Docs: https://leagueofdegens.com/agents.html
"""

setup(
    name='lod-agents',
    version='1.0.0',
    description='LoD Agent SDK — Build AI agents that play League of Degens.',
    long_description=description,
    long_description_content_type="text/markdown",
    author='League of Degens',
    license='MIT License',
    keywords='League of Legends AI reinforcement learning agents LoD',
    url='https://github.com/Jul1usCrypto/lod-agents',
    packages=[
        'pylol',
        'pylol.agents',
        'pylol.bin',
        'pylol.env',
        'pylol.lib',
        'pylol.maps',
        'pylol.run_configs',
        'pylol.tests'
    ],
    install_requires=[
        'absl-py>=0.1.0',
        'numpy>=1.10',
        'six',
        'redis',
        'portpicker'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ]
)
