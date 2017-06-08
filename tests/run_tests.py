import sys
import unittest
from os.path import dirname, join, abspath


def from_here(*parts):
    return abspath(join(HERE, *parts))


HERE = dirname(__file__)
sys.path += [
    from_here('..', '..'),
    from_here('stubs')
]


def main():
    loader = unittest.TestLoader()
    suite = loader.discover(HERE)
    result = unittest.TextTestRunner(verbosity=5).run(suite)
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
