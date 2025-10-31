import re
import argparse
from urllib.parse import urlparse, unquote

def convert(path):
    """
    Convert Windows-style paths and file:// URLs to Linux-style.

    Rules:
    - file:///C:/foo -> /mnt/c/foo
    - file://server/share/path -> /mnt/server/share/path
    - C:\\foo -> /mnt/c/foo
    - \\\\server\\share\\path -> /mnt/server/share/path
    - Replace backslashes with slashes, collapse duplicates
    """

    if not path:
        return ""

    s = path.strip()
    if not s:
        return ""

    # Decode URL-encoded characters
    s = unquote(s)

    # Handle file:// URLs
    if s.lower().startswith("file://"):
        parsed = urlparse(s)
        s = parsed.path or ""

        # If it's a UNC-style file://server/share/path
        if parsed.netloc:
            server = parsed.netloc
            parts = s.strip("/").split("/")
            if len(parts) >= 1:
                share = parts[0]
                tail = "/".join(parts[1:]) if len(parts) > 1 else ""
                result = f"/mnt/{server}/{share}"
                if tail:
                    result += "/" + tail
                return result
            return f"/mnt/{server}"

        # Otherwise, local path, e.g., file:///C:/Users/...
        s = s.lstrip("/")

    # Normalize backslashes to slashes
    s = s.replace("\\", "/")

    # ✅ Detect UNC before collapsing slashes
    is_unc = path.startswith('\\\\') or path.startswith('//')

    # Collapse duplicate slashes (except protocol ones)
    s = re.sub(r'(?<!:)//+', '/', s)

    # Handle UNC paths (\\server\share or //server/share)
    if is_unc:
        s = s.lstrip('/')
        parts = s.split('/')
        if len(parts) >= 2:
            server, share = parts[0], parts[1]
            tail = '/'.join(parts[2:]) if len(parts) > 2 else ''
            result = f"/mnt/{server}/{share}"
            if tail:
                result += '/' + tail
            return result
        return f"/mnt/{s}"

    # Handle drive letter, e.g. C:/path
    m = re.match(r'^([A-Za-z]):/?(.*)$', s)
    if m:
        drive = m.group(1).lower()
        rest = m.group(2)
        if rest:
            return f"/mnt/{drive}/{rest}"
        else:
            return f"/mnt/{drive}"

    # Otherwise, just normalize slashes
    return re.sub(r'/+', '/', s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Windows path or file:// URL to Linux path")
    parser.add_argument("String", metavar="path", help="Path or URL to convert")
    args = parser.parse_args()

    print(convert(args.String))
