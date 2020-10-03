# 4CB00

### Installing
- Clone the repository.
- Download and install 64-bit [Python3](https://www.python.org/getit/). Python 3.7.9 is recommended. Make sure to check *Install Python 3 to PATH*
- Install virtualenv. Run this on command prompt. Search `cmd` or `powershell` in the Windows start menu.
```bash
pip install virtualenv
```
- Go to 4CB00 location
```bash
cd C:\path\to\4CB00
```
- Create virtual environment
```bash
virtualenv venv
```
- Activate virtualenv
```bash
# On Windows
venv\Scripts\activate
# On Linux and Mac
source venv/Scripts/activate
```
- Install required packages
```bash
pip install -r requirements.txt
```