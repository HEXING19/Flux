package main

import (
	"bytes"
	"crypto/tls"
	"fmt"
	"io"
	"net/http"

	v4 "authcode/aksk"
)

// SDK使用流程
// 1.登录平台并从页面URl中获取到平台的地址
// 2.从平台页面 配置管理 -> 系统设置 -> 开放性 -> 联动码管理页面获取联动码
// 3.查看平台接口开放列表挑选接口
// 4.将联动码authCode、host、url信息填充到以下main程序中
// 5.根据接口文档结合调用方自身需求构造请求的参数、header，选择合适的请求方法
// 6.运行本程序并查看打印的返回结果
// 注意！！！
// signTool.CreateSignByAuthCode(req, authCode)步骤为对req签名，签名之后您不能修改req的任何内容
// 包括参数、url等，也不能将请求打印为curl等命令之后拷贝至其他环境执行
// 对req可以执行的唯一操作是将其发送出去
// 若您需要修改参数等，请重新构造新的req并对其执行签名操作

func main() {
	// 联动码从平台页面 配置管理 -> 系统设置 -> 开放性 -> 联动码管理页面获取
	authCode := ""

	// 构造请求，需根据实际情况更换参数
	// host为平台页面URL中的host, url参照接口文档
	body := "{\"page\": 1, \"pageSize\": 10}"

	// 构造POST请求
	req, err := http.NewRequest(http.MethodPost, "https://10.10.10.10/api/xdr/v1/assets/list", bytes.NewBuffer([]byte(body)))
	// 构造GET请求
	// req, err := http.NewRequest(http.MethodGet, "https://10.10.10.10/api/xdr/v1/assets/department?test=test", http.NoBody)
	if err != nil {
		fmt.Println(err)
		return
	}
	// 设置请求header
	req.Header["content-type"] = []string{"application/json"}

	// 对请求签名
	// 签名之后不能对req进行任何的修改、拷贝等，直接发送请求即可
	// 若有需要修改参数，请重新构造请求，重新签名
	signTool := v4.NewSdk()
	if err = signTool.CreateSignByAuthCode(req, authCode); err != nil {
		fmt.Println(err)
		return
	}

	// 发送请求
	client := &http.Client{}
	client.Transport = &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
		},
	}
	res, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return
	}
	// 打印结果
	resBody, err := io.ReadAll(res.Body)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(string(resBody))
}
