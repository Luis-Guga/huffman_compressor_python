class Node:
    def __init__(self, left=None, right=None):
        self._left = left
        self._right = right

    def children(self):
        return (self._left, self._right)

    def __str__(self):
        return f"{self._left}_{self._right}"
