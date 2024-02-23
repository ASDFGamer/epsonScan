#!/usr/bin/env python3

from http.server import (
    BaseHTTPRequestHandler,
    SimpleHTTPRequestHandler,
    ThreadingHTTPServer,
)
import json
import os
import random
import string
import subprocess
import sys
from typing import Any, NoReturn, Optional

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
SCAN_DIR = os.path.join(SCRIPT_DIR, "scans")


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


def update_config() -> None:
    replace_values: dict[str, str] = {}

    replace_values["DPI"] = get_env_var("DPI", default="300")

    if os.path.isfile(SCAN_DIR):
        fatal_error("{} has to be a dir and not a file".format(SCAN_DIR))
    if not os.path.isdir(SCAN_DIR):
        os.mkdir(SCAN_DIR)

    replace_values["RESULT_FOLDER"] = SCAN_DIR
    update_config_file(replace_values)


def update_config_file(replace_values: dict[str, str]) -> None:
    config_file_path = "./scan_config.SF2"
    with open(config_file_path, encoding="UTF-8") as f:
        new_config = f.read()

    for key, value in replace_values.items():
        print(f"Replace {key} with {value}")
        new_config = new_config.replace(key, value)

    with open(config_file_path, "w", encoding="UTF-8") as f:
        f.write(new_config)

    with open(config_file_path + ".bak", "w", encoding="UTF-8") as f:
        f.write(new_config)


class ScanHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        cleaned_path = self.path.lower().rstrip("/")

        if cleaned_path == "/scan":
            self.do_scan()
        elif cleaned_path.startswith("/files"):
            self.get_file()
        else:
            self.send_response(404)
            self.end_headers()
        return

    def do_scan(self):
        scanner_ip = get_env_var("SCANNER_IP")
        prefix = self._generate_prefix()
        update_config_file({"PREFIX": prefix})
        command = "epsonscan2 --scan {} ./scan_config.SF2".format(scanner_ip)
        try:
            subprocess.run(command.split(), check=True)
        except subprocess.CalledProcessError as e:
            self.send_response(500)
            self.end_headers()
            self._write_json(
                {
                    "message": "Error while scanning",
                    "returncode": e.returncode,
                    "output": e.output,
                    "command": e.cmd,
                }
            )
        else:
            self.send_response(200)
            self.end_headers()
            files = [
                filename
                for filename in os.listdir(SCAN_DIR)
                if filename.startswith(prefix)
            ]
            print(f"Prefix: {prefix}")
            self._write_json({"filename": files[0]})
        finally:
            update_config_file({prefix: "PREFIX"})

    def get_file(self):

        filename = self.path.split("/")[-1]
        if not filename.isalnum():
            self.send_response(404)
            self.end_headers()
            self._write_json({"message": "Invalid Filename"})
        self.send_response(200)
        self.send_header("Content-type", "application/pdf")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        with open(os.path.join(SCAN_DIR, filename), "rb") as file:
            self.wfile.write(file.read())  # Read the file and send the contents

    def _write_json(self, data: dict[str, Any]):
        message = json.dumps(data)
        self.wfile.write(message.encode("UTF-8"))

    def _generate_prefix(self) -> str:
        letters = string.ascii_lowercase
        while True:
            prefix = "".join(random.choice(letters) for _ in range(8))
            files = [
                filename
                for filename in os.listdir(SCAN_DIR)
                if filename.startswith(prefix)
            ]
            if len(files) == 0:
                return prefix


def run_server(
    handler_class: type[BaseHTTPRequestHandler] = SimpleHTTPRequestHandler,
):
    """Entrypoint for python server"""
    httpd = ThreadingHTTPServer(("0.0.0.0", 8080), handler_class)
    print("Launching server")
    httpd.serve_forever()


def main():
    update_config()
    run_server(ScanHTTPRequestHandler)


if __name__ == "__main__":
    main()
