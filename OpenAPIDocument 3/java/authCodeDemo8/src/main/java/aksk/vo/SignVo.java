package aksk.vo;

import lombok.AllArgsConstructor;
import lombok.Data;


import java.util.List;
import java.util.Map;

/**
 * @author sangfor
 */
@Data
@AllArgsConstructor
public class SignVo {
    private Map<String, List<String>> authorityHeader;
}
