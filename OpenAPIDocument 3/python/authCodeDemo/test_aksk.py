# -*- coding: utf-8 -*-
import json
import requests
from aksk_py3 import Signature

# SDK使用流程
# 1.登录平台并从页面URl中获取到平台的地址
# 2.从平台页面 配置管理 -> 系统设置 -> 开放性 -> 联动码管理页面获取联动码
# 3.查看平台接口开放列表挑选接口
# 4.将联动码auth_code、host、url信息填充到以下test_check程序中
# 5.根据接口文档结合调用方自身需求构造请求的参数、header，选择合适的请求方法
# 6.运行本程序并查看打印的返回结果
# 注意！！！
# signature.signature(req=req)步骤为对req签名，签名之后您不能修改req的任何内容
# 包括参数、url等，也不能将请求打印为curl等命令之后拷贝至其他环境执行
# 对req可以执行的唯一操作是将其发送出去
# 若您需要修改参数等，请重新构造新的req并对其执行签名操作


def test_check():
    # 联动码 从平台页面 配置管理 -> 系统设置 -> 开放性 -> 联动码管理页面获取
    auth_code = ""

    # 构造签名对象
    signature = Signature(auth_code=auth_code)

    # 构造请求，需根据实际情况更换参数
    # host为平台页面URL中的host, url参照接口文档
    url = "https://10.10.10.10/api/xdr/v1/assets/list"
    data = {
        # "startTimestamp": 1683371415
    }
    params = {
        # "startTimestamp": 1683371415
    }
    headers = {
        "content-type": "application/json"
    }

    # 构造POST请求
    req = requests.Request("POST", url, headers=headers, data=json.dumps(data))
    # 构造GET请求
    # req = requests.Request("GET", url, headers=headers, params=params)

    # 对请求签名
    # 签名之后不能对req进行任何的修改、拷贝等，直接发送请求即可
    # 若有需要修改参数，请重新构造请求，重新签名
    signature.signature(req=req)

    # 发送请求
    session = requests.Session()
    session.verify = False
    response = session.send(req.prepare())

    # 打印结果
    print(response.content.decode("utf-8"))


if __name__ == '__main__':
    test_check()
