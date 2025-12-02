def parent(i):
    return (i - 1) // 2

def left_child(i):
    return 2 * i + 1

def right_child(i):
    return 2 * i + 2

def swap(heap, i, j):
    heap[i], heap[j] = heap[j], heap[i]

def heapify_up(heap, i):
    if i == 0:
        return
    p = parent(i)
    if heap[i]['priority'] < heap[p]['priority']:
        swap(heap, i, p)
        heapify_up(heap, p)

def heapify_down(heap, i):
    smallest = i
    left = left_child(i)
    right = right_child(i)
    
    if left < len(heap) and heap[left]['priority'] < heap[smallest]['priority']:
        smallest = left
    
    if right < len(heap) and heap[right]['priority'] < heap[smallest]['priority']:
        smallest = right
    
    if smallest != i:
        swap(heap, i, smallest)
        heapify_down(heap, smallest)

def enqueue(heap, pasien):
    heap.append(pasien)
    heapify_up(heap, len(heap) - 1)

def dequeue(heap):
    if is_empty(heap):
        return None
    
    if len(heap) == 1:
        return heap.pop()
    
    root = heap[0]
    heap[0] = heap.pop()
    heapify_down(heap, 0)
    return root

def peek(heap):
    return heap[0] if not is_empty(heap) else None

def is_empty(heap):
    return len(heap) == 0

def size(heap):
    return len(heap)

def get_all(heap):
    return sorted(heap, key=lambda x: x['priority'])