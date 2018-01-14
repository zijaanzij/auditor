# auditor.py
Script for tracking file system changes

### Synopsis
auditor.py snap PATH [--filename NAME]  
auditor.py diff SNAP SNAP  

### Description
`autidor.py` when called with `snap` argument, saves the state of the file system PATH as a json SNAP file which contains a list of named entries with a metadata for each file entry.  
`autidor.py` when called with `diff` argument, compares two SNAP files and reports the changes.

#### snap mode example

```
$ auditor.py snap D:\\simple_http_server --filename initial.json
Snapshot was saved to "initial.json"
```

#### diff mode example

```
$ auditor.py diff initial.json changed.json
Element D:\simple_http_server\src was changed
Element D:\simple_http_server\src\AdvancedHttpServer.java was added
Element D:\simple_http_server\src\EventListener.java was added
Element D:\simple_http_server\src\SimpleHttpServer.java was removed
Element D:\simple_http_server\src\test.html was changed
```

### Compatibility

Python 3