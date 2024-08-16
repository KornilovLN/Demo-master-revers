#!/usr/bin/env python
import yaml
from pathlib import Path
from ekatra.backend.parts.ha import core
from Queue import Queue
from threading import Thread



CONF = '''
EKATRA_BACKEND_HISTORY_ACCESS:
#   cache: 
#     name: Test
#     verbose: true
  cache:
    name: Disk
    path: './.cache/tsdb'
    policy: portable
  layers:
    default:
      provider:
        name: OpenTSDBDUMP
        path: ./.cache/tsdb_dump
#       write_cache: false
'''



class Worker(Thread):
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)
            finally:
                self.tasks.task_done()


class ThreadPool:
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        for args in args_list:
            self.add_task(func, *args)

    def wait_completion(self):
        self.tasks.join()


def warmmp(ha, metric, start, end, level):
    ignore_cached = True
    forse_cached  = True
    column = start / (ha.levels[level] * ha.min_duration)
    ecolumn = end / (ha.levels[level] * ha.min_duration)
    layer = ha.getLayer('default')
    layer.metatile.slots = ecolumn - column + 1
    kind = 'A' if metric.split('.')[-1][0] == 'a' and not metric.endswith('.S') else 'B'
    print 'metric', metric, level, column, ecolumn
    ha.get(metric, level, column, ignore_cached=ignore_cached, kind=kind, forse_cached=forse_cached)


def process(metric, conf, start, end):
    ha = core.HistoryAccess()
    ha.init(conf)
    for level in range(len(ha.levels)):
        warmmp(ha, metric, start, end, level)


def main(conf, start, end):
    srs = conf['layers']['default']['provider']['path']
    root = Path(srs)
    pool = ThreadPool(10)
    tasks = [(fn.name, conf, start, end) for fn in sorted(root.glob('*.*'))]
#    tasks = [(fn.name, conf, start, end) for fn in sorted(root.glob('z5.aGT01N01'))]
    pool.map(process, tasks)
    pool.wait_completion()


if __name__ == "__main__":
    config = yaml.load(CONF)
    conf = config.setdefault('EKATRA_BACKEND_HISTORY_ACCESS', {})
    start = 1455408000
    end = start + 86400 * 365 * 4
    main(conf, start=start, end=end)

