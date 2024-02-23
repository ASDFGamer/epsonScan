#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import os
import sys
from typing import NoReturn, Optional


def fatal_error(message: str, exit_code: int = 1) -> NoReturn:
    print(message, file=sys.stderr)
    sys.exit(exit_code)


def get_env_var(
    name: str, default: Optional[str] = None, required: bool = False
) -> str:
    try:
        return os.environ[name]
    except KeyError:
        if required:
            fatal_error("The env var {} has to be set".format(name))
        if default is None:
            fatal_error(
                """
                The env var {} should have a default value assigned, but has none.
                This is a bug.
                """.format(
                    name
                )
            )
        return default


def update_config(config_file_path: str = "/docker/scan_config.SF2") -> None:
    replace_values: dict[str, str] = {}

    replace_values["SCANNER_IP"] = get_env_var("SCANNER_IP", required=True)
    replace_values["DPI"] = get_env_var("DPI", default="300")

    update_config_file(config_file_path, replace_values)


def update_config_file(config_file_path: str, replace_values: dict[str, str]) -> None:
    with open(config_file_path, encoding="UTF-8") as f:
        new_config = f.read()

    for key, value in replace_values.items():
        new_config.replace(key, value)

    with open(config_file_path, "w", encoding="UTF-8") as f:
        f.write(new_config)


def run_server(
    handler_class: type[BaseHTTPRequestHandler] = SimpleHTTPRequestHandler,
):
    """Entrypoint for python server"""
    httpd = HTTPServer(("0.0.0.0", 8080), handler_class)
    print("Launching server")
    httpd.serve_forever()


def main():
    update_config()
    run_server()


if __name__ == "__main__":
    main()
