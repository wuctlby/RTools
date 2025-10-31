#%%
from urllib.parse import urlparse, unquote
import argparse
import re


def convert(String):
    r"""Convert various Windows-style paths to a Linux-style path.

    Handles inputs such as:
    - Raw Windows backslash paths: C:\\Users\\Name\\file.txt
    - Forward-slash variants: C:/Users/Name/file.txt
    - UNC paths: \\\\server\\share\\path -> /mnt/server/share/path
    - file:// URLs: file:///C:/path or file://server/share/path

    Mapping rules:
    - Drive letter -> /mnt/<lowercase-drive>/rest
    - UNC (\\server\share\...) -> /mnt/server/share/...
    - Other paths: collapse duplicate slashes and normalize to '/'
    """
    if String is None:
        return ""
    orig = String
    s = String.strip()
    if s == "":
        return ""

    # If it's a file:// URL, let urlparse handle decoding of percent-escapes
    low = s.lower()
    parsed = None
    unc_flag = False
    if low.startswith('file://'):
        parsed = urlparse(s)
        # For file URLs, netloc may contain server for UNC paths
        if parsed.netloc:
            # e.g. file://server/share/path -> //server/share/path
            s = '//' + parsed.netloc + parsed.path
            unc_flag = True
        else:
            s = parsed.path

    # Normalize backslashes to forward slashes for easier handling
    s = s.replace('\\', '/')

    # Decode percent-encodings
    s = unquote(s)

    # Collapse duplicate slashes. If this is a UNC-style path we preserve the
    # leading double slash and only collapse the remainder.
    if s.startswith('//') or orig.startswith('\\') or unc_flag:
        # keep leading '//' then collapse the rest
        rest = s[2:]
        rest = re.sub(r'/+', '/', rest)
        s = '//' + rest
    else:
        s = re.sub(r'/+', '/', s)

    # Detect UNC paths: either original started with backslashes or the normalized
    # path starts with two slashes
    if orig.startswith('\\') or s.startswith('//'):
        # remove leading // (exactly two) then strip any extra slashes
        rest = s[2:].lstrip('/')
        parts = rest.split('/')
        if len(parts) >= 2:
            server = parts[0]
            share = parts[1]
            tail = '/'.join(parts[2:]) if len(parts) > 2 else ''
            result = f"/mnt/{server}/{share}"
            if tail:
                result = result + '/' + tail
            return result
        else:
            return f"/mnt/{rest}"

    # Drive letter: e.g., C:/path or C:
    m = re.match(r'^([A-Za-z]):(?:/(.*))?$', s)
    if m:
        drive = m.group(1).lower()
        rest = m.group(2) or ''
        result = f"/mnt/{drive}"
        if rest:
            result = result + '/' + rest
        return result

    # Some file:// URLs or other inputs may produce a leading slash before the
    # drive letter, like '/C:/path'. Handle that as well.
    m2 = re.match(r'^/([A-Za-z]):(?:/(.*))?$', s)
    if m2:
        drive = m2.group(1).lower()
        rest = m2.group(2) or ''
        result = f"/mnt/{drive}"
        if rest:
            result = result + '/' + rest
        return result

    # If path starts with a single leading slash, keep it (it's already absolute)
    # Otherwise return normalized relative path
    if s.startswith('/'):
        return s

    return s

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("String", metavar="text",
                        default="string_to_convert", help="the path you want to convert to linux format")
    args = parser.parse_args()

    print(convert(args.String))
# %%
