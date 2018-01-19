#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import socket
import re

host = '192.168.1.202'
port = 5002

def ReadRegister(num, digit):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    cmd = '500000ffff03000c00100001040000'\
            + ReversePer2Char('{:0=6x}'.format(num))\
            + 'a8' + ReversePer2Char('{:0=6x}'.format(digit))
    msg = bytes.fromhex(cmd)
    client.send(msg)
    res = client.recv(1024).hex()
    return int(ReversePer2Char(res[-4*digit:]), 16)

def ReadRegisters(num, digit):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    cmd = '500000ffff03000c00100001040000'\
            + ReversePer2Char('{:0=6x}'.format(num))\
            + 'a8' + ReversePer2Char('{:0=6x}'.format(digit))
    msg = bytes.fromhex(cmd)
    client.send(msg)
    res = client.recv(512+4*digit).hex()
    return [int(ReversePer2Char(x), 16) for x in re.findall('....', res[-4*digit:])]


def ReversePer2Char(chars):
    return ''.join(reversed(re.findall('..?', chars)))

