import sys
import os

sys.path.insert(0, 'd:/Jadwal')
from backend.seeder import parse_allocations

def test():
    allocations = parse_allocations()
    print(f"Total allocations parsed: {len(allocations)}")
    if allocations:
        for i, a in enumerate(allocations[:10]):
            print(f"  {i+1}: {a}")
            
if __name__ == '__main__':
    test()
