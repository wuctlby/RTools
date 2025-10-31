import pytest
import os
import importlib.util


# Import the implementation by file path so tests work regardless of package layout
def _load_converter():
    this_dir = os.path.dirname(__file__)
    impl_path = os.path.abspath(os.path.join(this_dir, "..", "src", "StringConvert.py"))
    spec = importlib.util.spec_from_file_location("stringconvert", impl_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.convert_to_linux_path


convert_to_linux_path = _load_converter()


@pytest.mark.parametrize(
    "inp,expected",
    [
        ("C:\\Users\\LibeiyuP\\Downloads", "/mnt/c/Users/LibeiyuP/Downloads"),
        ("C:/Users/LibeiyuP/Downloads", "/mnt/c/Users/LibeiyuP/Downloads"),
        ("D:", "/mnt/d"),
        ("file:///C:/Users/LibeiyuP/Downloads/file.pdf", "/mnt/c/Users/LibeiyuP/Downloads/file.pdf"),
        ("file://server/share/folder/file.txt", "/mnt/server/share/folder/file.txt"),
        ("/mnt/c/Users/test", "/mnt/c/Users/test"),
        ("", ""),
        (None, ""),
        # extra cases
        ("c:", "/mnt/c"),
        ("C:\\path with spaces\\file.txt", "/mnt/c/path with spaces/file.txt"),
    ],
)
def test_examples(inp, expected):
    assert convert_to_linux_path(inp) == expected


def test_no_change_for_unix_path():
    s = "/home/user/file"
    assert convert_to_linux_path(s) == s


def test_backslash_only_conversion():
    s = "some\\windows\\style\\path.txt"
    assert convert_to_linux_path(s) == "some/windows/style/path.txt"
