class Node:
    """
    Представляет собой узел двусвязного списка.

    Attributes:
        key (str): Ключ узла.
        value (str): Значение узла.
        prev (Node): Ссылка на предыдущий узел в списке.
        next (Node): Ссылка на следующий узел в списке.
    """
    def __init__(self, key, value):
        """
        Инициализирует узел с заданным ключом и значением.

        Args:
            key (str): Ключ узла.
            value (str): Значение узла.
        """
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    """
    Реализует кэш LRU (Least Recently Used) с использованием двусвязного списка.

    Attributes:
        capacity (int): Максимальная вместимость кэша.
        cache (dict): Словарь для быстрого доступа к элементам кэша.
        head (Node): Голова двусвязного списка.
        tail (Node): Хвост двусвязного списка.
    """
    def __init__(self, capacity: int = 10) -> None:
        self.capacity = capacity
        self.cache = {}  
        self.head = Node(0, 0)  
        self.tail = Node(0, 0) 
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        # Удаляем узел из списка
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add(self, node):
        # Добавляем узел в конец списка (после хвоста)
        prev_node = self.tail.prev
        prev_node.next = node
        self.tail.prev = node
        node.prev = prev_node
        node.next = self.tail

    def get(self, key: str) -> str:
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)  # Удаляем узел из текущего положения
            self._add(node)  # Добавляем узел в конец (обновляем как недавно использованный)
            return node.value
        return ''

    def set(self, key: str, value: str) -> None:
        if key in self.cache:
            self._remove(self.cache[key])  # Удаляем старый узел
        node = Node(key, value)
        self._add(node)  # Добавляем новый узел в конец
        self.cache[key] = node
        if len(self.cache) > self.capacity:
            # Удаляем наименее недавно использованный элемент (голову списка)
            lru_node = self.head.next
            self._remove(lru_node)
            del self.cache[lru_node.key]

    def rem(self, key: str) -> None:
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            del self.cache[key]