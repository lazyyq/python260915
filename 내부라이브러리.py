#내부라이브러리.py

import os
import glob

print(f"운영체제이름:{os.name}")
print(f"환경변수:{os.environ}")

# r: raw string notation
fName=r"/opt/homebrew/bin/python3.13"

if os.path.exists(fName):
    print(f"{fName} 파일의 크기: {os.path.getsize(fName)} 바이트")
else:
    print(f"{fName} does not exist.")

# print(glob.glob(r"/Users/kykint/Desktop/work/*.py"))
for item in glob.glob(r"/Users/kykint/Desktop/work/*.py"):
    print(item)
