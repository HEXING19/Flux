package aksk.qo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

import javax.validation.constraints.NotBlank;
import java.net.http.HttpHeaders;
import java.util.Objects;

/**
 * @author sangfor
 */
@Builder
@Getter
@Setter
@AllArgsConstructor
public class SignQo {
    @NotBlank(message = "method can not be null")
    private String method;

    @NotBlank(message = "uri can not be null")
    private String uri;

    @NotBlank(message = "host can not be null")
    private String host;

    @NotBlank(message = "payload can not be null")
    private byte[] payload;

    @NotBlank(message = "queryStr can not be null")
    private String queryStr;

    private HttpHeaders headers;

    @Override
    public String toString() {
        return "SignQo{" +
                ", method='" + method + '\'' +
                ", uri='" + uri + '\'' +
                ", host='" + host + '\'' +
                ", payload=" + (Objects.isNull(payload) ? "" : new String(payload)) +
                ", queryStr='" + queryStr + '\'' +
                ", headers=" + headers +
                '}';
    }
}
