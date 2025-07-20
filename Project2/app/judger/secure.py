from typing import Optional

"""黑名单、白名单校验"""
def check_cmd_available(cmd:Optional[str]) -> bool:
    # 白名单
    whitelist_prefixes = [
        "gcc", "g++", "python", "python3", "timeout", "/usr/bin/time"
    ]

    # 黑名单
    blacklist_keywords = [
        "rm", "shutdown", "reboot", "mkfs", "dd", "kill", "init", "telnet",
        "ftp", "nc", "ncat", "wget", "curl", "scp", "chmod", "chown", ">", ">>",
        "echo", "cat", "nano", "vi", ";", "&&", "|", "`", "$(", "docker", "mount",
        "umount"
    ]
    
    if cmd is None:
        return True

    cmd = cmd.strip()

    # 黑名单检测
    for keyword in blacklist_keywords:
        if keyword in cmd:
            return False

    # 白名单检测
    for prefix in whitelist_prefixes:
        if cmd.startswith(prefix):
            return True

    return False