from __future__ import print_function

import os

import torch

from .utils.dir import make_dirs
from .utils.download import download_url
from .utils.planetoid import read_planetoid


class Cora(object):
    url = "https://github.com/kimiyoung/planetoid/raw/master/data"

    def __init__(self, root, transform=None, target_transform=None):

        super(Cora, self).__init__()

        self.root = os.path.expanduser(root)
        self.raw_folder = os.path.join(self.root, 'raw')
        self.processed_folder = os.path.join(self.root, 'processed')
        self.data_file = os.path.join(self.processed_folder, 'data.pt')

        self.transform = transform
        self.target_transform = target_transform

        self.download()
        self.process()

        # Load processed data.
        self.input, index, self.target = torch.load(self.data_file)

        # Create unweighted sparse adjacency matrix.
        weight = torch.ones(index.size(1))
        n = self.input.size(0)
        self.adj = torch.sparse.FloatTensor(index, weight, torch.Size([n, n]))

    def __getitem__(self, index):
        data = (self.input, self.adj)
        target = self.target

        if self.transform is not None:
            data = self.transform(data)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return (data, target, self.mask)

    def __len__(self):
        return 1

    def _check_exists(self):
        return os.path.exists(self.root)

    def _check_processed(self):
        return os.path.exists(self.data_file)

    def download(self):
        if self._check_exists():
            return

        print('Downloading {}'.format(self.url))

        ext = ['x', 'y', 'tx', 'ty', 'allx', 'ally', 'graph', 'test.index']
        for e in ext:
            url = '{}/ind.{}.{}'.format(self.url, 'cora', e)
            download_url(url, self.raw_folder)

    def process(self):
        if self._check_processed():
            return

        print('Processing...')

        make_dirs(os.path.join(self.processed_folder))
        dir = os.path.join(self.raw_folder)
        data = read_planetoid(dir, 'cora')
        torch.save(data, self.data_file)

        print('Done!')
