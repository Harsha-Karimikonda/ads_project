#!/usr/bin/env python3
"""
COP 5536 Fall 2026 Programming Project - Job Scheduler
jobScheduler.py: Main simulation driver and command processor.

Usage:
    python3 jobScheduler.py input_file
Output:
    <input-base>_output_file.txt
"""

import sys
import os
import heapq
from typing import List, Dict, Tuple, Optional

from job import Job, JobStatus
from avl_tree import AVLTree
from max_heap import MaxHeap


class JobScheduler:
    """
    Simulates job execution and capacity management using an AVL Tree for
    primary storage, a Binary Max Heap for waiting jobs, and a library Min-Heap
    for running jobs.
    """
    def __init__(self, capacity: int = 1):
        self.capacity: int = capacity
        self.clock: int = 0
        
        # Primary lookup and storage (custom AVL Tree)
        self.avl_tree: AVLTree = AVLTree()
        
        # Waiting queue (custom Binary Max Heap)
        self.waiting_heap: MaxHeap = MaxHeap()
        
        # Cancelled jobs list (standard library list)
        self.cancelled_list: List[Job] = []
        
        # Running jobs Min-Heap: stores (completion_time, start_time, job_id, Job)
        self.running_pq: List[Tuple[int, int, int, Job]] = []
        
        # Execution order tracking: stores Job references in order they started
        self.execution_order: List[Job] = []
        
        # Record of all submitted job IDs (including active and cancelled)
        self.all_jobs: Dict[int, Job] = {}
        
        # Logged output messages
        self.output_lines: List[str] = []

    def _complete_jobs_up_to(self, timestamp: int):
        """
        Marks completed any running job whose completion time <= timestamp.
        Frees execution slots in running_pq.
        """
        while self.running_pq and self.running_pq[0][0] <= timestamp:
            comp_time, st, jid, job = heapq.heappop(self.running_pq)
            job.complete()

    def advance_time(self, timestamp: int):
        """Advances clock to timestamp and completes any finished jobs."""
        if timestamp > self.clock:
            self.clock = timestamp
        self._complete_jobs_up_to(self.clock)

    def submit_job(self, timestamp: int, job_id: int, priority: int, estimated_time: int, delta: int):
        """Handles SUBMIT command."""
        self.advance_time(timestamp)
        if job_id in self.all_jobs:
            self.output_lines.append(f"ERROR: Job {job_id} already exists")
            return

        job = Job(job_id, priority, estimated_time, delta, timestamp)
        self.all_jobs[job_id] = job
        self.avl_tree.insert(job_id, job)
        self.waiting_heap.insert(job)
        self.output_lines.append(f"Job {job_id} submitted at {timestamp} ms")

    def process_next(self, timestamp: int):
        """Handles PROCESS_NEXT command."""
        self.advance_time(timestamp)

        if self.waiting_heap.size == 0:
            self.output_lines.append("NO_WAITING_JOBS")
            return

        # If all k slots are occupied, wait until earliest running job completes
        if len(self.running_pq) >= self.capacity:
            earliest_completion = self.running_pq[0][0]
            self.clock = earliest_completion
            self._complete_jobs_up_to(self.clock)

        # Start highest-ranked waiting job
        job = self.waiting_heap.extract_max()
        if job:
            job.start(self.clock)
            heapq.heappush(self.running_pq, (job.completion_time, job.start_time, job.job_id, job))
            self.execution_order.append(job)
            self.output_lines.append(f"Job {job.job_id} started at {self.clock} ms")

    def find_job(self, timestamp: int, job_id: int):
        """Handles FIND command."""
        self.advance_time(timestamp)
        job = self.avl_tree.find(job_id)
        if not job:
            for cj in self.cancelled_list:
                if cj.job_id == job_id:
                    job = cj
                    break

        if not job:
            self.output_lines.append(f"ERROR: Job {job_id} not found")
        else:
            st = str(job.start_time) if job.start_time is not None else "null"
            act = str(job.actual_time) if job.actual_time is not None else "null"
            comp = str(job.completion_time) if job.completion_time is not None else "null"
            self.output_lines.append(
                f"Job {job.job_id}: submitted={job.submission_time}, started={st}, "
                f"actual_time={act}, completed={comp}, status={job.status}"
            )

    def job_status(self, timestamp: int):
        """Handles JOB_STATUS command."""
        self.advance_time(timestamp)
        self.output_lines.append("JOB STATUS")
        self.output_lines.append("Job       Submitted        Started    Actual Time       Completed       Status")

        # 1. Inorder traversal of AVL Tree
        for job in self.avl_tree.inorder_jobs():
            st = str(job.start_time) if job.start_time is not None else "null"
            act = str(job.actual_time) if job.actual_time is not None else "null"
            comp = str(job.completion_time) if job.completion_time is not None else "null"
            self.output_lines.append(
                f"{job.job_id:<9} {job.submission_time:<16} {st:<10} {act:<17} {comp:<15} {job.status}"
            )

        # 2. Cancelled jobs in cancellation order
        for job in self.cancelled_list:
            st = str(job.start_time) if job.start_time is not None else "null"
            act = str(job.actual_time) if job.actual_time is not None else "null"
            comp = str(job.completion_time) if job.completion_time is not None else "null"
            self.output_lines.append(
                f"{job.job_id:<9} {job.submission_time:<16} {st:<10} {act:<17} {comp:<15} {job.status}"
            )

        self.output_lines.append("END JOB STATUS")

    def cancel_job(self, timestamp: int, job_id: int):
        """Handles CANCEL command."""
        self.advance_time(timestamp)
        job = self.avl_tree.find(job_id)
        if job:
            if job.status == JobStatus.WAITING:
                self.waiting_heap.remove(job_id)
                self.avl_tree.delete(job_id)
                job.cancel()
                self.cancelled_list.append(job)
                self.output_lines.append(f"Job {job_id} cancelled")
            else:
                self.output_lines.append(f"ERROR: Job {job_id} cannot be cancelled while status is {job.status}")
        else:
            is_cancelled = any(cj.job_id == job_id for cj in self.cancelled_list)
            if is_cancelled:
                self.output_lines.append(f"ERROR: Job {job_id} cannot be cancelled while status is CANCELLED")
            else:
                self.output_lines.append(f"ERROR: Job {job_id} not found")

    def update_priority(self, timestamp: int, job_id: int, new_priority: int):
        """Handles UPDATE_PRIORITY command."""
        self.advance_time(timestamp)
        job = self.avl_tree.find(job_id)
        if job:
            if job.status == JobStatus.WAITING:
                self.waiting_heap.update_priority(job_id, new_priority)
                self.output_lines.append(f"Job {job_id} priority updated to {new_priority}")
            else:
                self.output_lines.append(f"ERROR: Job {job_id} priority cannot be updated while status is {job.status}")
        else:
            is_cancelled = any(cj.job_id == job_id for cj in self.cancelled_list)
            if is_cancelled:
                self.output_lines.append(f"ERROR: Job {job_id} priority cannot be updated while status is CANCELLED")
            else:
                self.output_lines.append(f"ERROR: Job {job_id} not found")

    def short_jobs(self, timestamp: int):
        """Handles SHORT_JOBS command."""
        self.advance_time(timestamp)
        self.waiting_heap.rebuild()
        self.output_lines.append("Scheduling mode changed to SHORT_JOBS")

    def generate_final_output(self) -> str:
        """Appends the required final structural representations and statistics."""
        # Execution order
        self.output_lines.append("EXECUTION_ORDER")
        for job in self.execution_order:
            self.output_lines.append(f"{job.job_id} {job.start_time} {job.completion_time}")
        self.output_lines.append("END_EXECUTION_ORDER")

        # AVL Tree level-by-level
        self.output_lines.extend(self.avl_tree.get_level_order_lines())

        # Inorder traversal
        inorder_str = ", ".join(str(k) for k in self.avl_tree.inorder_keys())
        self.output_lines.append(f"INORDER: [{inorder_str}]")

        # Max Heap internal array
        self.output_lines.append(self.waiting_heap.repr_str())

        # Tree Stats
        self.output_lines.append("TREE_STATS")
        self.output_lines.append(f"records={self.avl_tree.records}")
        self.output_lines.append(f"height={self.avl_tree.height}")
        self.output_lines.append(f"insertions={self.avl_tree.insertions}")
        self.output_lines.append(f"deletions={self.avl_tree.deletions}")
        self.output_lines.append(f"left_rotations={self.avl_tree.left_rotations}")
        self.output_lines.append(f"right_rotations={self.avl_tree.right_rotations}")
        self.output_lines.append("END_TREE_STATS")

        # Heap Stats
        self.output_lines.append("HEAP_STATS")
        self.output_lines.append(f"size={self.waiting_heap.size}")
        self.output_lines.append(f"max_size={self.waiting_heap.max_size}")
        self.output_lines.append(f"insertions={self.waiting_heap.insertions}")
        self.output_lines.append(f"extractions={self.waiting_heap.extractions}")
        self.output_lines.append(f"removals={self.waiting_heap.removals}")
        self.output_lines.append(f"priority_updates={self.waiting_heap.priority_updates}")
        self.output_lines.append(f"rebuilds={self.waiting_heap.rebuilds}")
        self.output_lines.append("END_HEAP_STATS")

        return "\n".join(self.output_lines) + "\n"


def run_scheduler(input_file_path: str):
    if not os.path.exists(input_file_path):
        print(f"Error: input file '{input_file_path}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(input_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    scheduler = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("CAPACITY"):
            parts = line.split()
            cap = int(parts[1])
            scheduler = JobScheduler(capacity=cap)
            continue

        if scheduler is None:
            # Default capacity 1 if CAPACITY line wasn't first
            scheduler = JobScheduler(capacity=1)

        parts = line.split()
        timestamp = int(parts[0])
        command = parts[1]

        if command == "SUBMIT":
            jid = int(parts[2])
            priority = int(parts[3])
            est = int(parts[4])
            delta = int(parts[5])
            scheduler.submit_job(timestamp, jid, priority, est, delta)

        elif command == "PROCESS_NEXT":
            scheduler.process_next(timestamp)

        elif command == "FIND":
            jid = int(parts[2])
            scheduler.find_job(timestamp, jid)

        elif command == "JOB_STATUS":
            scheduler.job_status(timestamp)

        elif command == "CANCEL":
            jid = int(parts[2])
            scheduler.cancel_job(timestamp, jid)

        elif command == "UPDATE_PRIORITY":
            jid = int(parts[2])
            new_p = int(parts[3])
            scheduler.update_priority(timestamp, jid, new_p)

        elif command == "SHORT_JOBS":
            scheduler.short_jobs(timestamp)

    if scheduler is None:
        scheduler = JobScheduler(capacity=1)

    final_content = scheduler.generate_final_output()

    # Determine output file name: <input-base>_output_file.txt
    base_name = os.path.splitext(os.path.basename(input_file_path))[0]
    output_filename = f"{base_name}_output_file.txt"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(final_content)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 jobScheduler.py <input_file>", file=sys.stderr)
        sys.exit(1)
    run_scheduler(sys.argv[1])
