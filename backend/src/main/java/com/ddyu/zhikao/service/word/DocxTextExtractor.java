package com.ddyu.zhikao.service.word;

import com.ddyu.zhikao.common.BizException;
import org.springframework.web.multipart.MultipartFile;

import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/**
 * 用 JDK 的 ZipFile 读 docx 里的 word/document.xml，再按 w:p 抽出段落文本。
 */
public final class DocxTextExtractor {

    private static final String DOCUMENT_ENTRY = "word/document.xml";
    private static final String W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main";

    private DocxTextExtractor() {
    }

    public static List<String> paragraphs(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw BizException.badRequest("文件为空");
        }
        String name = file.getOriginalFilename();
        if (name == null || !name.toLowerCase().endsWith(".docx")) {
            throw BizException.badRequest("只支持 .docx 文件");
        }
        Path temp = null;
        try {
            temp = Files.createTempFile("zhikao-import-", ".docx");
            file.transferTo(temp);
            return paragraphs(temp);
        } catch (BizException e) {
            throw e;
        } catch (IOException e) {
            throw BizException.badRequest("文件读取失败：" + e.getMessage());
        } finally {
            if (temp != null) {
                try {
                    Files.deleteIfExists(temp);
                } catch (IOException ignored) {
                    // 临时文件清不掉不影响导入结果
                }
            }
        }
    }

    public static List<String> paragraphs(Path docx) {
        try (ZipFile zip = new ZipFile(docx.toFile())) {
            ZipEntry entry = zip.getEntry(DOCUMENT_ENTRY);
            if (entry == null) {
                throw BizException.badRequest("不是有效的 docx：缺少 word/document.xml");
            }
            try (InputStream in = zip.getInputStream(entry)) {
                return readParagraphs(in);
            }
        } catch (BizException e) {
            throw e;
        } catch (IOException e) {
            throw BizException.badRequest("docx 已损坏，无法打开：" + e.getMessage());
        } catch (XMLStreamException e) {
            throw BizException.badRequest("docx 内容损坏，无法解析：" + e.getMessage());
        }
    }

    private static List<String> readParagraphs(InputStream in) throws XMLStreamException {
        XMLInputFactory factory = XMLInputFactory.newFactory();
        factory.setProperty(XMLInputFactory.SUPPORT_DTD, false);
        factory.setProperty(XMLInputFactory.IS_SUPPORTING_EXTERNAL_ENTITIES, false);
        XMLStreamReader reader = factory.createXMLStreamReader(in);
        List<String> paragraphs = new ArrayList<>();
        StringBuilder current = null;
        while (reader.hasNext()) {
            int event = reader.next();
            if (event == XMLStreamConstants.START_ELEMENT && W_NS.equals(reader.getNamespaceURI())) {
                String local = reader.getLocalName();
                if ("p".equals(local)) {
                    if (current != null) {
                        paragraphs.add(current.toString());
                    }
                    current = new StringBuilder();
                } else if ("t".equals(local) && current != null) {
                    current.append(reader.getElementText());
                } else if (("tab".equals(local) || "br".equals(local) || "cr".equals(local)) && current != null) {
                    current.append(' ');
                }
            }
        }
        if (current != null) {
            paragraphs.add(current.toString());
        }
        reader.close();
        return paragraphs;
    }
}
