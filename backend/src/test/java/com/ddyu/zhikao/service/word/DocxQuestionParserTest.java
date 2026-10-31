package com.ddyu.zhikao.service.word;

import org.junit.jupiter.api.Test;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * 只解析本地 docx，不连 MySQL / Redis。
 */
class DocxQuestionParserTest {

    private static final Path DIR = Path.of(
            "C:\\Users\\DDyu\\Desktop\\temp\\2026年第17届市调大赛网考说明及网考模拟题");

    private final DocxQuestionParser parser = new DocxQuestionParser();

    @Test
    void undergraduatePaperHas85Questions() {
        DocxQuestionParser.ParseResult result = parse("17届市调大赛本科组模拟题.docx");
        assertTrue(result.getErrors().isEmpty(), () -> result.getErrors().toString());
        assertEquals(85, result.getQuestions().size());
        assertEquals(59, count(result, "single"));
        assertEquals(15, count(result, "multi"));
        assertEquals(11, count(result, "judge"));

        DocxQuestionParser.ParsedQuestion first = bySortNo(result, 1);
        assertEquals("B", first.getAnswerLetters());

        DocxQuestionParser.ParsedQuestion multi = bySortNo(result, 60);
        assertEquals("multi", multi.getType());
        assertTrue(multi.getAnswerLetters().contains("A"));
        assertTrue(multi.getAnswerLetters().contains("B"));
        assertTrue(multi.getAnswerLetters().contains("C"));
        assertTrue(multi.getAnswerLetters().contains("D"));
    }

    @Test
    void juniorCollegePaperHas100Questions() {
        DocxQuestionParser.ParseResult result = parse("17届市调大赛专科组模拟题.docx");
        assertTrue(result.getErrors().isEmpty(), () -> result.getErrors().toString());
        assertEquals(100, result.getQuestions().size());
    }

    @Test
    void plainTextDocxParsesNothing() throws Exception {
        Path temp = Files.createTempFile("zhikao-empty-", ".docx");
        try {
            writePlainDocx(temp, "这只是一段普通文字，没有题目。");
            DocxQuestionParser.ParseResult result = parser.parse(DocxTextExtractor.paragraphs(temp));
            assertTrue(result.getQuestions().isEmpty());
        } finally {
            Files.deleteIfExists(temp);
        }
    }

    private DocxQuestionParser.ParseResult parse(String name) {
        return parser.parse(DocxTextExtractor.paragraphs(DIR.resolve(name)));
    }

    private long count(DocxQuestionParser.ParseResult result, String type) {
        return result.getQuestions().stream().filter(q -> type.equals(q.getType())).count();
    }

    private DocxQuestionParser.ParsedQuestion bySortNo(DocxQuestionParser.ParseResult result, int sortNo) {
        return result.getQuestions().stream()
                .filter(q -> q.getSortNo() == sortNo)
                .findFirst()
                .orElseThrow();
    }

    /** 造一份只有一段正文的 docx，不引入第三方库 */
    private void writePlainDocx(Path path, String text) throws Exception {
        String xml = """
                <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                  <w:body><w:p><w:r><w:t>%s</w:t></w:r></w:p></w:body>
                </w:document>
                """.formatted(text);
        Map<String, String> entries = Map.of(
                "[Content_Types].xml", """
                        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                        <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
                          <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
                          <Default Extension="xml" ContentType="application/xml"/>
                          <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
                        </Types>
                        """,
                "_rels/.rels", """
                        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                        <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
                          <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
                        </Relationships>
                        """,
                "word/document.xml", xml);
        try (ZipOutputStream zip = new ZipOutputStream(Files.newOutputStream(path))) {
            for (Map.Entry<String, String> entry : entries.entrySet()) {
                zip.putNextEntry(new ZipEntry(entry.getKey()));
                zip.write(entry.getValue().getBytes(java.nio.charset.StandardCharsets.UTF_8));
                zip.closeEntry();
            }
        }
    }
}
