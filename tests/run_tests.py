import sys
import unittest
from os.path import dirname, join, abspath

from_here = lambda *parts: abspath(join(HERE, *parts))

HERE = dirname(__file__)
sys.path += [
    from_here('..', '..'),
    from_here('stubs')
]


def main():
    loader = unittest.TestLoader()
    suite = loader.discover(HERE)

    unittest.TextTestRunner(
        verbosity=5
    ).run(suite)

if __name__ == '__main__':
    main()
