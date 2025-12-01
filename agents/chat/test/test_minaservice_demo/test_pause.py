import random
import secrets
import string
from datetime import datetime

import requests
from fake_useragent import UserAgent

cookies = {
    'serviceToken': 'sXEJMjSdm6MHAaBJzdchB+/p5vslaWjlgPAzZOkQq9S4XGFuuWFKpMaibGh0l6I+C5MDhuQCe8Mzej/+73bYvCTVbT2WcNTbKEYbPWMylJ0eSH/0C9NDlpO5hBawM2abTlgTd7mMBah4bu2SjPT88UfftL8K1ahBojPGpH9EIgaUnMULZQerivbC5Z255HHKYPvBisoVd8YHoSES8lWi5Q==',
    # 'hardware': 'OH2P',
    # 'deviceId': '74981115-b0be-43d6-a328-cc8b8f1a2b74',
    'userId': '2363583898',
    # 'phoneModel': 'Xiaomi',
    # 'instanceId': '164552a4-cb81-45c0-ab16-2de0eadefe93',
    # 'sn': '62833/A4ZT55167',
    # 'deviceSNProfile': 'eyJzaWduYXR1cmUiOiJHQkFaN3dmbC9uZFBnNTdjTWJHZ0xzZUZHQkpxdjBjVE1MZEsrcnM1RDh3YzZYN2V1d0VvRklpLzQ4MHJibTd4UkMvU002RUkydld4U0Ria0pRZ1NBQT09Iiwicm9tVmVyc2lvbiI6IjEuNTguNSIsInNpZ24iOiJjNzY0ZjliODMzNWNhMmFmMDdjMTI1ZDE0MDQxNjUxZTI0MzllZWQwMDJhZjMwYWMwYzMzMzFhNzU5YmViOWZiIiwic24iOiI2MjgzMy9BNFpUNTUxNjcifQ==',
}

headers = {
    # 'User-Agent': 'MiHome/6.0.103 (com.xiaomi.mihome; build:6.0.103.1; iOS 14.4.0) Alamofire/6.0.103 MICO/iOSApp/appStore/6.0.103',
    'User-Agent': UserAgent().random,
    # 'Accept-Encoding': 'gzip',
    'Content-Type': 'application/x-www-form-urlencoded',
    # 'clientexpids': 'sdg',
    # 'tvbgroupids': 'de1tD,de13A,dfclB,dejmA,dej0A,de7eA,decvC,dflaE,dezbH,deqlA,deqnA,defwB,ed92,eebu,eepb,eeqk,edui,ed8c,ed8h,eedj,eedl,eedn,eeei,eeqo,ee6i,efk7,de29C,deauB,de7hB,dey5C,de9bB,dernB',
    # 'x-user-level': '1',
}

def generate_random_string(length=20):
    """生成安全的随机字符串（大小写字母+数字，长度20）"""
    characters = string.ascii_letters + string.digits  # 包含a-zA-Z0-9
    return ''.join(secrets.choice(characters) for _ in range(length))

params = (
    # ('timestamp', int(datetime.now().timestamp() * 1000)),
    ('requestId', generate_random_string()),
)

response = requests.post(
    'https://api2.mina.xiaoaisound.com/remote/ubus',
    headers=headers,
    params=params,
    data='deviceId=74981115-b0be-43d6-a328-cc8b8f1a2b74&path=mediaplayer&method=player_play_operation&message=%7B%22action%22%3A%22pause%22%2C%22media%22%3A%22app_android%22%7D',
    cookies=cookies
)

print(response.text)

#NB. Original query string below. It seems impossible to parse and
#reproduce query strings 100% accurately so the one below is given
#in case the reproduced version is not "correct".
# response = requests.post('https://api2.mina.xiaoaisound.com/remote/ubus?timestamp=1764152265080&requestId=FgC49Abqi2mberdTxFs7', headers=headers, cookies=cookies)


# print(UserAgent().random)