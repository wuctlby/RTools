import sys
import os
import pytest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../src"))
sys.path.insert(0, SRC_DIR)

from StringConvert import convert

@pytest.mark.parametrize("input_path, expected", [
    # 1️⃣ 普通 Windows 路径
    ("C:\\Users\\LibeiyuP\\Downloads", "/mnt/c/Users/LibeiyuP/Downloads"),
    ("C:/Users/LibeiyuP/Documents", "/mnt/c/Users/LibeiyuP/Documents"),

    # 2️⃣ 仅盘符路径
    ("D:", "/mnt/d"),
    ("Z:\\", "/mnt/z"),

    # 3️⃣ UNC 路径
    ("\\\\server\\share\\folder\\file.txt", "/mnt/server/share/folder/file.txt"),
    ("//server/share/folder/file.txt", "/mnt/server/share/folder/file.txt"),

    # 4️⃣ file:// URI - 本地路径
    ("file:///C:/Users/LibeiyuP/Downloads/file.pdf", "/mnt/c/Users/LibeiyuP/Downloads/file.pdf"),
    ("file:///D:/data/test.txt", "/mnt/d/data/test.txt"),

    # 5️⃣ file:// URI - 网络共享
    ("file://server/share/folder/file.txt", "/mnt/server/share/folder/file.txt"),

    # 6️⃣ Linux 路径（应保持不变）
    ("/mnt/c/Users/test", "/mnt/c/Users/test"),
    ("/home/libeiyup", "/home/libeiyup"),

    # 7️⃣ 相对路径
    ("relative\\path\\to\\file", "relative/path/to/file"),
    ("./folder\\subfolder", "./folder/subfolder"),

    # 8️⃣ URL 编码路径
    ("C:\\Users\\LibeiyuP\\My%20Documents\\file.txt", "/mnt/c/Users/LibeiyuP/My Documents/file.txt"),

    # 9️⃣ 空或 None 输入
    ("", ""),
    (None, ""),
])
def test_convert_paths(input_path, expected):
    """Test various path conversions."""
    result = convert(input_path)
    assert result == expected, f"\nInput: {input_path}\nExpected: {expected}\nGot: {result}"
