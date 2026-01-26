import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import aksk.service.impl.SigSignerJavaImpl;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.conn.ssl.NoopHostnameVerifier;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContextBuilder;
import org.apache.http.ssl.TrustStrategy;
import org.apache.http.util.EntityUtils;
import org.junit.jupiter.api.Test;

import javax.net.ssl.SSLContext;
import java.security.cert.X509Certificate;


// SDK使用流程
// 1.登录平台并从页面URl中获取到平台的地址
// 2.从平台页面 配置管理 -> 系统设置 -> 开放性 -> 联动码管理页面获取联动码
// 3.查看深信服平台接口开放列表挑选接口
// 4.将联动码authCode、host、url信息填充到以下main程序中
// 5.根据接口文档结合调用方自身需求构造请求的参数、header，选择合适的请求方法
// 6.运行本程序并查看打印的返回结果
// 注意！！！
// sigSignerJava.sign(request)步骤为对req签名，签名之后您不能修改req的任何内容
// 包括参数、url等，也不能将请求打印为curl等命令之后拷贝至其他环境执行
// 对req可以执行的唯一操作是将其发送出去
// 若您需要修改参数等，请重新构造新的req并对其执行签名操作

public class JavaSignerTest {
    @Test
    public void testNormal() {
        try {
            // 联动码从平台页面 配置管理 -> 系统设置 -> 开放性 -> 联动码管理页面获取
            SigSignerJavaImpl sigSignerJava = new SigSignerJavaImpl("");

            // 构造POST请求
            HttpPost request = new HttpPost("https://10.10.10.10/api/xdr/v1/assets/list");
            JSONObject json = new JSONObject();
            // json.put("startTime", 1689776019);
            // json.put("endTime", 1689779619);
            // json.put("size", 1000);
            request.setEntity(new StringEntity(JSON.toJSONString(json)));

            // 构造GET请求
            // HttpGet request = new HttpGet("https://10.10.10.10/api/xdr/v1/assets/department?getUndistributed=1");

            // 设置请求头
            request.setHeader("content-type", "application/json");

            // 签名
            // 签名之后不能对request进行任何的修改、拷贝等，直接发送请求即可
            // 若有需要修改参数，请重新构造请求，重新签名
            sigSignerJava.sign(request);

            // 发送请求
            SSLContext sslContext = new SSLContextBuilder().loadTrustMaterial(null, new TrustStrategy() {
                public boolean isTrusted(X509Certificate[] arg0, String arg1) {
                    return true;
                }
            }).build();
            SSLConnectionSocketFactory sslsf = new SSLConnectionSocketFactory(sslContext, NoopHostnameVerifier.INSTANCE);
            HttpClient httpClient = HttpClients.custom().setSSLSocketFactory(sslsf).build();
            HttpResponse response = httpClient.execute(request);

            // 打印结果
            String content = EntityUtils.toString(response.getEntity(), "UTF-8");
            System.out.printf("%s", content);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}