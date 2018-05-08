import multiprocessing
import multiprocessing.pool
#from multiprocessing import Pool
import time
from random import randint

#pool = Pool(processes=1)



class NoDaemonProcess(multiprocessing.Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess

def sleepawhile(t):
    print("Sleeping %i seconds..." % t)
    time.sleep(t)
    return t

def fn(x):
    print("Entering fn")
    time.sleep(10)
    print ("Exiting fn")
    return x*x


def work():
    pool = multiprocessing.Pool()

    result = pool.map(fn, [3])

    # The following is not really needed, since the (daemon) workers of the
    # child's pool are killed when the child is terminated, but it's good
    # practice to cleanup after ourselves anyway.
    pool.close()
    pool.join()
    print result


if __name__ == '__main__':
    work()

'''
def scrape_data_callback(response):
    print(response)


def scrape_data(request):
    time.sleep(10)
    return request


def scrape_task(request):
    result = pool.apply_async(scrape_data, [request], scrape_data_callback)
    print ("Returning from Async task")
    return
'''