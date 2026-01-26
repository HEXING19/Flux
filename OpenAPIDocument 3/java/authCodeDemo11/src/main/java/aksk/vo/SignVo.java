package aksk.vo;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.net.http.HttpHeaders;

/**
 * @author sangfor
 */
@Data
@AllArgsConstructor
public class SignVo {
    private HttpHeaders authorityHeader;
}
