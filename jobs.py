from typing import Tuple
from .codes import LaserJobOp, LaserOp


def create_job_batches(jobs: Tuple[LaserOp, ...]):
    # job batch must be length of exactly 256 jobs,
    # if not last one is padded with nops
    for i in range(0, len(jobs), 256):
        batch = jobs[i:i+256]
        if len(batch) < 256:
            batch += (LaserOp(LaserJobOp.NOP), ) * (256 - len(batch))
        batch_bytes = b''.join(job.to_bytes() for job in batch)
        yield batch_bytes

