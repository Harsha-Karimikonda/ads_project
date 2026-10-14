# COP 5536 Fall 2026 - Programming Project
# Makefile for Job Scheduler Simulator

PYTHON = python3

.PHONY: all clean test report pack

all:
	@chmod +x jobScheduler.py
	@# Create ./jobScheduler wrapper script for convenience
	@echo '#!/bin/sh' > jobScheduler
	@echo 'python3 jobScheduler.py "$$@"' >> jobScheduler
	@chmod +x jobScheduler
	@$(PYTHON) -m py_compile job.py avl_tree.py max_heap.py jobScheduler.py
	@echo "Build successful. Run with: python3 jobScheduler.py <input_file> or ./jobScheduler <input_file>"

test: all
	@$(PYTHON) test_scheduler.py

report:
	@$(PYTHON) generate_report.py

pack: all report
	@rm -f submission.zip
	@zip -j submission.zip job.py avl_tree.py max_heap.py jobScheduler.py Makefile report.pdf
	@echo "Created submission.zip ready for submission."

clean:
	@rm -rf __pycache__ *.pyc jobScheduler *_output_file.txt test1.txt test2.txt test3.txt submission.zip
	@echo "Cleaned generated files."
