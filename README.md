# ads_project
Advanced data structures project, implementation of Job scheduling system in HPC in Python.

## COP 5536 Fall 2026 Programming Project - Job Scheduler

### Overview
This project simulates an HPC batch job scheduler with a fixed execution capacity $k$. Submitted jobs are managed using a custom **AVL Tree** (keyed by `job_id`) for $O(\log n)$ primary storage and lookup, a custom **Binary Max Heap** for queueing `WAITING` jobs, and a library Min-Heap for tracking `RUNNING` jobs by earliest completion time.

### Project Structure
- `job.py`: `Job` entity definition and status lifecycle transitions (`WAITING`, `RUNNING`, `COMPLETED`, `CANCELLED`).
- `avl_tree.py`: Self-balancing AVL Tree implemented from scratch with rotation tracking (`records`, `height`, `insertions`, `deletions`, `left_rotations`, `right_rotations`) and level-order tree printing.
- `max_heap.py`: Binary Max Heap implemented from scratch storing waiting jobs, with position indexing for $O(\log n)$ cancellations/updates, `PRIORITY` and `SHORT_JOBS` scheduling modes, and bottom-up rebuild.
- `jobScheduler.py`: Main discrete-event simulation engine and command dispatcher.
- `test_scheduler.py`: Automated test suite covering Testcases 1, 2, 3 and standalone data structure tests.
- `generate_report.py`: Script to generate the required 2-page project documentation PDF.
- `report.pdf`: Generated project report.
- `Makefile`: Build, test, and packaging automation.

### Requirements
- Python 3.8+ (standard library only, no external packages required)
- `make`

### Building and Running
To prepare the executable:
```bash
make
```

To run a simulation on an input file:
```bash
python3 jobScheduler.py <input_file>
# or
./jobScheduler <input_file>
```
Output will be written to `<input-base>_output_file.txt`.

### Running Tests
To run the automated verification suite:
```bash
make test
```

### Packaging for Submission
To generate `submission.zip` containing all required files in the top-level directory without nested folders:
```bash
make pack
```
