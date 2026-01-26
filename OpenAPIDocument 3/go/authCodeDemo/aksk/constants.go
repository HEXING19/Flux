package v4

const (
	extendHeader       = "Algorithm=HMAC-SHA256, Access=%s, SignedHeaders=%s, Signature=%s"
	totalStr           = "HMAC-SHA256\n%s\n%s"
	AuthHeaderKey      = "authorization"
	sdkHostKey         = "sdk-host"
	sdkContentTypeKey  = "sdk-content-type"
	contentTypeKey     = "content-type"
	defaultContentType = "application/json"
	signDateKey        = "sign-date"
	authInfoMapSize    = 4
)
