#!/usr/bin/env python3
# coding: utf-8

import sys
import ui

SYMBOL_BACKSPACE = '<'
SYMBOL_ENTER = '>'
SYMBOL_SPACE = ' '

class CinFile:
    def __init__(self, cin_file_name):
        self.cname = None
        self.__key2char = dict()
        self.__char2key = dict()
        self.__key2symbol = dict()
        self.__symbol2key = dict()
        self.end_keys = " "
        self.end_symbols = " "

        with open(cin_file_name, encoding='utf-8') as fin:

            # get cname
            for line in fin:
                if line.startswith("%cname "):
                    self.cname = line.rstrip().split(" ")[1]
                    break

            # find keyname or endkey
            line = fin.readline()
            keyname_begin = line.startswith("%keyname begin")
            endkey_line = line.startswith("%endkey ")
            while (not (keyname_begin or endkey_line)):
                line = fin.readline()
                keyname_begin = line.startswith("%keyname begin")
                endkey_line = line.startswith("%endkey ")

            if (endkey_line):
                index = line.find(' ')
                self.end_keys = line[index:]
                # bypass until keyname section
                while (not fin.readline().startswith("%keyname begin")):
                    pass

            # read keyname
            for line in fin:
                if line.startswith("%keyname end"):
                    break
                key, symbol = line.rstrip().split(" ")
                self.__key2symbol[key] = symbol
                self.__symbol2key[symbol] = key

            # bypass until chardef section
            while (not fin.readline().startswith("%chardef begin")):
                pass

            # read chardef
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

            for key, symbol in self.__key2symbol.items():
                if (key in self.end_keys):
                    self.end_symbols += self.__key2symbol[key]

    def lookup(self, key, symbol=True):
        if (symbol):
            key = "".join([self.__symbol2key[s] for s in key])
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


class IMDictDoc:
    def __init__(self, kb_cin_file_name, res_cin_file_name):
        self.kb_cin = CinFile(kb_cin_file_name)
        self.res_cin = CinFile(res_cin_file_name)
        self.kb_symbols = [
            "ㄅㄉˇˋㄓˊ˙ㄚㄞㄢ<",
            "ㄆㄊㄍㄐㄔㄗㄧㄛㄟㄣㄦ",
            # "ㄇㄋㄎㄑㄕㄘㄨㄜㄠㄤ>",
            "ㄇㄋㄎㄑㄕㄘㄨㄜㄠㄤ",
            "ㄈㄌㄏㄒㄖ ㄙㄩㄝㄡㄥ",
            ]


class IMDictView:
    def __init__(self, doc, lookup_view_pyui):
        self.__doc = doc
        self.lookup_view = ui.load_view(lookup_view_pyui)
        self.__inputs_lab = self.lookup_view['inputs_lab']
        self.__results_tv = self.lookup_view['results_tv']

    def load_keyboard_onto_view(self, symbols, key_margin=4, key_radius=4):
        kb_view = self.lookup_view['keyboard']

        num_col = max([len(row) for row in symbols])
        key_width = kb_view.width / num_col - key_margin
        key_height = kb_view.height / len(symbols) - key_margin

        for i in range(len(symbols)):
            row = symbols[i]
            for j in range(len(row)):
                symbol = row[j]
                if (symbol == SYMBOL_BACKSPACE):
                    title = '🔙'
                elif (symbol == SYMBOL_ENTER):
                    title = '🔍'
                elif (symbol == SYMBOL_SPACE):
                    title = '⚪️'
                else:
                    title = symbol
                b = ui.Button(title=title)
                b.width = key_width
                b.height = key_height
                b.center = (
                    (key_width + key_margin) * (j + 0.5),
                    (key_height + key_margin) * (i + 0.5)
                    )
                b.flex = 'WHLRTB'
                b.border_width = 1
                b.border_color = 'black'
                b.corner_radius = key_radius
                b.name = symbol
                b.action = self.__button_action
                kb_view.add_subview(b)

    def __button_action(self, sender):
        symbol = sender.name
        if (symbol == SYMBOL_BACKSPACE):
            # backspace
            self.__inputs_lab.text = self.__inputs_lab.text[:-1]
        elif (symbol == SYMBOL_ENTER or symbol in self.__doc.kb_cin.end_symbols):
            # lookup
            if (symbol != SYMBOL_ENTER and symbol != SYMBOL_SPACE):
                self.__inputs_lab.text += symbol
            inputs = self.__inputs_lab.text
            query_chars = self.__doc.kb_cin.lookup(inputs)
            query_results = []
            for c in query_chars:
                rlookup = self.__doc.res_cin.rlookup(c)
                if (rlookup):
                    res = " / ".join(rlookup)
                else:
                    res = "(unknown)"
                line = "{}: {}".format(c, res)
                query_results.append(line)
            self.__results_tv.text = "\n".join(query_results)
        else:
            self.__inputs_lab.text += symbol

def main():
    doc = IMDictDoc('bopomofo.cin', 'cangjie.cin')
    view = IMDictView(doc, 'lookup')
    view.load_keyboard_onto_view(doc.kb_symbols)
    view.lookup_view.present('fullscreen')

if __name__ == '__main__':
    main()
