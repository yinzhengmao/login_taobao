import json
import os
import re

import requests

s = requests.Session()
#cookies序列化文件
COOKIES_FILE_PATH = 'taobao_login_cookies.txt'

class UsernameLogin:
    def __init__(self, username, ua, TPL_password2):
        '''
        账号登录对象
        :param username:用户名
        :param ua: 淘宝的ua参数
        :param TPL_password2: 加密后的密码
        '''
        #检测是否需要验证码的URL
        self.user_check_url = 'https://login.taobao.com/member/request_nick_check.do?_input_charset=utf-8'
        #验证淘宝用户名密码url
        self.verify_password_url = 'https://login.taobao.com/member/login.jhtml'
        #访问st码url
        self.vst_url = 'https://login.taobao.com/member/vst.htm?st={}'
        #淘宝个人主页
        self.my_taobao_url = 'http://i.taobao.com/my_taobao.htm'

        #淘宝用户名
        self.username = username
        #淘宝关键参数，包含用户浏览器等一些信息，很多地方会用到，从浏览器或者抓包工具中复制，可以重复使用
        self.ua = ua
        #加密后的密码，从浏览器或者抓包工具中复制，可以重复使用
        self.TPL_password2 = TPL_password2

        #请求超时时间
        self.timeout = 3

    def _user_check(self):
        '''
        检测账号是否需要验证码
        :return:
        '''
        data = {
            'username' : self.username,
            'ua' : self.ua
        }
        try:
            response = s.post(self.user_check_url, data = data, timeout = self.timeout)
            response.raise_for_status()
        except Exception as e:
            print('检测是否需要验证码请求失败，原因: ')
            raise e
        needcode = response.json()['needcode']
        print('是否需要滑块验证： {}'.format(needcode))
        return  needcode

    def _verify_password(self):
        '''
        验证用户名密码，并获取st码申请URL
        :return: 验证成功返回st码申请地址
        '''
        verify_password_headers = {
            'connection': 'keep-alive',
            'cache-control': 'max-age=0',
            'origin': 'https://login.taobao.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'referer': 'https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fi.taobao.com%2Fmy_taobao.htm%3Fnekot%3DzOy1wLPqx9q1xMOoaQ%253D%253D1586065410519'
        }
        #登录taobao.com提交的数据，如果登录失败，可以从浏览复制你的form data
        verify_password_data = {
            'TPL_username': self.username,
            #'TPL_password': '',
            'ncoToken': 'a9f87fdd24a9961c18c16ec69a433cf7c236f010',
            'slideCodeShow': 'false',
            'useMobile': 'false',
            'lang': 'zh_CN',
            'loginsite': 0,
            'newlogin': 0,
            'TPL_redirect_url': 'https://i.taobao.com/my_taobao.htm?nekot=zOy1wLPqx9q1xMOoaQ%3D%3D1586065410519',
            'from': 'tb',
            'fc': 'default',
            'style': 'default',
            'keyLogin': 'false',
            'qrLogin': 'true',
            'newMini': 'false',
            'newMini2': 'false',
            'loginType': '3',
            'gvfdcname': '10',
            'gvfdcre': '68747470733A2F2F6C6F67696E2E74616F62616F2E636F6D2F6D656D6265722F6C6F676F75742E6A68746D6C3F73706D3D61317A30322E312E3735343839343433372E372E333762643738326464723237324426663D746F70266F75743D7472756526726564697265637455524C3D6874747073253341253246253246692E74616F62616F2E636F6D2532466D795F74616F62616F2E68746D2533466E656B6F742533447A4F7931774C507178397131784D4F6F61512532353344253235334431353836303635343130353139',
            'TPL_password_2': self.TPL_password2,
            'loginASR': '1',
            'loginASRSuc': '1',
            'oslanguage': 'zh-CN',
            'sr': '1366*768',
            'osVer': '',
            'naviVer': 'chrome|80.039705',
            'osACN': 'Mozilla',
            'osAV': '5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36',
            'osPF': 'Win32',
            'appkey': '00000000',
            'nickLoginLink': '',
            'mobileLoginLink': 'https://login.taobao.com/member/login.jhtml?redirectURL=https://i.taobao.com/my_taobao.htm?nekot=zOy1wLPqx9q1xMOoaQ%3D%3D1586065410519&useMobile=true',
            'showAssistantLink': '',
            'um_token': 'T4AC7F1A38361B8F86D846C93CACC33F67A37C1D10E4E691377C8131CFF',
            'ua': self.ua
        }
        try:
            response = s.post(self.verify_password_url, headers=verify_password_headers, data=verify_password_data,
                              timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            print('验证用户名和密码请求失败，原因: ')
            raise e
        # 提取申请st码地址
        apply_st_url_match = re.search(r'script src="(.*?)"></script>', response.text)
        #存在则返回提取成功则返回
        if apply_st_url_match:
            print('验证用户名密码成功， st码申请地址：{}'.format(apply_st_url_match.group(1)))
            return apply_st_url_match.group(1)
        else:
            print('用户名密码验证失败，请更换data参数')
            raise RuntimeError('用户名密码验证失败！ response：{}'.format(response.text))
    def _apply_st(self):
        '''
        申请st码
        :return:st码
        '''
        apply_st_url = self._verify_password()
        try:
            response = s.get(apply_st_url)
            response.raise_for_status()
        except Exception as e:
            print('申请st码请求失败,原因：')
            raise e
        st_match = re.search(r'"data":{"st":"(.*?)"}', response.text)
        if st_match:
            print('获取st码成功，st码：{}'.format(st_match.group(1)))
            return st_match.group(1)
        else:
            raise RuntimeError('获取st码失败! response:{}'.format(response.text))

    def login(self):
        '''
        使用st码登录
        :return:
        '''
        #目前requests库还没有很好的办法破解淘宝滑块验证
        #加载cookies文件
        if self._load_cookies():
            return True
        #判断是否需要滑块验证
        self._user_check()
        st = self._apply_st()
        headers = {
            'Host': 'login.taobao.com',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36',
        }
        try:
            response = s.get(self.vst_url.format(st), headers = headers)
            response.raise_for_status()
        except Exception as e:
            print('st码登录请求失败，原因')
            raise e
        #登录成功，提取跳转淘宝主页链接
        my_taobao_match = re.search(r'top.location.href = "(.*?)"',response.text)
        if my_taobao_match:
            print('登录淘宝成功，跳转链接：{}'.format(my_taobao_match.group(1)))
            self._serialization_cookies()
            return True
        else:
            raise RuntimeError('登录失败！ response:{}'.format(response.text))
    def _load_cookies(self):
        #1.判断cookies序列化文件是否存在
        if not os.path.exists(COOKIES_FILE_PATH):
            return False
        #2.加载cookies
        s.cookies = self._deserialization_cookies()
        #3.判断cookies是否过期
        try:
            self.get_taobao_nick_name()
        except Exception as e:
            os.remove(COOKIES_FILE_PATH)
            print('cookies过期，删除cookies文件！')
            return False
        print('加载淘宝登录cookies成功！')
        return True

    def _serialization_cookies(self):
        '''
        序列化cookies
        :return:
        '''
        cookies_dict = requests.utils.dict_from_cookiejar(s.cookies)
        with open(COOKIES_FILE_PATH, 'w+', encoding='utf-8') as file:
            json.dump(cookies_dict, file)
            print('保存cookies文件成功')

    def _deserialization_cookies(self):
        '''
        反序列化cookies
        :return:
        '''
        with open(COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
            cookies_dict = json.load(file)
            cookies = requests.utils.cookiejar_from_dict(cookies_dict)
            return cookies

    def get_taobao_nick_name(self):
        '''
        获取淘宝昵称
        :return: 淘宝昵称
        '''
        #淘宝用户主页url
        #my_taobao_url = self.login()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36',
        }
        try:
            response = s.get(self.my_taobao_url, headers = headers)
            response.raise_for_status()
        except Exception as e:
            print('获取淘宝主页请求失败！原因：')
            raise e
        #提取淘宝昵称
        nick_name_match = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        if nick_name_match:
            print('登录淘宝成功，你的用户名是：{}'.format(nick_name_match.group(1)))
            return nick_name_match.group(1)
        else:
            raise RuntimeError('获取淘宝昵称失败！response：{}'.format(response.text))

if __name__ == '__main__':
    #淘宝用户名
    username = '15116964635'
    #淘宝重要参数，从浏览器或者抓包工具中复制，可以重复使用
    ua = ''
    #加密后的密码，从浏览器或者抓包工具中复制，可以重复使用
    TPL_password2 = ''
    ul = UsernameLogin(username, ua, TPL_password2)
    ul.login()
    ul.get_taobao_nick_name()






