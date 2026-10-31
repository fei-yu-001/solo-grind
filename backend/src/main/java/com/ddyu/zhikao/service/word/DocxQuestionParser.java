package com.ddyu.zhikao.service.word;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 把市调大赛 Word 题库的段落文本解析成题目。
 * 不读文件，只认三种行：题干、选项标题、选项。
 */
public class DocxQuestionParser {

    private static final Pattern STEM = Pattern.compile(
            "^(\\d+)-题目：(.*)\\[题型：(单选题|多选题|判断题)]\\[答案：([A-E]+)]\\s*$");
    private static final Pattern OPTION_HEADER = Pattern.compile("^\\d+-选项：\\s*$");
    private static final Pattern OPTION = Pattern.compile("^（([A-E])）(.*)$");

    private static final Map<String, String> TYPE_CODE = Map.of(
            "单选题", "single",
            "多选题", "multi",
            "判断题", "judge");

    /**
     * 按段落出现顺序解析。标题行、选项标题行忽略；对不上格式的行记一条错误，不中断后面的题。
     */
    public ParseResult parse(List<String> paragraphs) {
        List<ParsedQuestion> questions = new ArrayList<>();
        List<ParseError> errors = new ArrayList<>();
        ParsedQuestion current = null;
        for (String raw : paragraphs) {
            String line = raw == null ? "" : raw.trim();
            if (line.isEmpty() || OPTION_HEADER.matcher(line).matches() || isTitle(line)) {
                continue;
            }
            Matcher stem = STEM.matcher(line);
            if (stem.matches()) {
                current = finish(questions, errors, current);
                current = newQuestion(stem, line, errors);
                continue;
            }
            Matcher option = OPTION.matcher(line);
            if (option.matches()) {
                if (current == null) {
                    errors.add(new ParseError(line, "选项出现在题目之前"));
                } else {
                    addOption(current, option.group(1), option.group(2), line, errors);
                }
                continue;
            }
            errors.add(new ParseError(line, "无法识别的行"));
        }
        finish(questions, errors, current);
        return new ParseResult(questions, errors);
    }

    private ParsedQuestion finish(List<ParsedQuestion> questions, List<ParseError> errors, ParsedQuestion current) {
        if (current == null) {
            return null;
        }
        if (current.options.isEmpty()) {
            errors.add(new ParseError(current.sourceLine, "题目没有选项"));
            return null;
        }
        for (char letter : current.answerLetters.toCharArray()) {
            if (!current.options.containsKey(String.valueOf(letter))) {
                errors.add(new ParseError(current.sourceLine,
                        "答案 " + current.answerLetters + " 里有选项里没有的字母"));
                return null;
            }
        }
        questions.add(current);
        return null;
    }

    private ParsedQuestion newQuestion(Matcher stem, String line, List<ParseError> errors) {
        String typeName = stem.group(3);
        String answer = stem.group(4);
        String reason = answerReason(typeName, answer);
        if (reason != null) {
            errors.add(new ParseError(line, reason));
            return null;
        }
        ParsedQuestion question = new ParsedQuestion();
        question.sortNo = Integer.parseInt(stem.group(1));
        question.stem = stem.group(2).trim();
        question.type = TYPE_CODE.get(typeName);
        question.answerLetters = answer;
        question.sourceLine = line;
        if (question.stem.isEmpty()) {
            errors.add(new ParseError(line, "题干为空"));
            return null;
        }
        return question;
    }

    /** 文档开头的标题，如「17届市调大赛本科组模拟题1」，没有题号前缀 */
    private boolean isTitle(String line) {
        return !line.contains("-题目：") && !line.startsWith("（") && line.contains("模拟题");
    }

    private String answerReason(String typeName, String answer) {
        if ("单选题".equals(typeName) && answer.length() != 1) {
            return "单选题答案必须是一个字母";
        }
        if ("判断题".equals(typeName) && !"A".equals(answer) && !"B".equals(answer)) {
            return "判断题答案必须是 A（对）或 B（错）";
        }
        if ("多选题".equals(typeName) && answer.length() < 2) {
            return "多选题答案至少两个字母";
        }
        return null;
    }

    private void addOption(ParsedQuestion current, String key, String text, String line, List<ParseError> errors) {
        // 公式经常被做成图片，w:t 里只剩「（A）」。内容留空，不因此整卷失败
        String content = text.trim();
        if (content.isEmpty()) {
            content = "（公式或图片）";
        }
        if (current.options.containsKey(key)) {
            errors.add(new ParseError(line, "选项 " + key + " 重复"));
            return;
        }
        current.options.put(key, content);
    }

    public static class ParseResult {
        private final List<ParsedQuestion> questions;
        private final List<ParseError> errors;

        public ParseResult(List<ParsedQuestion> questions, List<ParseError> errors) {
            this.questions = questions;
            this.errors = errors;
        }

        public List<ParsedQuestion> getQuestions() {
            return questions;
        }

        public List<ParseError> getErrors() {
            return errors;
        }
    }

    public static class ParsedQuestion {
        private int sortNo;
        private String type;
        private String stem;
        private final Map<String, String> options = new LinkedHashMap<>();
        private String answerLetters;
        private String sourceLine;

        public int getSortNo() {
            return sortNo;
        }

        public String getType() {
            return type;
        }

        public String getStem() {
            return stem;
        }

        public Map<String, String> getOptions() {
            return options;
        }

        public String getAnswerLetters() {
            return answerLetters;
        }
    }

    public static class ParseError {
        private final String line;
        private final String reason;

        public ParseError(String line, String reason) {
            this.line = line;
            this.reason = reason;
        }

        public String getLine() {
            return line;
        }

        public String getReason() {
            return reason;
        }
    }
}
