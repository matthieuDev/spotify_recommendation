import os

base_folder = '/'.join(
    os.path.abspath(__file__).replace('\\', '/').split('/')[:-1]
) + '/'
cache_folder = base_folder + 'cache/'
