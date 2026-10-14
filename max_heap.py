"""
COP 5536 Fall 2026 Programming Project - Job Scheduler
max_heap.py: Binary Max Heap implementation for waiting jobs.
"""

from typing import List, Dict, Optional
from job import Job


class SchedulingMode:
    PRIORITY = "PRIORITY"
    SHORT_JOBS = "SHORT_JOBS"


class MaxHeap:
    """
    Binary Max Heap storing WAITING Job references.
    Supports:
    - PRIORITY mode (priority DESC, submission_time ASC, job_id ASC)
    - SHORT_JOBS mode (estimated_time ASC, priority DESC, submission_time ASC, job_id ASC)
    - Dynamic O(log n) removal and priority updates via an internal position map.
    - Statistics tracking: size, max_size, insertions, extractions, removals, priority_updates, rebuilds.
    """
    def __init__(self):
        self.heap: List[Job] = []
        self.pos: Dict[int, int] = {}
        self.mode: str = SchedulingMode.PRIORITY
        
        # Statistics
        self.max_size: int = 0
        self.insertions: int = 0
        self.extractions: int = 0
        self.removals: int = 0
        self.priority_updates: int = 0
        self.rebuilds: int = 0

    @property
    def size(self) -> int:
        return len(self.heap)

    def _higher_rank(self, a: Job, b: Job) -> bool:
        """Returns True if job 'a' has higher scheduling rank than job 'b'."""
        if self.mode == SchedulingMode.PRIORITY:
            if a.priority != b.priority:
                return a.priority > b.priority
            if a.submission_time != b.submission_time:
                return a.submission_time < b.submission_time
            return a.job_id < b.job_id
        else:
            # SHORT_JOBS mode
            if a.estimated_time != b.estimated_time:
                return a.estimated_time < b.estimated_time
            if a.priority != b.priority:
                return a.priority > b.priority
            if a.submission_time != b.submission_time:
                return a.submission_time < b.submission_time
            return a.job_id < b.job_id

    def _swap(self, i: int, j: int):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.pos[self.heap[i].job_id] = i
        self.pos[self.heap[j].job_id] = j

    def _sift_up(self, i: int):
        while i > 0:
            parent = (i - 1) // 2
            if self._higher_rank(self.heap[i], self.heap[parent]):
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i: int):
        n = len(self.heap)
        while True:
            largest = i
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and self._higher_rank(self.heap[left], self.heap[largest]):
                largest = left
            if right < n and self._higher_rank(self.heap[right], self.heap[largest]):
                largest = right
            if largest != i:
                self._swap(i, largest)
                i = largest
            else:
                break

    def insert(self, job: Job):
        """Inserts a waiting job into the heap."""
        self.insertions += 1
        idx = len(self.heap)
        self.heap.append(job)
        self.pos[job.job_id] = idx
        self._sift_up(idx)
        if len(self.heap) > self.max_size:
            self.max_size = len(self.heap)

    def extract_max(self) -> Optional[Job]:
        """Extracts and returns the highest ranking waiting job."""
        if not self.heap:
            return None
        self.extractions += 1
        top = self.heap[0]
        del self.pos[top.job_id]
        last = self.heap.pop()
        if self.heap:
            self.heap[0] = last
            self.pos[last.job_id] = 0
            self._sift_down(0)
        return top

    def remove(self, job_id: int) -> Optional[Job]:
        """Removes a job by its job_id from the heap in O(log n) time."""
        if job_id not in self.pos:
            return None
        self.removals += 1
        idx = self.pos[job_id]
        job = self.heap[idx]
        del self.pos[job_id]
        last = self.heap.pop()
        if idx < len(self.heap):
            self.heap[idx] = last
            self.pos[last.job_id] = idx
            parent = (idx - 1) // 2
            if idx > 0 and self._higher_rank(self.heap[idx], self.heap[parent]):
                self._sift_up(idx)
            else:
                self._sift_down(idx)
        return job

    def update_priority(self, job_id: int, new_priority: int) -> bool:
        """Updates the priority of a waiting job and restores heap property."""
        if job_id not in self.pos:
            return False
        self.priority_updates += 1
        idx = self.pos[job_id]
        self.heap[idx].priority = new_priority
        parent = (idx - 1) // 2
        if idx > 0 and self._higher_rank(self.heap[idx], self.heap[parent]):
            self._sift_up(idx)
        else:
            self._sift_down(idx)
        return True

    def rebuild(self):
        """Switches mode permanently to SHORT_JOBS and reorganizes the waiting heap."""
        self.mode = SchedulingMode.SHORT_JOBS
        self.rebuilds += 1
        n = len(self.heap)
        for i in reversed(range(n // 2)):
            self._sift_down(i)

    def repr_str(self) -> str:
        """Returns the internal array representation of the Max Heap."""
        if not self.heap:
            return "MAX_HEAP: []"
        items = [f"({j.job_id},{j.priority},{j.estimated_time})" for j in self.heap]
        return "MAX_HEAP: [" + ", ".join(items) + "]"
