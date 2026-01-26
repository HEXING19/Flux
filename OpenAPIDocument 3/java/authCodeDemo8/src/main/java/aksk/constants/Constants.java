package aksk.constants;


/**
 * @author sangfor
 */
public class Constants {
    public final static String SIG_HEADER_AUTHORIZATION = "Authorization";
    public final static String SIGN_DATE = "sign-date";
    public final static String SDK_CONTENT_TYPE = "sdk-content-type";
    public final static String CONTENT_TYPE = "content-type";
    public final static String SDK_HOST = "sdk-host";
    public final static String HOST = "Host";
    public final static String PAYLOAD_HASH = "Payload-Hash";

    public static final int SIG_ESCAPE_URI = 1;
    public static final int SIG_ESCAPE_QUERY = 2;

    public static final String AUTH_STR = "algorithm=HMAC-SHA256, Access=%s, SignedHeaders=%s, Signature=%s";
    public static final String SIGN_STR = "HMAC-SHA256\n%s\n%s";
    public final static String DATE_FORMAT = "yyyyMMdd'T'HHmmssZZ";

    public final static int AUTH_CODE_PARAMS_NUM = 14;
    public final static String AUTH_CODE_PARAMS = "%s+%s+%s+%s+%s+%s+%s+%s";
}
