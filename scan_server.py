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

print(f"Run {__name__}")

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


class ScanHTTPRequestHandler(BaseHTTPRequestHandler):

    valid_formats = ["pnm", "tiff", "png", "jpeg", "pdf"]

    mime_types = {
        "pnm": "image/x-portable-anymap",
        "tiff": "image/tiff",
        "png": "image/png",
        "jpeg": "image/jpeg",
        "pdf": "application/pdf",
    }

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
        scanner_ip = get_env_var("SCANNER_IP", required=True)
        prefix = self._generate_prefix()
        device = f"epsonds:net:{scanner_ip}"
        file_format = get_env_var("FILE_FORMAT", default="pdf").lower()
        if file_format not in self.valid_formats:
            valid_formats_str = ",".join(self.valid_formats)
            fatal_error(
                f"Format {file_format} is invalid. Valid formats are: {valid_formats_str}"
            )
        output_file = self._generate_prefix() + "." + file_format
        dpi = get_env_var("DPI", default="300")
        command = f"scanimage --device {device} --format={file_format} --output-file {output_file} --progress --resolution {dpi}"
        try:
            subprocess.run(command.split(), check=True)
        except subprocess.CalledProcessError as e:
            self.send_response(500)
            self.end_headers()
            self._write_json(
                {
                    "message": "Error while scanning",
                    "returncode": e.returncode,
                    "stdout": e.stdout,
                    "stderr": e.stderr,
                    "command": e.cmd,
                }
            )
        else:
            self.send_response(200)
            self.end_headers()

            print(f"Prefix: {prefix}")
            self._write_json({"filename": output_file})

    def get_file(self):
        filename = self.path.split("/")[-1]
        if not filename.isalnum():
            self.send_response(404)
            self.end_headers()
            self._write_json({"message": "Invalid Filename"})
        self.send_response(200)
        file_format = get_env_var("FILE_FORMAT", default="pdf").lower()
        mime_type = self.mime_types[file_format]
        self.send_header("Content-type", mime_type)
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
    httpd = ThreadingHTTPServer(("", 8080), handler_class)
    print("Launching server")
    httpd.serve_forever()


def main():
    print("Start")
    run_server(ScanHTTPRequestHandler)


if __name__ == "__main__":
    main()
