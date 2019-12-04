import jobs
import time
import itertools
import pathlib

@jobs.OnResult(jobs.GetMimeType)
def OnResult(job, result):
    if job.status == "exception":
        raise result.exception
    else:
        print(f"{result.file}: {result.mime}")

pool = jobs.ThreadedJobPool(threads = 16)

for file in pathlib.Path("/usr/bin").iterdir():
    job = jobs.GetMimeType(file)
    #job.onresult = OnResult
    pool.Add(job)

#job = jobs.ExceptionJob()
#job.onresult = OnResult
#pool.Add(job)
#pool.Join(i)

#pool.Add(i)
#result = pool.Join(i)
#pool.Close()
#raise Exception(f"{result.file}: {result.mime}")

for i in itertools.count():
    print("Busy loop!")
    jobsleft = len([x for x in pool.jobs if x.status == "running"])
    if not jobsleft:
        print("No jobs left, exiting...")
        pool.Close()
        raise SystemExit(0)
    print(f"Jobs left: {jobsleft}")
    print("Sleeping for 1 second...")
    time.sleep(1)