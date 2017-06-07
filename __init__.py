"""urlquote transform a url to a file path and upside down

Usage:

>>> # Test setup
>>> import tempfile
>>> import os
>>> # A directory stock contents of url
>>> urlcontent_directory = tempfile.TemporaryDirectory()
>>> path_directory = urlcontent_directory.name + 'stock_url'
>>> os.makedirs(path_directory)
>>> # End test setup
>>>
>>> # import urlquote
>>> url_quote = urlquote(path_directory)
>>> url = 'http://gitlab.lan/C3NRD/Ook/issues/3'
>>> # Transform an url to a path
>>> url_quote.url2filepath(url).lstrip(path_directory)
'http%3A%2F%2F/gitlab.lan%2F/C3NRD%2F/Ook%2F/issues%2F/3'
>>> # The parent dicrectory
>>> url_quote.url2filepath(url, -1).lstrip(path_directory)
'http%3A%2F%2F/gitlab.lan%2F/C3NRD%2F/Ook%2F/issues%2F'
>>> # Equivalent
>>> url_quote.parent_directory(url).lstrip(path_directory)
'http%3A%2F%2F/gitlab.lan%2F/C3NRD%2F/Ook%2F/issues%2F'
>>> # The last element of path is the file name
>>> url_quote.url2filename(url)
'3'
>>> # url2filepath is bijective and filepath2url is function reverse of url2filepath
>>> url == url_quote.filepath2url(url_quote.url2filepath(url))
True
"""
import urllib.parse


class urlquote:
    def __init__(self, directory='./', path_separator='/', max_length=254):
        """Initial the urlquote

        change the parametter default for adapt each different OS

        :param directory: type string, the path to the directory where the url file stocked
        :param path_separator: type string, separator of path
        :param max_length: size maximum of name of directory or file in an O.S.
        """

        self.directory = directory.rstrip(path_separator) + path_separator
        self.path_separator = path_separator
        self.max_length = max_length

    def split_without_remove(self, url, sep):
        """Split a string but not remove the key of separator

        :param url: type string
        :param sep: type string, separator
        :return: a list of string
        >>> urlq = urlquote()
        >>> urlq.split_without_remove('a/b/c', '/')
        ['a/', 'b/', 'c']
        >>> urlq.split_without_remove('a/b/c/', '/')
        ['a/', 'b/', 'c/']
        """
        splited_url = url.split(sep)
        if len(splited_url) > 1:
            splited_url = [e + sep
                           for e in splited_url[:-1]] + [splited_url[-1]]
            if splited_url[-1] == "":
                del splited_url[-1]
        return splited_url

    def max_len_cut(self, li):
        """Split the last element of list of string into many
        separates parts whose length is 254 maximum
        """
        if len(li[-1]) <= self.max_length:
            return li
        return self.max_len_cut(
            li[:-1] + [li[-1][:self.max_length]] + [li[-1][self.max_length:]])

    def is_protocol(self, s):
        """Test if a string is a prefix of protocol"""
        return s in ['http://', 'https://', 'ftp://']

    def url2filelistpath(self, url):
        """Return the list of path's element of a url in directory local
        """
        # separate protocole if exists
        l = self.split_without_remove(url, '//')
        # separate with '/'
        url_split = [elt for l1 in [self.split_without_remove(l1, '/')
                                    if not self.is_protocol(l1) else [l1]
                                    for l1 in l] for elt in l1]
        url_quote = []
        # quote url with percent encode then treat all elements whose leght > 255
        for string in [urllib.parse.quote(elt, safe='') for elt in url_split]:
            url_quote += self.max_len_cut([string])
        return url_quote

    def url2filepath(self, url, parent_dir=None):
        """Return a path complete to the file of url
        """
        return self.directory + self.path_separator.join(
            self.url2filelistpath(url)[:parent_dir])

    def parent_directory(self, url):
        """Return the path to 'parent directory' of file of an url"""
        return self.url2filepath(url, -1)

    def url2filename(self, url):
        """Return the file name of url

        !!! the file name is not a path complete
        """
        return self.url2filelistpath(url)[-1]

    def filepath2url(self, path_file, path_separator='/'):
        """Decode a path to an url
        """
        # remove path 'directory'
        if self.directory == path_file[:len(self.directory)]:
            path_file = path_file[len(self.directory):]
        # decode the path
        return urllib.parse.unquote("".join(path_file.split(path_separator)))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
