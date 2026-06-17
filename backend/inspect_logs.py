import os
import json

log_path = r"C:\Users\LENOVO\.gemini\antigravity-ide\brain\7798c166-92ea-4b2d-bf12-6ac302bfe103\.system_generated\logs\transcript.jsonl"
print("Checking log path:", log_path)
if os.path.exists(log_path):
    print("Log exists! Reading last 50 lines...")
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print("Total lines in log:", len(lines))
    for i in range(max(0, len(lines)-10), len(lines)):
        try:
            data = json.loads(lines[i])
            print(f"Step {data.get('step_index')}, Type: {data.get('type')}, Source: {data.get('source')}")
            content = data.get('content', '')
            if content:
                print("Content length:", len(content))
                print("Content preview:", content[:500])
        except Exception as e:
            print("Error parsing line:", e)
else:
    print("Log does not exist.")
