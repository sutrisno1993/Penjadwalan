import os
import re

def parse_allocations() -> list[dict]:
    allocations = []
    md_path = "d:/Jadwal/backend/# DATA ALOKASI JAM PELAJARAN (JP) PER KE.md"
    if not os.path.exists(md_path):
        print(f"File alokasi tidak ditemukan: {md_path}")
        return allocations
    current_classes = []
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("###"):
                heading_content = line[3:].strip()
                heading_content = re.sub(r"\(masing-masing kelas\)", "", heading_content, flags=re.IGNORECASE).strip()
                parts = re.split(r"[\,\&]|(?:\s+dan\s+)|(?:\s+and\s+)", heading_content, flags=re.IGNORECASE)
                current_classes = [p.strip() for p in parts if p.strip()]
                continue
            subject_match = re.match(r"^\*\s+([^:]+):\s+\*\*([0-9]+) JP\*\*", line)
            if subject_match and current_classes:
                subject = subject_match.group(1).strip()
                jp = int(subject_match.group(2))
                for cname in current_classes:
                    allocations.append({"class": cname, "subject": subject, "jp": jp})
    return allocations

allocs = parse_allocations()
print(f"Parsed allocations count: {len(allocs)}")
