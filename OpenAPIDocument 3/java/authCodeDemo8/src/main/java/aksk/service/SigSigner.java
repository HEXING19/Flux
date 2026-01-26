package aksk.service;

import lombok.NonNull;
import org.apache.http.client.methods.HttpRequestBase;

/**
 * @author sangfor
 */
public interface SigSigner {

    /**
     * 本方法用来对签名结构体进行签名
     *
     * @param request 签名参数
     * @throws Exception 当签名出现异常时抛出
     */
    void sign(@NonNull HttpRequestBase request) throws Exception;
}
