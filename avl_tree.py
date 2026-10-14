"""
COP 5536 Fall 2026 Programming Project - Job Scheduler
avl_tree.py: Self-balancing AVL Tree implementation keyed by job_id.
"""

from typing import Optional, List, Any
from job import Job


class AVLNode:
    """
    A single node in the AVL tree storing job_id as key and reference to Job object.
    """
    def __init__(self, key: int, job: Job):
        self.key: int = key
        self.job: Job = job
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height: int = 1


class AVLTree:
    """
    AVL Tree implementation satisfying COP 5536 project requirements.
    - Leaf height is 1, empty subtree height is 0.
    - Balance Factor BF = height(left) - height(right), valid in {-1, 0, 1}.
    - Tracks primitive left and right rotation counts, total insertions, and deletions.
    """
    def __init__(self):
        self.root: Optional[AVLNode] = None
        self.records: int = 0
        self.insertions: int = 0
        self.deletions: int = 0
        self.left_rotations: int = 0
        self.right_rotations: int = 0

    @property
    def height(self) -> int:
        """Returns the height of the tree (0 if empty)."""
        return self._get_height(self.root)

    def _get_height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _get_balance(self, node: Optional[AVLNode]) -> int:
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _update_height(self, node: AVLNode):
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        """Primitive right rotation."""
        self.right_rotations += 1
        x = y.left
        t2 = x.right
        x.right = y
        y.left = t2
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        """Primitive left rotation."""
        self.left_rotations += 1
        y = x.right
        t2 = y.left
        y.left = x
        x.right = t2
        self._update_height(x)
        self._update_height(y)
        return y

    def _rebalance(self, node: AVLNode) -> AVLNode:
        """Checks balance factor and performs primitive rotations as necessary."""
        self._update_height(node)
        bf = self._get_balance(node)

        # Left heavy
        if bf > 1:
            if self._get_balance(node.left) >= 0:
                # LL case: single right rotation
                return self._rotate_right(node)
            else:
                # LR case: left rotation on left child, then right rotation on node
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)

        # Right heavy
        if bf < -1:
            if self._get_balance(node.right) <= 0:
                # RR case: single left rotation
                return self._rotate_left(node)
            else:
                # RL case: right rotation on right child, then left rotation on node
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)

        return node

    def insert(self, key: int, job: Job) -> bool:
        """
        Inserts (key, job) into the AVL Tree.
        Returns True if inserted, False if key already exists.
        """
        inserted = [False]
        self.root = self._insert(self.root, key, job, inserted)
        if inserted[0]:
            self.insertions += 1
            self.records += 1
            return True
        return False

    def _insert(self, node: Optional[AVLNode], key: int, job: Job, inserted: List[bool]) -> AVLNode:
        if not node:
            inserted[0] = True
            return AVLNode(key, job)

        if key < node.key:
            node.left = self._insert(node.left, key, job, inserted)
        elif key > node.key:
            node.right = self._insert(node.right, key, job, inserted)
        else:
            # Duplicate key found
            inserted[0] = False
            return node

        return self._rebalance(node)

    def delete(self, key: int) -> bool:
        """
        Deletes the node with the given key from the AVL Tree.
        Returns True if deleted, False if key was not found.
        """
        deleted = [False]
        self.root = self._delete(self.root, key, deleted)
        if deleted[0]:
            self.deletions += 1
            self.records -= 1
            return True
        return False

    def _min_value_node(self, node: AVLNode) -> AVLNode:
        curr = node
        while curr.left:
            curr = curr.left
        return curr

    def _delete(self, node: Optional[AVLNode], key: int, deleted: List[bool]) -> Optional[AVLNode]:
        if not node:
            return None

        if key < node.key:
            node.left = self._delete(node.left, key, deleted)
        elif key > node.key:
            node.right = self._delete(node.right, key, deleted)
        else:
            deleted[0] = True
            # Node with only one child or no child
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            else:
                # Node with two children: replace with inorder successor (min in right subtree)
                temp = self._min_value_node(node.right)
                node.key = temp.key
                node.job = temp.job
                node.right = self._delete(node.right, temp.key, [False])

        if not node:
            return None

        return self._rebalance(node)

    def find(self, key: int) -> Optional[Job]:
        """Searches for key and returns the associated Job object if found, else None."""
        curr = self.root
        while curr:
            if key == curr.key:
                return curr.job
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def inorder_keys(self) -> List[int]:
        """Returns the list of job_id keys in inorder sequence."""
        res: List[int] = []
        def _traverse(node: Optional[AVLNode]):
            if node:
                _traverse(node.left)
                res.append(node.key)
                _traverse(node.right)
        _traverse(self.root)
        return res

    def inorder_jobs(self) -> List[Job]:
        """Returns the list of Job objects in inorder sequence (increasing Job ID)."""
        res: List[Job] = []
        def _traverse(node: Optional[AVLNode]):
            if node:
                _traverse(node.left)
                res.append(node.job)
                _traverse(node.right)
        _traverse(self.root)
        return res

    def get_level_order_lines(self) -> List[str]:
        """
        Formats tree level by level according to specification:
        TREE
        LEVEL 0: [<key>]
        LEVEL 1: [<key>]|[<key>]
        LEVEL 2: [<key>]|NULL|[<key>]|[<key>]
        ...
        END_TREE
        Trailing NULL entries after the last real node on each level are omitted.
        """
        if not self.root:
            return ["TREE", "END_TREE"]

        lines = ["TREE"]
        current_level: List[Optional[AVLNode]] = [self.root]
        level_idx = 0

        while True:
            if all(n is None for n in current_level):
                break

            # Find index of the last non-null node on this level
            last_real_idx = -1
            for i, node in enumerate(current_level):
                if node is not None:
                    last_real_idx = i

            parts = []
            for i in range(last_real_idx + 1):
                node = current_level[i]
                if node is not None:
                    parts.append(f"[{node.key}]")
                else:
                    parts.append("NULL")

            lines.append(f"LEVEL {level_idx}: " + "|".join(parts))

            # Expand next level
            next_level: List[Optional[AVLNode]] = []
            for node in current_level:
                if node is not None:
                    next_level.append(node.left)
                    next_level.append(node.right)
                else:
                    next_level.append(None)
                    next_level.append(None)

            current_level = next_level
            level_idx += 1

        lines.append("END_TREE")
        return lines
