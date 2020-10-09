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

### Usage
Make sure to activate the virtualenv (see [Installing](Installing))\
Run the following command to start the program (for Linux use `python3`)
```bash
python main.py
```

Read the commands printed in the command prompt/terminal

### Output
The program can save the input image file in a form which consists of the rFFT2 values of each color and the full FFT image size.
The rFFT2 data can be compressed and will be stored without zero padding.

### Results
Tested with a RAW image provided from [Signature Edits](https://www.signatureedits.com/free-raw-photos/).

Results using skulls image (*inst = m.n_photo.graphy.NEF*):
Compression<br>(input value) | FFT file size<br>KB | JPG file size<br>KB
------------|-------------|---------
0           | 542.595     | 1.542
10          | 25.275      | 970
60          | 10.076      | 922