"""
COP 5536 Fall 2026 - Comprehensive Test Suite
Validates jobScheduler against TestCases.docx and additional edge cases.
"""

import os
import subprocess
import sys
from avl_tree import AVLTree
from max_heap import MaxHeap
from job import Job

def run_testcase(test_num: int, input_text: str, expected_output_text: str):
    input_file = f"test{test_num}.txt"
    output_file = f"test{test_num}_output_file.txt"

    with open(input_file, "w", encoding="utf-8") as f:
        f.write(input_text.strip() + "\n")

    cmd = [sys.executable, "jobScheduler.py", input_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Testcase {test_num} failed to run:")
        print(result.stderr)
        return False

    if not os.path.exists(output_file):
        print(f"❌ Testcase {test_num} did not produce {output_file}")
        return False

    with open(output_file, "r", encoding="utf-8") as f:
        actual_output = f.read()

    # Normalize line endings and whitespace for table comparison
    actual_lines = [l.strip() for l in actual_output.strip().splitlines()]
    expected_lines = [l.strip() for l in expected_output_text.strip().splitlines()]

    # Normalize spaces inside lines to handle column alignment differences gracefully
    diffs = []
    if len(actual_lines) != len(expected_lines):
        diffs.append(f"Line count mismatch: actual {len(actual_lines)} vs expected {len(expected_lines)}")
    
    for i, (act, exp) in enumerate(zip(actual_lines, expected_lines)):
        act_tokens = act.split()
        exp_tokens = exp.split()
        if act_tokens != exp_tokens:
            diffs.append(f"Line {i+1} mismatch:\n  Actual:   {act}\n  Expected: {exp}")

    if diffs:
        print(f"❌ Testcase {test_num} MISMATCH:")
        for d in diffs[:10]:
            print("  ", d)
        return False

    print(f"✅ Testcase {test_num} PASSED!")
    return True

def test_data_structures_unit():
    print("Running standalone data structure unit tests...")
    
    # 1. Test AVL Tree rotations (LL, RR, LR, RL)
    avl = AVLTree()
    # Insert 30, 20, 10 -> LL rotation (1 right rotation)
    avl.insert(30, Job(30, 1, 10, 0, 0))
    avl.insert(20, Job(20, 1, 10, 0, 0))
    avl.insert(10, Job(10, 1, 10, 0, 0))
    assert avl.root.key == 20
    assert avl.right_rotations == 1
    assert avl.left_rotations == 0

    # Insert 40, 50 -> RR rotation at 30 (1 left rotation)
    avl.insert(40, Job(40, 1, 10, 0, 0))
    avl.insert(50, Job(50, 1, 10, 0, 0))
    assert avl.left_rotations == 1

    # Insert 25 -> LR rotation at 20 (1 left, 1 right)
    avl2 = AVLTree()
    avl2.insert(30, Job(30, 1, 10, 0, 0))
    avl2.insert(10, Job(10, 1, 10, 0, 0))
    avl2.insert(20, Job(20, 1, 10, 0, 0))
    assert avl2.root.key == 20
    assert avl2.left_rotations == 1
    assert avl2.right_rotations == 1

    # RL rotation at 10 (1 right, 1 left)
    avl3 = AVLTree()
    avl3.insert(10, Job(10, 1, 10, 0, 0))
    avl3.insert(30, Job(30, 1, 10, 0, 0))
    avl3.insert(20, Job(20, 1, 10, 0, 0))
    assert avl3.root.key == 20
    assert avl3.right_rotations == 1
    assert avl3.left_rotations == 1

    print("✅ AVL Tree rotation tests PASSED!")

    # 2. Test MaxHeap tie-breaking logic
    heap = MaxHeap()
    # Same priority, different submission time
    j1 = Job(1, 5, 20, 0, 10)
    j2 = Job(2, 5, 20, 0, 5) # earlier submission time
    heap.insert(j1)
    heap.insert(j2)
    assert heap.extract_max().job_id == 2 # j2 was submitted earlier
    
    # Same priority and submission time, tie broken by smaller job_id
    heap_tie = MaxHeap()
    j3 = Job(30, 5, 20, 0, 15)
    j4 = Job(20, 5, 20, 0, 15)
    heap_tie.insert(j3)
    heap_tie.insert(j4)
    assert heap_tie.extract_max().job_id == 20 # smaller job_id

    # SHORT_JOBS tie-breaker test
    heap_short = MaxHeap()
    sj1 = Job(1, 5, 50, 0, 10)
    sj2 = Job(2, 8, 50, 0, 10) # same est, higher priority
    heap_short.insert(sj1)
    heap_short.insert(sj2)
    heap_short.rebuild()
    assert heap_short.extract_max().job_id == 2

    print("✅ Max Heap tie-breaking tests PASSED!")

def main():
    tc1_in = """CAPACITY 2
5 SUBMIT 101 5 50 10
10 SUBMIT 102 8 30 5
15 SUBMIT 103 3 70 20
20 PROCESS_NEXT
30 PROCESS_NEXT
70 PROCESS_NEXT
170 JOB_STATUS"""

    tc1_out = """Job 101 submitted at 5 ms
Job 102 submitted at 10 ms
Job 103 submitted at 15 ms
Job 102 started at 20 ms
Job 101 started at 30 ms
Job 103 started at 70 ms
JOB STATUS
Job       Submitted        Started    Actual Time       Completed       Status
101       5                30         60                90              COMPLETED
102       10               20         35                55              COMPLETED
103       15               70         90                160             COMPLETED
END JOB STATUS
EXECUTION_ORDER
102 20 55
101 30 90
103 70 160
END_EXECUTION_ORDER
TREE
LEVEL 0: [102]
LEVEL 1: [101]|[103]
END_TREE
INORDER: [101, 102, 103]
MAX_HEAP: []
TREE_STATS
records=3
height=2
insertions=3
deletions=0
left_rotations=1
right_rotations=0
END_TREE_STATS
HEAP_STATS
size=0
max_size=3
insertions=3
extractions=3
removals=0
priority_updates=0
rebuilds=0
END_HEAP_STATS"""

    tc2_in = """CAPACITY 2
5 SUBMIT 101 2 50 5
10 SUBMIT 102 4 30 10
15 SUBMIT 103 6 70 5
20 SUBMIT 104 3 40 10
25 SUBMIT 105 5 60 5
30 UPDATE_PRIORITY 101 9
35 PROCESS_NEXT
40 UPDATE_PRIORITY 101 1
45 UPDATE_PRIORITY 104 8
50 PROCESS_NEXT
60 UPDATE_PRIORITY 103 3
95 JOB_STATUS"""

    tc2_out = """Job 101 submitted at 5 ms
Job 102 submitted at 10 ms
Job 103 submitted at 15 ms
Job 104 submitted at 20 ms
Job 105 submitted at 25 ms
Job 101 priority updated to 9
Job 101 started at 35 ms
ERROR: Job 101 priority cannot be updated while status is RUNNING
Job 104 priority updated to 8
Job 104 started at 50 ms
Job 103 priority updated to 3
JOB STATUS
Job     Submitted   Started   Actual Time   Completed   Status
101     5           35        55            90          COMPLETED
102     10          null      null          null        WAITING
103     15          null      null          null        WAITING
104     20          50        50            100         RUNNING
105     25          null      null          null        WAITING
END JOB STATUS
EXECUTION_ORDER
101 35 90
104 50 100
END_EXECUTION_ORDER
TREE
LEVEL 0: [102]
LEVEL 1: [101]|[104]
LEVEL 2: NULL|NULL|[103]|[105]
END_TREE
INORDER: [101, 102, 103, 104, 105]
MAX_HEAP: [(105,5,60), (103,3,70), (102,4,30)]
TREE_STATS
records=5
height=3
insertions=5
deletions=0
left_rotations=2
right_rotations=0
END_TREE_STATS
HEAP_STATS
size=3
max_size=5
insertions=5
extractions=2
removals=0
priority_updates=3
rebuilds=0
END_HEAP_STATS"""

    tc3_in = """CAPACITY 2
5 SUBMIT 101 3 60 5
10 SUBMIT 102 9 30 10
15 SUBMIT 103 5 90 10
20 PROCESS_NEXT
30 PROCESS_NEXT
40 SUBMIT 104 8 80 5
45 SUBMIT 105 2 10 10
50 SUBMIT 106 6 60 10
55 SHORT_JOBS
57 CANCEL 104
58 PROCESS_NEXT
60 PROCESS_NEXT
160 JOB_STATUS"""

    tc3_out = """Job 101 submitted at 5 ms
Job 102 submitted at 10 ms
Job 103 submitted at 15 ms
Job 102 started at 20 ms
Job 103 started at 30 ms
Job 104 submitted at 40 ms
Job 105 submitted at 45 ms
Job 106 submitted at 50 ms
Scheduling mode changed to SHORT_JOBS
Job 104 cancelled
Job 105 started at 60 ms
Job 106 started at 80 ms
JOB STATUS
Job       Submitted        Started    Actual Time       Completed       Status
101       5                null       null              null            WAITING
102       10               20         40                60              COMPLETED
103       15               30         100               130             COMPLETED
105       45               60         20                80              COMPLETED
106       50               80         70                150             COMPLETED
104       40               null       null              null            CANCELLED
END JOB STATUS
EXECUTION_ORDER
102 20 60
103 30 130
105 60 80
106 80 150
END_EXECUTION_ORDER
TREE
LEVEL 0: [105]
LEVEL 1: [102]|[106]
LEVEL 2: [101]|[103]
END_TREE
INORDER: [101, 102, 103, 105, 106]
MAX_HEAP: [(101,3,60)]
TREE_STATS
records=5
height=3
insertions=6
deletions=1
left_rotations=3
right_rotations=0
END_TREE_STATS
HEAP_STATS
size=1
max_size=4
insertions=6
extractions=4
removals=1
priority_updates=0
rebuilds=1
END_HEAP_STATS"""

    test_data_structures_unit()
    success = True
    success &= run_testcase(1, tc1_in, tc1_out)
    success &= run_testcase(2, tc2_in, tc2_out)
    success &= run_testcase(3, tc3_in, tc3_out)

    if success:
        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉")
    else:
        print("\n❌ SOME TESTS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
