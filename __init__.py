"""urlquote transform a url to a file path and upside down

Usage:

>>> # Test setup
>>> import tempfile
>>> import os
>>> # A directory stock contents of url
>>> urlcontent_directory = tempfile.TemporaryDirectory()
>>> path_directory = urlcontent_directory.name + '/'
>>> TEST_URLS = [
...     "http://example.com",  # No trailing /
...     "http://example.com/",  # Trailing /
...     "https://example.com/",  # https
...     "ftp://example.com/",  # ftp
...     "//example.com/",  # No protocol (<- Not sure we should handle this, maybe throw an error)
...     "dtc://example.com/",  # New protocol (I think we should handle this one, it is a valid URL after all)
...     "http://example.com/toto_",  # 1 child
...     "http://example.com//toto",  # Double slash
...     "http://example.com/toto_/titi____"
...     "http://example.com/toto#subsection",  # Fragment identifier
...     "http://example.com/verylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongnameverylongname",  # Very long name
...     "http://example.com/toto?param",  # Param
...     "http://example.com/toto?param=value",  # Param and value
...     "http://example.com/toto?param=value&param2=toto",  # Multiple params
...     "http://example.com/toto%20tata",  # Space in a name
...     "https://en.wiktionary.org/wiki/Ῥόδος", # IRI
...     "https://www.google.fr/search?q=python+create+a+file+systeme+FAT32&ie=utf-8&oe=utf-8&gws_rd=cr&ei=liE4WdHoGIi_aL3ru4gP#q=les+exemple+url",
...     "baike.baidu.com/item/刘亦菲",
...     "http://baike.baidu.com/item/%E5%88%98%E4%BA%A6%E8%8F%B2/136156",
...     "https://www.google.fr/search?q=fsq&ie=utf-8&oe=utf-8&gws_rd=cr&ei=2Rw4WZiIGcy0aaHmsqgO#q=/",
...     "https://www.google.fr/search?q=fsq&ie=utf-8&oe=utf-8&gws_rd=cr&ei=2Rw4WZiIGcy0aaHmsqgO#q=/////",
...     "https://www.google.fr/search?q=fsq&ie=utf-8&oe=utf-8&gws_rd=cr&ei=2Rw4WZiIGcy0aaHmsqgO#q=%2F",
...     "https://www.google.fr/search?q=fsq&ie=utf-8&oe=utf-8&gws_rd=cr&ei=2Rw4WZiIGcy0aaHmsqgO#q=%252F//",
...     "localhost:8000/?request=https://abc/Ῥόδος?file#fragment?param=value&param2=value",
...     "http://localhost:8000/proxy?request=https://abc.xyz/Ῥόδος?file#fragment?param=value&param2=value",
...     "https://us.hidester.com/proxy.php?u=eJwBQgC9%2F3M6NTg6Im9RWVLInEER%2B2QoY7hjryhadaL9BZy6uSFMTxIuZAvn8ahUZO46XG%2FzapDJHAAlYy1h%2BLIEMcRI3FUiO5NWG%2B0%3D&b=7"
... ]
>>> # End test setup
>>>
>>> # import urlquote
>>> url = 'protocol://domain.tld/dir1/dir2/file#fragment?param=value&param2=value'
>>> # Transform an url to a path
>>> url2filename(url)
'protocol%3A%2F%2F/domain.tld%2F/dir1%2F/dir2%2F/file/%23fragment/%3Fparam/%3Dvalue/%26param2/%3Dvalue_'
>>> # url2filepath is bijective and filepath2url is function reverse of url2filepath
>>> test_bijective = True
>>> for url in TEST_URLS:
...     test_bijective = test_bijective and url == filename2url(url2filename(url))
>>> test_bijective
True
>>> test_valide = True
>>> # Create url file
>>> import logging
>>> for url in TEST_URLS:
...     filename = path_directory + url2filename(url)
...     if (not os.path.exists(os.path.dirname(filename))):
...         os.makedirs(os.path.dirname(filename))
...     with open(filename, 'w') as f:
...         logging.debug(url)
...         ignore_buff_cpt = f.write(url)
... # Read a content of url from directory
>>> for url in TEST_URLS:
...     filename = path_directory + url2filename(url)
...     with open(filename, 'r') as f:
...         test_valide = test_valide and f.read() == url
>>> test_valide
True
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


def split_withour_remove_prefix(url, sep):
    """Same as split_without_remove but the key of separator
    will be located as prefix of element in list.
    """
    splited_url = url.split(sep)
    if len(splited_url) > 1:
        splited_url = [splited_url[0]] + [sep + e for e in splited_url[1:]]
        if splited_url[0] == "":
            del splited_url[0]
    return splited_url


def paramurl_split(part_of_url):
    """Separate all parametter in url and their values"""
    list_param_url = [part_of_url]
    keys_special = ['?', '&', '=', '#']
    for key in keys_special:
        temp_list = []
        for elt in list_param_url:
            temp_list += split_withour_remove_prefix(elt, key)
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
    """Test if a string is a prefix of protocol"""
    # a protocole in url is a form like 'protocol://'
    test = re.compile('^\w+://')
    return bool(test.search(s))


def url2filename(url):
    """Return the list of path's element of a url in directory local
    """
    # separate protocole if exists
    l = split_without_remove(url, '//')
    # step 1: separate protocol, then separate all elt with '/'
    url_split_step1 = [elt for l1 in [split_without_remove(l1, '/')
                                      if not is_protocol(l1) else [l1]
                                      for l1 in l] for elt in l1]
    # step 2: separate parametters in url and their value
    url_split_step2 = []
    for string in url_split_step1:
        url_split_step2 += paramurl_split(string)
    # step 3: encode url
    url_quote = []
    # quote url with percent encode then treat all elements whose leght > 255
    for string in [urllib.parse.quote(elt, safe='') for elt in url_split_step2]:
        url_quote += max_len_cut([string])
    # file system of linux does not accept a basename of file have same name as
    # a folder
    # add a suffix '_' in basename of file for differentiate
    url_quote[-1] += '_'
    return path_separator.join(url_quote)


def filename2url(filename):
    """Decode a filename to an url
    """

    filename = filename.split(path_separator)
    filename[-1] = filename[-1][:-1]
    # decode the path
    return urllib.parse.unquote("".join(filename))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
