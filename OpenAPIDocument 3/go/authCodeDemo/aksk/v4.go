package v4

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"reflect"
	"sort"
	"strings"
	"time"
)

type (
	sdk struct{}
	// SignParams 签名计算参数
	SignParams struct {
		AccessKey string
		SecretKey string
		Method    string
		Uri       string
		Payload   []byte
		QueryStr  string
		Host      string
		Headers   map[string]string
	}

	headerParam struct {
		Key   string
		Value string
	}

	// Equipment 设备信息
	Equipment struct {
		ClientID       string
		Domain         string
		ClientName     string
		ClientProduct  string
		ClientVersion  string
		ClientIP       string
		Authority      string
		Extended       string
		Desc           string
		AK             string
		SK             string
		SupportVersion string
		HTTPSPort      uint16
	}
)

// NewSdk 新建签名SDK
func NewSdk() *sdk {
	return &sdk{}
}

// CreateSign 给http请求添加签名,使用AkSk秘钥对
func (s *sdk) CreateSign(req *http.Request, ak, sk string) error {
	if req == nil {
		return fmt.Errorf("createSign http request is nil")
	}
	if ak == "" || sk == "" {
		return fmt.Errorf("ak sk can't be blank")
	}
	var headerKey []string
	for key := range req.Header {
		headerKey = append(headerKey, key)
	}
	payload, err := readBody(req)
	if err != nil {
		return err
	}
	host := req.URL.Host
	header, err := parseRequireHeader(req, headerKey)
	if err != nil {
		return err
	}
	signParam := &SignParams{
		AccessKey: ak,
		SecretKey: sk,
		Method:    req.Method,
		Uri:       req.URL.Path,
		QueryStr:  req.URL.RawQuery,
		Host:      host, // openapi的地址
		Payload:   payload,
		Headers:   header,
	}
	// 获取签名信息
	err = s.signature(signParam)
	if err != nil {
		return err
	}
	// 设置签名信息到请求头
	setRequestHeader(req, signDateKey, signParam.Headers[signDateKey])
	setRequestHeader(req, sdkHostKey, signParam.Headers[sdkHostKey])
	setRequestHeader(req, sdkContentTypeKey, signParam.Headers[sdkContentTypeKey])
	setRequestHeader(req, AuthHeaderKey, signParam.Headers[AuthHeaderKey])
	return nil
}

// CreateSignByAuthCode 给http请求添加签名,使用联动码
func (s *sdk) CreateSignByAuthCode(req *http.Request, authCode string) error {
	equipment, err := decodeAuthCode(authCode)
	if err != nil {
		return err
	}
	return s.CreateSign(req, equipment.AK, equipment.SK)
}

// signature 计算签名
func (s *sdk) signature(params *SignParams) error {
	if params == nil || params.Uri == "" || params.Method == "" || params.SecretKey == "" {
		return fmt.Errorf("params illegal,params can't be nil or blank except payload or query string")
	}

	signDate, err := headerCheck(params)
	if err != nil {
		return err
	}

	headerStr, signHeaderStr := signHeaderHandler(params)
	canonicalStr, err := getCanonicalStr(params, headerStr, signHeaderStr)
	if err != nil {
		return err
	}

	canonicalStr = sha256HexUpper([]byte(canonicalStr))
	total := fmt.Sprintf(totalStr, signDate, canonicalStr)

	sign := hmacSha256Hex(params.SecretKey, total)
	extend := fmt.Sprintf(extendHeader, params.AccessKey, signHeaderStr, strings.ToUpper(sign))

	params.Headers[AuthHeaderKey] = extend
	return nil
}

func getCanonicalStr(params *SignParams, headers, signHeader string) (string, error) {
	builder := strings.Builder{}
	builder.WriteString(params.Method)
	builder.WriteString("\n")
	builder.WriteString(urlTransform(params.Uri))
	builder.WriteString("\n")
	transform, err := queryStrTransform(params.QueryStr)
	if err != nil {
		return "", err
	}
	builder.WriteString(transform)
	builder.WriteString("\n")
	builder.WriteString(headers)
	builder.WriteString(signHeader)
	builder.WriteString("\n")
	builder.WriteString(payloadTransform(params.Payload))
	return builder.String(), nil
}

func headerCheck(params *SignParams) (string, error) {
	var signDate string
	if params.Headers == nil {
		params.Headers = make(map[string]string, authInfoMapSize)
	}
	if params.Headers[sdkHostKey] == "" {
		params.Headers[sdkHostKey] = params.Host
	}
	if params.Headers[contentTypeKey] == "" {
		params.Headers[sdkContentTypeKey] = defaultContentType
	} else {
		params.Headers[sdkContentTypeKey] = params.Headers[contentTypeKey]
	}
	if params.Headers[signDateKey] == "" {
		signDate = time.Now().Format("20060102T150405Z")
		params.Headers[signDateKey] = signDate
	}
	if params.Headers[AuthHeaderKey] != "" {
		return "", fmt.Errorf("duplicate check")
	}
	return params.Headers[signDateKey], nil
}

func queryStrTransform(queryStr string) (string, error) {
	if queryStr == "" {
		return "", nil
	}
	split := strings.Split(queryStr, "&")
	sort.Strings(split)
	for i := range split {
		if split[i] == "" {
			return "", fmt.Errorf("query string illegal")
		}
		if !strings.Contains(split[i], "=") {
			return "", fmt.Errorf("query string illegal")
		}
		unescape, err := url.QueryUnescape(split[i])
		if err != nil {
			return "", fmt.Errorf("query string unescape error")
		}
		escape := url.QueryEscape(unescape)
		escape = strings.ReplaceAll(escape, "%2F", "/")
		split[i] = strings.ReplaceAll(escape, "%3D", "=")
	}

	return strings.Join(split, "&"), nil
}

func payloadTransform(payload []byte) string {
	int8s := make([]int8, len(payload))
	for i := range payload {
		int8s[i] = int8(payload[i])
	}
	sort.Slice(int8s, func(i, j int) bool {
		return int8s[i] < int8s[j]
	})
	for i := range int8s {
		payload[i] = byte(int8s[i])
	}
	payload = removeSpaces(payload)
	return sha256HexUpper(payload)
}

func urlTransform(urlStr string) string {
	urlStr = url.QueryEscape(urlStr)
	urlStr = strings.ReplaceAll(urlStr, "%2F", "/")
	urlStr = strings.ReplaceAll(urlStr, "+", "%20")
	if !strings.HasSuffix(urlStr, "/") {
		urlStr = urlStr + "/"
	}
	return urlStr
}

func signHeaderHandler(params *SignParams) (string, string) {
	var headerKeys []headerParam
	for k, v := range params.Headers {
		headerKeys = append(headerKeys, headerParam{k, v})
	}
	sort.Slice(headerKeys, func(i, j int) bool {
		return strings.Compare(strings.ToLower(headerKeys[i].Key), strings.ToLower(headerKeys[j].Key)) < 0
	})
	var headerBuilder, signHeaderBuilder strings.Builder
	for i := range headerKeys {
		headerBuilder.WriteString(headerKeys[i].Key)
		headerBuilder.WriteString(":")
		headerBuilder.WriteString(headerKeys[i].Value)
		headerBuilder.WriteString("\n")
		signHeaderBuilder.WriteString(headerKeys[i].Key)
		signHeaderBuilder.WriteString(";")
	}
	signHeaderStr := signHeaderBuilder.String()
	headerStr := headerBuilder.String()
	length := len(signHeaderStr)
	if length > 0 {
		signHeaderStr = signHeaderStr[:length-1]
	}
	return headerStr, signHeaderStr
}

func readBody(r *http.Request) ([]byte, error) {
	body, err := io.ReadAll(r.Body)
	if r.Body != nil {
		_ = r.Body.Close()
	}
	rewrite := make([]byte, len(body))
	copy(rewrite, body)
	r.Body = io.NopCloser(bytes.NewBuffer(rewrite))
	if err != nil {
		return nil, fmt.Errorf("readBody failed")
	}
	return body, nil
}

func sha256HexUpper(b []byte) string {
	sum256 := sha256.Sum256(b)
	res := hex.EncodeToString(sum256[:])
	return strings.ToUpper(res)
}

func removeSpaces(b []byte) []byte {
	j := 0
	for i := 0; i < len(b); i++ {
		if b[i] != ' ' {
			if i != j {
				b[j] = b[i]
			}
			j++
		}
	}
	return b[:j]
}

func hmacSha256Hex(key string, data string) string {
	mac := hmac.New(sha256.New, []byte(key))
	_, _ = mac.Write([]byte(data))
	sum := mac.Sum(nil)
	return hex.EncodeToString(sum)
}

func setRequestHeader(req *http.Request, key, value string) {
	req.Header[key] = []string{value}
}

func parseRequireHeader(req *http.Request, headerKey []string) (map[string]string, error) {
	header := make(map[string]string)
	for _, key := range headerKey {
		val := req.Header[key]
		if len(val) > 0 {
			header[key] = val[0]
			continue
		}
		return nil, fmt.Errorf("can't get the key %s from request header", key)
	}
	return header, nil
}

func decodeAuthCode(authCode string) (*Equipment, error) {
	equipmentMsg, err := hex.DecodeString(authCode)
	if err != nil {
		return nil, fmt.Errorf("authCode decode failed")
	}
	equipmentElement := strings.Split(string(equipmentMsg), "|")
	if len(equipmentElement) != reflect.TypeOf(Equipment{}).NumField()+1 {
		return nil, fmt.Errorf("parse Equipment element failed, field number incorrect")
	}
	equipment := Equipment{
		ClientID:       equipmentElement[0],
		Domain:         equipmentElement[1],
		ClientName:     equipmentElement[2],
		ClientProduct:  equipmentElement[3],
		ClientVersion:  equipmentElement[4],
		ClientIP:       equipmentElement[5],
		Authority:      equipmentElement[6],
		Extended:       equipmentElement[7],
		Desc:           equipmentElement[8],
		AK:             equipmentElement[9],
		SK:             equipmentElement[10],
		SupportVersion: equipmentElement[11],
	}
	aesSecret := calcAesSecret(equipment)
	if equipment.AK, err = aesCBCDecode(equipment.AK, aesSecret[:]); err != nil {
		return nil, err
	}
	if equipment.SK, err = aesCBCDecode(equipment.SK, aesSecret[:]); err != nil {
		return nil, err
	}
	return &equipment, nil
}

func calcAesSecret(equipment Equipment) [sha256.Size]byte {
	calcStr := fmt.Sprintf("%s+%s+%s+%s+%s+%s+%s+%s",
		equipment.ClientID,
		equipment.Domain,
		equipment.ClientName,
		equipment.ClientProduct,
		equipment.ClientVersion,
		equipment.ClientIP,
		equipment.Authority,
		equipment.SupportVersion,
	)
	return sha256.Sum256([]byte(calcStr))
}

func aesCBCDecode(ciphertext string, key []byte) (string, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return "", fmt.Errorf("create aes Cipher failed")
	}
	cipherByte, err := hex.DecodeString(ciphertext)
	if err != nil {
		return "", fmt.Errorf("create aes Cipher failed")
	}
	plaintext := make([]byte, len(cipherByte))
	iv := make([]byte, aes.BlockSize)
	mode := cipher.NewCBCDecrypter(block, iv)
	mode.CryptBlocks(plaintext, cipherByte)
	return string(plaintext), nil
}
