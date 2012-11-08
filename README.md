## fbx-to-threejs

Utility for converting FBX model files to Three.js JSON format files

## Dependencies

* Requires Autodesk FBX SDK Python 2013.3 bindings. 

```
You can download the python bindings from the Autodesk website: 
  http://usa.autodesk.com/fbx/
```

* Requires Python 2.6 or 3.1 (The FBX SDK requires one of these versions)

``` bash
sudo apt-get install build-essential
wget http://www.python.org/ftp/python/2.6.8/Python-2.6.8.tar.bz2
tar jxf ./Python-2.6.8.tar.bz2
cd ./Python-2.6.8
./configure --prefix=/opt/python2.6.8 && make && make install
```

