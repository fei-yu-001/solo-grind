package com.ddyu.zhikao.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.ddyu.zhikao.common.BizException;
import com.ddyu.zhikao.dto.TagForm;
import com.ddyu.zhikao.entity.QuestionTag;
import com.ddyu.zhikao.entity.Tag;
import com.ddyu.zhikao.mapper.QuestionTagMapper;
import com.ddyu.zhikao.mapper.TagMapper;
import com.ddyu.zhikao.service.TagService;
import com.ddyu.zhikao.vo.TagVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * 标签：列表 + 轻量增删
 */
@Service
@RequiredArgsConstructor
public class TagServiceImpl implements TagService {

    private final TagMapper tagMapper;
    private final QuestionTagMapper questionTagMapper;

    @Override
    public List<TagVO> list() {
        return tagMapper.selectTagList(null);
    }

    @Transactional
    @Override
    public TagVO create(TagForm form) {
        Long count = tagMapper.selectCount(
                new LambdaQueryWrapper<Tag>().eq(Tag::getName, form.getName()));
        if (count > 0) {
            throw BizException.conflict("标签名已存在：" + form.getName());
        }
        Tag tag = new Tag();
        tag.setName(form.getName());
        tag.setColor(form.getColor());
        tagMapper.insert(tag);
        return toVO(tag, 0L);
    }

    /** 标签删了关联也一起清（question_tag 没开级联删 tag 一侧） */
    @Transactional
    @Override
    public void delete(Long id) {
        Tag tag = tagMapper.selectById(id);
        if (tag == null) {
            throw BizException.notFound("标签不存在");
        }
        questionTagMapper.delete(new LambdaQueryWrapper<QuestionTag>().eq(QuestionTag::getTagId, id));
        tagMapper.deleteById(id);
    }

    private TagVO toVO(Tag tag, Long questionCount) {
        TagVO vo = new TagVO();
        vo.setId(tag.getId());
        vo.setName(tag.getName());
        vo.setColor(tag.getColor());
        vo.setQuestionCount(questionCount);
        return vo;
    }
}
