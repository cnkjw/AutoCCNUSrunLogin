#!/bin/python
# -*- coding: utf-8 -*-

from tenacity import retry, stop_after_attempt, wait_fixed
from urllib.request import urlopen
import hmac
import hashlib
import re
import time
import json
import random
import requests
import js2py as j2p
from urllib.parse import quote


################################################################################
# 0. 常量
# ------------------------------------------------------------------------------

# 指定用户名和密码
my_username = "username" # 用户名
my_passwd = "passwd"     # 密码

# 重试间隔
retry_interval = 30 # second

# 不要修改
jQuery_version = '1.12.4'

# 加密常量
ac_id = 1
srun_n = 200
srun_type = 1
enc_ver = "srun_bx1"

################################################################################
# 1. 编解码工具
# ------------------------------------------------------------------------------


def get_md5(password, token):
    return hmac.new(token.encode(), password.encode(), hashlib.md5).hexdigest()


def get_sha1(value):
    return hashlib.sha1(value.encode()).hexdigest()


base64 = j2p.EvalJs()
base64.execute('''var _PADCHAR = "=", _ALPHA = "LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA";
    function _getbyte(s, i) {
        var x = s.charCodeAt(i);
        if (x > 255) {
            throw "INVALID_CHARACTER_ERR: DOM Exception 5"
        }
        return x
    }
    function _encode(s) {
        if (arguments.length !== 1) {
            throw "SyntaxError: exactly one argument required"
        }
        s = String(s);
        var i, b10, x = [], imax = s.length - s.length % 3;
        if (s.length === 0) {
            return s
        }
        for (i = 0; i < imax; i += 3) {
            b10 = (_getbyte(s, i) << 16) | (_getbyte(s, i + 1) << 8) | _getbyte(s, i + 2);
            x.push(_ALPHA.charAt(b10 >> 18));
            x.push(_ALPHA.charAt((b10 >> 12) & 63));
            x.push(_ALPHA.charAt((b10 >> 6) & 63));
            x.push(_ALPHA.charAt(b10 & 63))
        }
        switch (s.length - imax) {
            case 1:
                b10 = _getbyte(s, i) << 16;
                x.push(_ALPHA.charAt(b10 >> 18) + _ALPHA.charAt((b10 >> 12) & 63) + _PADCHAR + _PADCHAR);
                break;
            case 2:
                b10 = (_getbyte(s, i) << 16) | (_getbyte(s, i + 1) << 8);
                x.push(_ALPHA.charAt(b10 >> 18) + _ALPHA.charAt((b10 >> 12) & 63) + _ALPHA.charAt((b10 >> 6) & 63) + _PADCHAR);
                break
        }
        return x.join("")
    }
''')

encode = j2p.EvalJs()
encode.execute('''
function s(a, b) {
    var c = a.length;
    var v = [];

    for (var i = 0; i < c; i += 4) {
        v[i >> 2] = a.charCodeAt(i) | a.charCodeAt(i + 1) << 8 | a.charCodeAt(i + 2) << 16 | a.charCodeAt(i + 3) << 24;
    }

    if (b)
        v[v.length] = c;
    return v;
}
function l(a, b) {
    var d = a.length;
    var c = d - 1 << 2;

    if (b) {
        var m = a[d - 1];
        if (m < c - 3 || m > c)
            return null;
        c = m;
    }

    for (var i = 0; i < d; i++) {
        a[i] = String.fromCharCode(a[i] & 0xff, a[i] >>> 8 & 0xff, a[i] >>> 16 & 0xff, a[i] >>> 24 & 0xff);
    }

    return b ? a.join('').substring(0, c) : a.join('');
}
function encode(str, key) {
    if (str === '')
        return '';
    var v = s(str, true);
    var k = s(key, false);
    if (k.length < 4)
        k.length = 4;
    var n = v.length - 1, z = v[n], y = v[0], c = 0x86014019 | 0x183639A0, m, e, p, q = Math.floor(6 + 52 / (n + 1)), d = 0
    while (0 < q--) {
        d = d + c & (0x8CE0D9BF | 0x731F2640);
        e = d >>> 2 & 3;

        for (p = 0; p < n; p++) {
            y = v[p + 1];
            m = z >>> 5 ^ y << 2;
            m += y >>> 3 ^ z << 4 ^ (d ^ y);
            m += k[p & 3 ^ e] ^ z;
            z = v[p] = v[p] + m & (0xEFB8D130 | 0x10472ECF);
        }

        y = v[0];
        m = z >>> 5 ^ y << 2;
        m += y >>> 3 ^ z << 4 ^ (d ^ y);
        m += k[p & 3 ^ e] ^ z;
        z = v[n] = v[n] + m & (0xBB390742 | 0x44C6F8BD);
    }
    
    return l(v, false);
}''')

################################################################################

################################################################################
# 2. 请求函数
# ------------------------------------------------------------------------------


def now_milliseconds():
    # 获取 JS 形式的时间
    return int(time.time() * 1000)


def create_jQuery_header():
    return 'jQuery' + (jQuery_version+'{:.16f}'.format(random.random())).replace('.', '') + '_' + str(now_milliseconds())


def get_rad_userinfo(jQuery_header):
    rad_user_info_headers = {
        'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': 'lang=zh-CN',
        'DNT': '1',
        'Host': 'portal.ccnu.edu.cn',
        'Referer': 'https://portal.ccnu.edu.cn/srun_portal_pc?ac_id=1&theme=pro',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    rad_user_info_url = 'https://portal.ccnu.edu.cn/cgi-bin/rad_user_info?callback={}&_={}'
    request_rad_user_info = requests.get(url=rad_user_info_url.format(
        jQuery_header, now_milliseconds()), headers=rad_user_info_headers)
    rad_user_info_str_dict = re.search(
        '(?<='+jQuery_header+'\\().+(?=\\))', request_rad_user_info.text)
    return eval(rad_user_info_str_dict.group())


def get_challenge(jQuery_header, rad_user_info, username):
    get_challenge_headers = {
        'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': 'lang=zh-CN',
        'DNT': '1',
        'Host': 'portal.ccnu.edu.cn',
        'Referer': 'https://portal.ccnu.edu.cn/srun_portal_pc?ac_id=1&theme=pro',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    get_challenge_url = 'https://portal.ccnu.edu.cn/cgi-bin/get_challenge?callback={}&username={}&ip={}&_={}'.format(
        jQuery_header, username, rad_user_info['client_ip'], now_milliseconds()
    )
    request_get_challenge = requests.get(
        url=get_challenge_url, headers=get_challenge_headers)
    get_challenge_str_dict = re.search(
        '(?<='+jQuery_header+'\\().+(?=\\))', request_get_challenge.text)
    return eval(get_challenge_str_dict.group())


def create_userinfo(token, username, passwd, ip, ac_id=ac_id, enc=enc_ver):
    info = {
        "username": username,
        "password": passwd,
        "ip": ip,
        "acid": str(ac_id),
        "enc_ver": enc
    }
    info = json.dumps(info, separators=(',', ':'))
    return r"{SRBX1}" + base64._encode(encode.encode(info, token))


def create_passwd(passwd, token):
    hmd5 = get_md5(passwd, token)
    return r'{MD5}' + hmd5


def create_chksum(token, username, passwd, ip, info, ac_id=ac_id, n=srun_n, type_=srun_type):
    hmd5 = get_md5(passwd, token)

    info_str = token + username
    info_str += token + hmd5 + token + str(ac_id)
    info_str += token + ip + token + str(n)
    info_str += token + str(type_) + token + info
    return get_sha1(info_str)


def call_srun_portal(jQuery_header, challenge_info, username, password):
    srun_portal_headers = {
        'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': 'lang=zh-CN',
        'DNT': '1',
        'Host': 'portal.ccnu.edu.cn',
        'Referer': 'https://portal.ccnu.edu.cn/srun_portal_pc?ac_id=1&theme=pro',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    token = challenge_info['challenge']
    ip = challenge_info["client_ip"]
    md5_passwd = quote(create_passwd(password, token), 'utf-8')
    encoded_info = create_userinfo(
        token, username, password, ip, ac_id, enc_ver)
    chksum = create_chksum(token, username, password, ip,
                           encoded_info, ac_id, srun_n, srun_type)

    srun_portal_url = 'https://portal.ccnu.edu.cn/cgi-bin/srun_portal?callback={}&action=login&username={}&password={}&os=Windows+10&name=Windows&double_stack=0&chksum={}&info={}&ac_id={}&ip={}&n={}&type={}&_={}'.format(
        jQuery_header, username, md5_passwd, chksum, quote(encoded_info, 'utf-8'), ac_id, ip, srun_n, srun_type, now_milliseconds())
    # return srun_portal_url
    request_srun_portal = requests.get(
        url=srun_portal_url, headers=srun_portal_headers)
    get_srun_portal_str_dict = re.search(
        '(?<='+jQuery_header+'\\().+(?=\\))', request_srun_portal.text)
    return eval(get_srun_portal_str_dict.group())


def internet_on():
    try:
        urlopen('https://www.baidu.com/', timeout=10)
        return True
    except:
        return False


@retry(stop=stop_after_attempt(5), wait=wait_fixed(3), reraise=True)
def connect():
    jquery_header = create_jQuery_header()
    raduserinfo = get_rad_userinfo(jquery_header)
    challenge = get_challenge(jquery_header, raduserinfo, my_username)
    call_srun_portal(jquery_header, challenge, my_username, my_passwd)


################################################################################
# 3. 主函数
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    print("自动联网脚本启动...")
    while True:
        time.sleep(retry_interval)
        if internet_on():
            continue
        connect()

