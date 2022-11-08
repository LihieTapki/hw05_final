import os.path

import environ

env = environ.Env(
    DEBUG=(bool, False),
    CI=(bool, False),
)
if os.path.exists('yatube.env'):
    environ.Env.read_env('yatube.env')

__all__ = [
    'env',
]
