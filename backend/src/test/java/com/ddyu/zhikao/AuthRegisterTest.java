package com.ddyu.zhikao;

import com.ddyu.zhikao.common.BizException;
import com.ddyu.zhikao.config.TokenStore;
import com.ddyu.zhikao.dto.RegisterDTO;
import com.ddyu.zhikao.entity.SysUser;
import com.ddyu.zhikao.mapper.UserMapper;
import com.ddyu.zhikao.service.AuthService;
import com.ddyu.zhikao.service.impl.AuthServiceImpl;
import com.ddyu.zhikao.vo.RegisterVO;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * 注册接口：只测 DTO 校验和 Service 逻辑，不连数据库、不连 Redis
 */
class AuthRegisterTest {

    private UserMapper userMapper;
    private AuthService authService;
    private final PasswordEncoder passwordEncoder = new BCryptPasswordEncoder();
    private Validator validator;

    @BeforeEach
    void setUp() {
        userMapper = mock(UserMapper.class);
        TokenStore tokenStore = mock(TokenStore.class);
        authService = new AuthServiceImpl(userMapper, tokenStore, passwordEncoder);
        ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @Test
    void registerSuccess() {
        RegisterDTO dto = dto("zhangsan", "123456", "张三");
        when(userMapper.selectCount(any())).thenReturn(0L);
        when(userMapper.insert(any(SysUser.class))).thenAnswer(invocation -> {
            SysUser user = invocation.getArgument(0);
            user.setId(5L);
            return 1;
        });

        RegisterVO vo = authService.register(dto);

        assertEquals(5L, vo.getId());
        assertEquals("zhangsan", vo.getUsername());
        assertEquals("张三", vo.getNickname());
        assertEquals("STUDENT", vo.getRole());

        ArgumentCaptor<SysUser> captor = ArgumentCaptor.forClass(SysUser.class);
        verify(userMapper).insert(captor.capture());
        SysUser saved = captor.getValue();
        assertEquals("STUDENT", saved.getRole());
        assertEquals(1, saved.getStatus());
        assertNotEquals("123456", saved.getPassword());
        assertTrue(passwordEncoder.matches("123456", saved.getPassword()));
    }

    @Test
    void registerDuplicateUsername() {
        when(userMapper.selectCount(any())).thenReturn(1L);

        BizException e = assertThrows(BizException.class,
                () -> authService.register(dto("zhangsan", "123456", "张三")));

        assertEquals(400, e.getCode());
        assertEquals("用户名已被注册，请换一个", e.getMessage());
        verify(userMapper, never()).insert(any(SysUser.class));
    }

    @Test
    void registerInvalidUsername() {
        List<String> messages = validate(dto("ab", "123456", "张三"));
        assertEquals(List.of("用户名需为 4-20 位字母、数字或下划线"), messages);
    }

    @Test
    void registerShortPassword() {
        List<String> messages = validate(dto("zhangsan", "123", "张三"));
        assertEquals(List.of("密码长度需为 6-20 位"), messages);
    }

    @Test
    void registerBlankNickname() {
        List<String> messages = validate(dto("zhangsan", "123456", ""));
        assertEquals(List.of("请输入昵称"), messages);
    }

    @Test
    void registerBlankUsername() {
        List<String> messages = validate(dto("", "123456", "张三"));
        assertEquals(List.of("请输入用户名"), messages);
    }

    private RegisterDTO dto(String username, String password, String nickname) {
        RegisterDTO dto = new RegisterDTO();
        dto.setUsername(username);
        dto.setPassword(password);
        dto.setNickname(nickname);
        return dto;
    }

    private List<String> validate(RegisterDTO dto) {
        Set<ConstraintViolation<RegisterDTO>> violations = validator.validate(dto);
        return violations.stream().map(ConstraintViolation::getMessage).sorted().toList();
    }
}