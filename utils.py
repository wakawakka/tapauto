import logging
from uuid import uuid4


def get_logger(filepath=None, level=logging.INFO) -> logging.Logger:
    logger_id = uuid4().hex[:4]
    logger = logging.Logger(logger_id)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        # "%(asctime)s - %(levelname)s - %(message)s"
    )

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if filepath:
        fh = logging.FileHandler(filepath, encoding="utf8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def create_proxychains_conf(path, proxy_host, proxy_port, proxy_user, proxy_password):
    pattern = (
        "strict_chain\n"
        "proxy_dns\n"
        "remote_dns_subnet 224\n"
        "localnet 127.0.0.0/255.0.0.0\n"
        "delete_fake_ip_after_child_exits 1\n"
        "default_target PROXY\n"
        "use_fake_ip_when_hostname_not_matched 1\n"
        "map_resolved_ip_to_host 0\n"
        "search_for_host_by_resolved_ip 0\n"
        "resolve_locally_if_match_hosts 1\n"
        "gen_fake_ip_using_hashed_hostname 0\n"
        "first_tunnel_uses_ipv4 1\n"
        "first_tunnel_uses_ipv6 0\n"
        "log_level 400\n"
        "[ProxyList]\n"
        f"socks5 {proxy_host} {proxy_port} {proxy_user} {proxy_password}\n"
    )
    written = 0
    with open(path, "w") as f:
        written = f.write(pattern)
    return written > 0
