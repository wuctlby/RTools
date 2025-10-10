#%%
import argparse
import re

def convert(String):
    """
    Convert Windows-style paths to Linux-style.

    Rules:
    - Drive letter paths like C:\\foo -> /mnt/c/foo (drive letter lowercased)
    - UNC paths like \\\\server\\share\\path -> /mnt/server/share/path
    - Replace backslashes with forward slashes and collapse duplicate slashes
    - Preserve relative paths by only normalizing slashes
    """
    if String is None:
        return ""
    s = String.strip()
    if s == "":
        return ""

    # Normalize backslashes to slashes
    s = s.replace('\\', '/')

    # Collapse multiple slashes
    s = re.sub(r'/+', '/', s)

    # UNC paths: start with //server/share
    if s.startswith('//'):
        # remove leading //
        rest = s[2:]
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
            # just map to /mnt/<rest>
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

    # Otherwise, just return normalized path
    return s

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("String", metavar="text",
                        default="string_to_convert", help="the path you want to convert to linux format")
    args = parser.parse_args()

    print(convert(args.String))