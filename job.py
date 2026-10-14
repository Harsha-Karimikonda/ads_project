"""
COP 5536 Fall 2026 Programming Project - Job Scheduler
job.py: Definition of the Job entity.
"""

class JobStatus:
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Job:
    """
    Represents a single job submitted to the job scheduler.
    """
    def __init__(self, job_id: int, priority: int, estimated_time: int, delta: int, submission_time: int):
        self.job_id = job_id
        self.priority = priority
        self.estimated_time = estimated_time
        self.delta = delta
        self.submission_time = submission_time
        
        self.start_time = None
        self.actual_time = None
        self.completion_time = None
        self.status = JobStatus.WAITING

    def start(self, start_timestamp: int):
        """Transitions job to RUNNING and calculates actual and completion times."""
        self.status = JobStatus.RUNNING
        self.start_time = start_timestamp
        self.actual_time = self.estimated_time + self.delta
        self.completion_time = self.start_time + self.actual_time

    def complete(self):
        """Transitions job to COMPLETED."""
        self.status = JobStatus.COMPLETED

    def cancel(self):
        """Transitions job to CANCELLED."""
        self.status = JobStatus.CANCELLED

    def __repr__(self):
        return (f"Job(id={self.job_id}, p={self.priority}, est={self.estimated_time}, "
                f"delta={self.delta}, sub={self.submission_time}, status={self.status})")
