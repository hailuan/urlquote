"""urlquote transform a url to a file name and upside down.

Usage:

>>> # add line
>>> # /tmp/test_urlquote/fat.fs    /tmp/test_urlquote/fat32    vfat     user,noauto,nofail    0    0
>>> # in /etc/fstab before the test
>>> # Test setup
>>> import os
>>> import subprocess
>>> from shutil import copy2
>>> # A directory stock contents of url
>>> dirtmp = '/tmp/test_urlquote/'
>>> dir_fat32 = dirtmp + 'fat32/'
>>> os.makedirs(dir_fat32)
>>> copy2('fat32/fat.fs', dirtmp)
'/tmp/test_urlquote/fat.fs'
>>> # mount a FAT32
>>> cmd = ['mount', dirtmp + 'fat.fs']
>>> output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
>>> # list url for test
>>> TEST_URLS = [
...     "www.example.com", # sample url
...     "protocol://domain.tld/dir1/dir2/file#fragment?param=value&param2=value", # example sample
...     "http://example.com",  # No trailing /
...     "http://example.com/",  # Trailing /
...     "https://example.com/",  # https
...     "ftp://example.com/",  # ftp
...     "//example.com/",  # No protocol (<- Not sure we should handle this, maybe throw an error)
...     "dtc://example.com/",  # New protocol (I think we should handle this one, it is a valid URL after all)
...     "http://example.com/_toto",  # 1 child
...     "http://example.com//toto",  # Double slash
...     "http://example.com/_toto/_titi" ,#child of child
...     "http://example.com/_toto/_titi/" , # Trailing /
...     "http://example.com/toto#subsection",  # Fragment identifier
...     "http://example.com/verylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongname",  # Very long name
...     "http://example.com/toto?param",  # Param
...     "http://example.com/toto?param=value",  # Param and value
...     "http://example.com/toto?param=value&param2=toto",  # Multiple params
...     "http://example.com/toto%20tata",  # Space in a name
...     "https://en.wiktionary.org/wiki/Ῥόδος", # IRI
...     "https://www.google.fr/search?q=python+create+a+file+systeme+FAT32&ie=utf-8&oe=utf-8&gws_rd=cr&ei=liE4WdHoGIi_aL3ru4gP#q=les+exemple+url",
...     "baike.baidu.com/item/刘亦菲", # word special
...     "http://baike.baidu.com/item/%E5%88%98%E4%BA%A6%E8%8F%B2/136156", # baike.baidu.com/item/刘亦菲/136156, url with percent key
...     "https://www.google.fr/search?q=fsq&ie=utf-8&oe=utf-8&gws_rd=cr&ei=2Rw4WZiIGcy0aaHmsqgO#q=/", # / is a value
...     "https://www.google.fr/search?q=fsq&ie=utf-8&oe=utf-8&gws_rd=cr&ei=2Rw4WZiIGcy0aaHmsqgO#q=/////", # several '/'
...     "https://www.google.fr/search?q=fsq&ie=utf-8&oe=utf-8&gws_rd=cr&ei=2Rw4WZiIGcy0aaHmsqgO#q=%2F",
...     "https://www.google.fr/search?q=fsq&ie=utf-8&oe=utf-8&gws_rd=cr&ei=2Rw4WZiIGcy0aaHmsqgO#q=%252F//", # percent encode 2 time
...     "localhost:8000/?request=https://abc/Ῥόδος?file#fragment?param=value&param2=value", # parameter's value is a url
...     "http://localhost:8000/proxy?request=https://abc.xyz/Ῥόδος?file#fragment?param=value&param2=value", # parameter's value is a url with special key
...     "https://us.hidester.com/proxy.php?u=eJwBQgC9%2F3M6NTg6Im9RWVLInEER%2B2QoY7hjryhadaL9BZy6uSFMTxIuZAvn8ahUZO46XG%2FzapDJHAAlYy1h%2BLIEMcRI3FUiO5NWG%2B0%3D&b=7", # proxy encode an url to base64
...     "https://www.google.fr/search?q=google+https://abc/%E1%BF%AC%CF%8C%CE%B4%CE%BF%CF%82%3Ffile%23fragment%3Fparam%3Dvalue%26param2%3Dvalue&ie=utf-8&oe=utf-8&gws_rd=cr&ei=OnM5Wc3mAYL7adKFvLgP#q=https://abc/%E1%BF%AC%CF%8C%CE%B4%CE%BF%CF%82?file%23fragment?param%3Dvalue%26param2%3Dvalue" # google search a url with percent encode
... ]
>>> # End test setup
>>>
>>> # invalid name in a FAT32
>>> try:
...     os.makedirs(dir_fat32 + 'a>b')
... except OSError:
...     raise ValueError('Invalid argument')
Traceback (most recent call last):
...
ValueError: Invalid argument
>>> # import urlquote
>>> url = 'protocol://domain.tld/dir1/dir2/file#fragment?param=value&param2=value'
>>> # Transform an url to a path
>>> url2filename(url)
'protocol%3A%2F%2F/domain.tld%2F/dir1%2F/dir2%2F/file/#fragment/%3Fparam/=value/&param2/_=value'
>>> # url2filepath is bijective and filepath2url is function reverse of url2filepath
>>> # Test property bijective of function url2filename
>>> for url in TEST_URLS:
...     assert url == filename2url(url2filename(url)), "Bijective false " + url
>>> # Test if all url is valid in FAT32
>>> # Create url file
>>> for url in TEST_URLS:
...     filename = dir_fat32 + url2filename(url)
...     if not os.path.exists(os.path.dirname(filename)):
...         os.makedirs(os.path.dirname(filename))
...     with open(filename, 'w') as f:
...         _ignore = f.write(url)
>>> # Read a content of url from directory
>>> for url in TEST_URLS:
...     filename = dir_fat32 + url2filename(url)
...     with open(filename, 'r') as f:
...         assert f.read() == url, "Can't read " + url
>>>
>>> # close the FAT32
>>> cmd = ['umount', dirtmp + 'fat.fs']
>>> output = subprocess.check_output(cmd,stderr=subprocess.STDOUT)
>>> cmd = ['rm', '-rf', dirtmp]
>>> output = subprocess.check_output(cmd)
"""
import urllib.parse
import re

path_separator = '/'
max_length = 254


def split_without_remove(url, sep):
    """Split a string but not remove the key of separator.
    The key of separator will be located as suffix of element in list.

    :param url: type string
    :param sep: type string, separator
    :return: a list of string


    >>> split_without_remove('a/b/c', '/')
    ['a/', 'b/', 'c']
    >>> split_without_remove('a/b/c/', '/')
    ['a/', 'b/', 'c/']
    """
    splited_url = url.split(sep)
    if len(splited_url) > 1:
        splited_url = [e + sep for e in splited_url[:-1]] + [splited_url[-1]]
        if splited_url[-1] == "":
            del splited_url[-1]
    return splited_url


def split_without_remove_prefix(url, sep):
    """Same as split_without_remove but the key of separator
    will be located as prefix of element in list.

    >>> split_without_remove_prefix('&a=b/', '=')
    ['&a', '=b/']
    """
    splited_url = url.split(sep)
    if len(splited_url) > 1:
        splited_url = [splited_url[0]] + [sep + e for e in splited_url[1:]]
        if splited_url[0] == "":
            del splited_url[0]
    return splited_url


def paramurl_split(part_of_url):
    """Separate all parameter in url and their values.

    >>> paramurl_split('file#fragment?param=value&param2=value')
    ['file', '#fragment', '?param', '=value', '&param2', '=value']
    """
    list_param_url = [part_of_url]
    keys_special = ['?', '&', '=', '#']
    for key in keys_special:
        temp_list = []
        for elt in list_param_url:
            temp_list += split_without_remove_prefix(elt, key)
        list_param_url = temp_list[:]
    return list_param_url


def max_len_cut(li):
    """Split the last element of list of string into many
    separates parts whose length is 254 maximum
    """
    if len(li[-1]) <= max_length:
        return li
    return max_len_cut(
        li[:-1] + [li[-1][:max_length]] + [li[-1][max_length:]])


def is_protocol(s):
    """Test if a string is a prefix of protocol."""
    # a protocole in url is a form like 'protocol://'
    test = re.compile('^\w+://')
    return bool(test.search(s))


def percent_quote(chain, characters='%"*:<>?/\\|\t\n\r\x0b\x0c'):
    """Quote special character to percent-encode in a chain of string.

    >>> percent_quote('élément spécial : & / ^ #', '/')
    'élément spécial : & %2F ^ #'
    """
    for c in characters:
        chain = chain.replace(c, urllib.parse.quote(c, safe=''))
    return chain


def url2filename(url):
    """Return the list of path's element of a url in directory local.
    """
    # separate protocole if exists
    l = split_without_remove(url, '//')
    # step 1: separate protocol, then separate all elt with '/'
    url_split_step1 = [elt for l1 in [split_without_remove(l1, '/')
                                      if not is_protocol(l1) else [l1]
                                      for l1 in l] for elt in l1]
    # step 2: separate parameters in url and their value
    url_split_step2 = []
    for string in url_split_step1:
        url_split_step2 += paramurl_split(string)
    # step 3: encode url
    url_quote = []
    # quote url with percent encode then treat all elements whose leght > 255
    for string in [percent_quote(elt) for elt in url_split_step2]:
        url_quote += max_len_cut([string])
    # file system of linux does not accept a basename of file have same name as
    # a folder
    # add a prefix '_' in basename of file for differentiate
    url_quote[-1] = '_' + url_quote[-1]
    return path_separator.join(url_quote)


def filename2url(filename):
    """Decode a filename to an url.
    """

    filename = filename.split(path_separator)
    filename[-1] = filename[-1][1:]
    # decode the path
    return urllib.parse.unquote("".join(filename))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
