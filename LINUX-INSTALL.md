```
# setup ve directory
cd ~/x/w
git clone https://github.com/hvqzao/ve

# configure ve
./ve -P 2.7.13
# <-- press [Enter] to confirm build settings

cat >.ve <<EOF
PY="py-2.7.13"
VE_BIN="bin"
EOF

# enable ve
. ./ve

# pip update
pip install --upgrade pip

# get report-ng
git clone https://github.com/hvqzao/report-ng

# meet report-ng requirements
pip install cx_freeze==4.3.3
pip install lxml==3.3.5
# no wxpython
pip install pillow
pip install pyaml
pip install beautifulsoup==3.2.1

cd report-ng
```

# NOT TESTED:
#
# http://stackoverflow.com/questions/32284938/how-to-properly-install-wxpython
# https://wiki.wxpython.org/How%20to%20install%20wxPython#Installing_wxPython-Phoenix_using_pip
#
# pip install --upgrade --trusted-host wxpython.org --pre -f http://wxpython.org/Phoenix/snapshot-builds/ wxPython_Phoenix 

