#!/usr/bin/env python3
# coding: utf-8

import sys
import ui


class CinFile:

    def __init__(self, cin_file_name):
        self.cname = None
        self.__key2char = dict()
        self.__char2key = dict()
        self.__key2symbol = dict()

        with open(cin_file_name, encoding='utf-8') as fin:

            # get cname
            for line in fin:
                if line.startswith("%cname "):
                    self.cname = line.rstrip().split(" ")[1]
                    break

            # bypass until keyname section
            while (not fin.readline().startswith("%keyname begin")):
                pass

            # read keyname
            for line in fin:
                if line.startswith("%keyname end"):
                    break
                key, symbol = line.rstrip().split(" ")
                self.__key2symbol[key] = symbol

            # bypass until chardef section
            while (not fin.readline().startswith("%chardef begin")):
                pass

            # read xhardef
            for line in fin:
                if line.startswith("%chardef end"):
                    break
                key, char = line.rstrip().split(" ")
                if key not in self.__key2char:
                    self.__key2char[key] = []
                self.__key2char[key].append(char)
                if char not in self.__char2key:
                    self.__char2key[char] = []
                self.__char2key[char].append(key)

    def lookup(self, key):
        if key in self.__key2char:
            return self.__key2char[key]
        else:
            return None

    def rlookup(self, char, symbol=True):
        if char not in self.__char2key:
            return None
        res = []
        for key in self.__char2key[char]:
            if symbol:
                syms = [self.__key2symbol[k] for k in list(key)]
                res.append(''.join(syms))
            else:
                res.append(key)
        return res


def lookup_action(sender):
    '@type sender: ui.Button'
    inputs_tf = sender.superview['inputs']
    results_tv = sender.superview['results']
    res = []
    for char in list(inputs_tf.text):
        keys = cin.rlookup(char)
        key_str = '／'.join(keys)
        r = '{}：{}'.format(char, key_str)
        res.append(r)
    results_tv.text = '\n'.join(res)


if __name__ == '__main__':
    cin = CinFile('cangjie.cin')
    v = ui.load_view()
    v.present('sheet')
