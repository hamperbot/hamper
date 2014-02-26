Trouble Installing
==================

### Problem: pyopenssl has issues compiling in Ubuntu

If `pip install -r requirements.txt` in your virtualenv gives an error like:


```
OpenSSL/crypto/x509.h:17:25: fatal error: openssl/ssl.h: No such file or directory
 #include <openssl/ssl.h>
                         ^
compilation terminated.

```

resulting in the final error

```
error: command 'x86_64-linux-gnu-gcc' failed with exit status 1
````

### Solution: Install libssl-dev

Make sure you have libssl-dev installed from your system's package manager: 

```
$ sudo apt-get install libssl-dev
```
