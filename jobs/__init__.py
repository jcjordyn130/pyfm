import threading
import time
import magic
import random
import queue

# example:
# job = jobs.GetMimeType("/some/file")
# job.onresult = somefunc
# am I just reimplementing asyncio with threads?
# jobpool.Add(job)

class GenericJobPool():
    pass

class ThreadedJobPool(GenericJobPool):
    jobs = list()
    jobthreads = list()
    queue = queue.Queue()

    def __init__(self, threads):
        self.threads = threads

        for i in range(0, threads):
            jobthread = threading.Thread(target = self._jobthread)
            jobthread.start()
            self.jobthreads.append(jobthread)

    def _jobthread(self):
        while True:
            job = self.queue.get()
            if job == "close":
                break

            try:
                job.Run()
            except Exception as e:
                job.OnException(e)

    def Close(self):
        for jobthread in self.jobthreads:
            self.queue.put("close")

    def Join(self, job):
        return None

    def Add(self, job):
        # This function was originally named "Run" but I decided against
        # that as the job might not be ran when the function returns.
        # All this function does is adds a job to the execution queue.
        #
        # The reason we add it to the list of jobs here, is because
        # the job threads might be all stuck in a job.
        self.jobs.append(job)
        self.queue.put(job)

class Job():
    onresult = None
    status = "notrunning"

    def Run(self):
        self.status = "running"

    def OnResult(self, result):
        self.status = "done"
        self.onresult(result)

    def OnException(self, exception):
        self.status = "exception"
        self.onresult(JobException(exception))

def OnResult(job):
    def onresult(func):
        job.onresult = func

    return onresult

class Sleeper(Job):
    def __init__(self, time):
        self.time = time

    def Run(self):
        print(f"sleeping for {self.time}")
        time.sleep(self.time)
        print("done!")

class ExceptionJob(Job):
    def __init__(self):
        pass

    def Run(self):
        super().Run()
        time.sleep(1)
        raise Exception("test")

class GetMimeType(Job):
    def __init__(self, file):
        self.file = file

    def Run(self):
        # Run the superclass
        # This is internal, but all it does is mark us as running.
        super().Run()

        mime = magic.from_file(str(self.file), mime = True)
        #time.sleep(random.randrange(1, 5)) # Emulate latency...
        result = JobResult()
        result.mime = mime
        result.file = self.file
        self.OnResult(result)

class JobEvent():
    pass

class JobException(JobEvent):
    exception = None

    def __init__(self, exception):
        self.exception = exception

class JobResult(JobEvent):
    pass