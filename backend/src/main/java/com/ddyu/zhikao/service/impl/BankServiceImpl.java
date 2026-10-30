package com.ddyu.zhikao.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.ddyu.zhikao.common.BizException;
import com.ddyu.zhikao.common.CacheKeys;
import com.ddyu.zhikao.common.PageResult;
import com.ddyu.zhikao.dto.BankForm;
import com.ddyu.zhikao.entity.QuestionBank;
import com.ddyu.zhikao.entity.Question;
import com.ddyu.zhikao.mapper.BankMapper;
import com.ddyu.zhikao.mapper.QuestionMapper;
import com.ddyu.zhikao.service.BankService;
import com.ddyu.zhikao.vo.BankVO;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.util.Collections;
import java.util.List;

/**
 * 题库：分页条件查询、详情、增删改、Redis 字典缓存
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class BankServiceImpl implements BankService {

    private static final Duration DICT_TTL = Duration.ofSeconds(3600);
    private static final Duration EMPTY_TTL = Duration.ofSeconds(60);

    private final BankMapper bankMapper;
    private final QuestionMapper questionMapper;
    private final StringRedisTemplate redis;
    private final ObjectMapper objectMapper;

    @Override
    public PageResult<BankVO> page(String keyword, String groupName, String status, long page, long size) {
        Page<BankVO> result = new Page<>(page, size);
        result.setRecords(bankMapper.selectBankPage(result, keyword, groupName, status));
        List<BankVO> records = result.getRecords();
        records.forEach(vo -> vo.setStatusText("ENABLED".equals(vo.getStatus()) ? "启用" : "停用"));
        return new PageResult<>(result.getTotal(), result.getCurrent(), result.getSize(), records);
    }

    /** 全量字典：cache-aside，空结果写 __EMPTY__ 防穿透 */
    @Override
    public List<BankVO> listAll() {
        String key = CacheKeys.DICT_BANKS;
        try {
            String cached = redis.opsForValue().get(key);
            if (cached != null) {
                if (CacheKeys.EMPTY_VALUE.equals(cached)) {
                    log.info("[cache] 题库字典 命中（空值标记）");
                    return Collections.emptyList();
                }
                log.info("[cache] 题库字典 命中");
                return objectMapper.readValue(cached, new TypeReference<List<BankVO>>() {
                });
            }
        } catch (Exception e) {
            log.warn("[cache] 题库字典读取失败，回源数据库: {}", e.getMessage());
        }
        log.info("[cache] 题库字典 未命中，回源数据库");
        List<BankVO> list = bankMapper.selectBankPage(null, null, null, null);
        fillStatusText(list);
        try {
            if (list.isEmpty()) {
                redis.opsForValue().set(key, CacheKeys.EMPTY_VALUE, EMPTY_TTL);
            } else {
                redis.opsForValue().set(key, objectMapper.writeValueAsString(list), DICT_TTL);
            }
        } catch (Exception e) {
            log.warn("[cache] 题库字典写入失败: {}", e.getMessage());
        }
        return list;
    }

    @Override
    public BankVO getById(Long id) {
        BankVO vo = bankMapper.selectBankByIds(List.of(id)).stream().findFirst()
                .orElseThrow(() -> BizException.notFound("题库不存在"));
        vo.setStatusText("ENABLED".equals(vo.getStatus()) ? "启用" : "停用");
        return vo;
    }

    @Transactional
    @Override
    public BankVO create(BankForm form) {
        checkNameUnique(form.getName(), null);
        QuestionBank bank = new QuestionBank();
        bank.setName(form.getName());
        bank.setGroupName(form.getGroupName());
        bank.setDescription(form.getDescription());
        bank.setStatus(form.getStatus() == null ? "ENABLED" : form.getStatus());
        bankMapper.insert(bank);
        evictDict();
        return getById(bank.getId());
    }

    @Transactional
    @Override
    public BankVO update(Long id, BankForm form) {
        QuestionBank bank = bankMapper.selectById(id);
        if (bank == null) {
            throw BizException.notFound("题库不存在");
        }
        checkNameUnique(form.getName(), id);
        bank.setName(form.getName());
        bank.setGroupName(form.getGroupName());
        bank.setDescription(form.getDescription());
        bank.setStatus(form.getStatus() == null ? bank.getStatus() : form.getStatus());
        bankMapper.updateById(bank);
        evictDict();
        return getById(id);
    }

    /** 题库下还有题目时不能删 */
    @Transactional
    @Override
    public void delete(Long id) {
        QuestionBank bank = bankMapper.selectById(id);
        if (bank == null) {
            throw BizException.notFound("题库不存在");
        }
        Long questionCount = questionMapper.selectCount(
                new LambdaQueryWrapper<Question>().eq(Question::getBankId, id));
        if (questionCount > 0) {
            throw BizException.conflict("题库下还有 " + questionCount + " 道题目，不能删除");
        }
        bankMapper.deleteById(id);
        evictDict();
    }

    private void checkNameUnique(String name, Long excludeId) {
        LambdaQueryWrapper<QuestionBank> wrapper = new LambdaQueryWrapper<QuestionBank>()
                .eq(QuestionBank::getName, name);
        if (excludeId != null) {
            wrapper.ne(QuestionBank::getId, excludeId);
        }
        if (bankMapper.selectCount(wrapper) > 0) {
            throw BizException.conflict("题库名已存在：" + name);
        }
    }

    private void fillStatusText(List<BankVO> list) {
        list.forEach(vo -> vo.setStatusText("ENABLED".equals(vo.getStatus()) ? "启用" : "停用"));
    }

    private void evictDict() {
        try {
            redis.delete(CacheKeys.DICT_BANKS);
            log.info("[cache] 题库增删改，删除字典缓存");
        } catch (Exception e) {
            log.warn("[cache] 题库字典删除失败: {}", e.getMessage());
        }
    }
}
