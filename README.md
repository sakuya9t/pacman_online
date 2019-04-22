# pacman_online

## COMP90020 Distributed Algorithms

| Name          | ID          | Email                           |
| ------------- |:-----------:| -------------------------------:|
| Zijian Wang   | 950618      | zijianw2@student.unimelb.edu.au |
| Nai Wang      | 927209      | naiw1@student.unimelb.edu.au    |
| Leewei Kuo    | 932975      | leeweik1@student.unimelb.edu.au |
| Ivan Chee     | 736901      | ichee@student.unimelb.edu.au    |


## Installation
pip install keyboard

## Execution
python capture.py


## Bug in Python 2.7
Python 2.7 may encounter an error similar to below:
File "C:\Python27\lib\site-packages\keyboard\_winkeyboard.py", line 37, in <module>
  kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
File "C:\Python27\lib\site-packages\keyboard\_winkeyboard.py", line 44, in <module>
  user32 = ctypes.WinDLL('user32', use_last_error=True)
TypeError: LoadLibrary() argument 1 must be string, not unicode

Open the file with kernel32
Change 'kernel32' to b'kernel32'
And 'user32' to b'user32
>> nano /c/Anaconda2/lib/site-packages/keyboard/_winkeyboard.py
