import time
import operator

import gevent
from ginkgo.core import Service
from ginkgo.config import Setting

from ..models import Bin

class MemoryStorage(Service):
    cleanup_interval = Setting('cleanup_interval', default=3600)

    def __init__(self, bin_ttl):
        self.bin_ttl = bin_ttl
        self.bins = {}
        self.request_count = 0

    def do_start(self):
        self.spawn(self._cleanup_loop)

    def _cleanup_loop(self):
        while True:
            gevent.sleep(self.cleanup_interval)
            self._expire_bins()

    def _expire_bins(self):
        expiry = time.time() - self.bin_ttl
        for name, bin in self.bins.items():
            if bin.created < expiry:
                self.bins.pop(name)

    def create_bin(self, private=False):
        bin = Bin(private)
        self.bins[bin.name] = bin
        return self.bins[bin.name]

    def create_request(self, bin, request):
        bin.add(request)
        self.request_count += 1

    def count_bins(self):
        return len(self.bins)

    def count_requests(self):
        return self.request_count

    def lookup_bin(self, name):
        return self.bins[name]
