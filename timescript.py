import time
import pylab
from numpy import average
from pyrtm import rtm


# TEST PARAMETERS
test_iterations = 9
processes = 32
rtm = rtm.SBdart

# SET UP TESTS
tests = {proc: [{p:None for p in range(1, proc+1)}
                               for i in range(test_iterations)]
                                            for proc in range(1, processes+1)}


# GRAPH THE RESULTS
def show_results():
    results = [average([tests[t][i]['t'] for i in range(test_iterations)])/t for t in tests]
    longest = max(results)
    normalized = [result/results[0] for result in results]
    pylab.plot(range(1, processes+1), normalized)
    pylab.scatter(range(1, processes+1), normalized)
    pylab.plot(range(1, processes+1), [1 for i in range(processes)])
    pylab.ylim(ymin=0)
    pylab.xlim(xmin=0)
    pylab.grid()
    pylab.show()


# CALLBACK
def callback(result):
    # record the completion time for this run
    tf = time.time()
    
    # find out which test this was
    proc_num, proc, itt = [int(n) for n in result['description'].split()]
    
    # mark it as complete
    tests[proc_num][itt][proc] = True
    
    # check if this itteration is complete
    if all([tests[proc_num][itt][p] for p in range(1, proc_num+1)]):
        # save the time
        t = tf - tests[proc_num][itt]['t0']
        tests[proc_num][itt].update({'tf': tf, 't': t})
        # check if there are more processes to run
        if itt+1 < test_iterations:
            test(proc_num, itt+1)
        elif proc_num < processes:
            test(proc_num+1, 0)
        else:
            print tests
            show_results()


# RUN A TEST
def test(proc_num, itt):
    rtms = [rtm({'description': '%d %d %d' % (proc_num, num, itt)})
                                       for num in range(1, proc_num+1)]
    tests[proc_num][itt]['t0'] = time.time()
    print "\ntesting... %d %d" % (proc_num, itt)
    for r in rtms:
        r.go(callback)


# KICK IT ALL OFF
test(1, 0)

