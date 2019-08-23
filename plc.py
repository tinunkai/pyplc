import socket
import re

PORT = 5002

def read_words_fx3u(device_code, client, start_digit, end_digit, port=PORT, dic=True):
    '''
    '''
    digit_num = end_digit - start_digit + 1
    #cmd = '01'      'ff'   '0a00'  '00000000' '2052'      '40'   '00'
    #     |subheader|pc num|timeout|device num|device code|digits|end
    cmd = '01ff0a00'\
        + reverse_per_two_char('{:0=8x}'.format(start_digit))\
        + device_code\
        + reverse_per_two_char('{:0=4x}'.format(digit_num))\
        + '00'

    msg = bytes.fromhex(cmd)
    client.send(msg)
    res = client.recv(4096).hex()
    if res[:4] != '8100':
        return None
    values = [int(reverse_per_two_char(x), 16) for x in re.findall('....', res[4:])]
    if dic:
        return dict(zip(range(start_digit, start_digit + digit_num), values))
    else:
        return values

def read_rs_fx3u(client, start_digit, end_digit, port=PORT, dic=True):
    return read_words_fx3u('2052', client, start_digit, end_digit, port, dic)

def read_register(host, start_digit, digit_num=1, port=PORT, dic=True):
    '''
    Example:
        read D400 single word:
        read_register(400, 1)
    '''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    cmd = '500000ffff03000c00100001040000'\
            + reverse_per_two_char('{:0=6x}'.format(start_digit))\
            + 'a8' + reverse_per_two_char('{:0=6x}'.format(digit_num))
    msg = bytes.fromhex(cmd)
    client.send(msg)
    res = client.recv(1024).hex()
    if dic:
        return {start_digit: int(reverse_per_two_char(res[-4*digit_num:]), 16)}
    else:
        return int(reverse_per_two_char(res[-4*digit_num:]), 16)

def read_bit(device_code, host, start_digit, digit_num=1, port=PORT, dic=True):
    read_digit = start_digit
    while read_digit % 16 != 0:
        read_digit -= 1
    idx = start_digit - read_digit + 1
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    cmd = '500000ffff03000c00100001040000'\
            + reverse_per_two_char('{:0=6x}'.format(read_digit))\
            + device_code + reverse_per_two_char('{:0=6x}'.format(digit_num))
    msg = bytes.fromhex(cmd)
    client.send(msg)
    res = client.recv(1024).hex()
    if dic:
        return {start_digit: int(format(int(reverse_per_two_char(res[-4*digit_num:]), 16), '016b')[-idx])}
    else:
        return int(format(int(reverse_per_two_char(res[-4*digit_num:]), 16), '016b')[-idx])

def read_bits(device_code, host, start_digit, end_digit, port=PORT, dic=True):
    '''
    Example:
        read D400 to D409 single word:
        read_register(400, 409)
    '''
    digit_num = end_digit - start_digit + 1
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    cmd = '500000ffff03000c00100001040000'\
            + reverse_per_two_char('{:0=6x}'.format(start_digit))\
            + device_code + reverse_per_two_char('{:0=6x}'.format(digit_num))
    msg = bytes.fromhex(cmd)
    client.send(msg)
    res = client.recv(512+4*digit_num).hex()
    values = [int(reverse_per_two_char(x), 16) for x in re.findall('....', res[-4*digit_num:])]
    if dic:
        return dict(zip(range(start_digit, start_digit + digit_num), values))
    else:
        return values

def read_x(host, start_digit, digit_num=1, port=PORT, dic=True):
    '''
    Example:
        read X400 single word:
        read_x('192.168.1.202', 0x400)
    '''
    return read_bit('9c', host, start_digit, digit_num, port, dic)

def read_y(host, start_digit, digit_num=1, port=PORT, dic=True):
    return read_bit('9d', host, start_digit, digit_num, port, dic)

def read_zrs(device_code, host, start_digit, end_digit, port=PORT, dic=True):
    return read_bits('b0', host, start_digit, end_digit, port, dic)

def read_registers(host, start_digit, end_digit, port=PORT, dic=True):
    '''
    Example:
        read D400 to D409 single word:
        read_register(400, 409)
    '''
    digit_num = end_digit - start_digit + 1
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    cmd = '500000ffff03000c00100001040000'\
            + reverse_per_two_char('{:0=6x}'.format(start_digit))\
            + 'a8' + reverse_per_two_char('{:0=6x}'.format(digit_num))
    msg = bytes.fromhex(cmd)
    client.send(msg)
    res = client.recv(512+4*digit_num).hex()
    values = [int(reverse_per_two_char(x), 16) for x in re.findall('....', res[-4*digit_num:])]
    if dic:
        return dict(zip(range(start_digit, start_digit + digit_num), values))
    else:
        return values

def reverse_per_two_char(chars):
    '''
    reverse '010203' to '030201'
    '''
    return ''.join(reversed(re.findall('..?', chars)))

def is_open(ip, port=PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False
