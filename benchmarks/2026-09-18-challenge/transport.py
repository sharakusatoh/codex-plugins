from pathlib import Path
import os,shutil,json,queue,subprocess,threading,time
ROOT=Path(__file__).resolve().parent
CODEX=Path(os.environ.get('BENCH_CODEX') or shutil.which('codex') or 'codex')
class Server:
    def __init__(self):
        overrides = {
            "mcp_servers.node_repl.enabled": "false",
            "features.plugins": "false",
            "features.apps": "false",
            "features.memories": "false",
            "features.shell_tool": "false",
            "project_doc_max_bytes": "0",
            "web_search": '"disabled"',
            "model_reasoning_effort": '"low"',
            "model_reasoning_summary": '"none"',
            "model_verbosity": '"low"',
        }
        command = [str(CODEX)]
        for key, value in overrides.items():
            command += ["-c", key + "=" + value]
        command += ["app-server"]
        self.messages = queue.Queue()
        self.request_id = 0
        self.err = (ROOT / "server.stderr.log").open("a", encoding="utf-8")
        self.process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=self.err, text=True, encoding="utf-8", bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        def consume():
            for line in self.process.stdout:
                try:
                    self.messages.put(json.loads(line))
                except json.JSONDecodeError:
                    pass
            self.messages.put({"serverExited": self.process.poll()})
        threading.Thread(target=consume, daemon=True).start()
        self.call("initialize", {
            "clientInfo": {"name": "sharaku-persona-benchmark", "version": "1.0.0"},
            "capabilities": {"experimentalApi": True},
        })
        self.send({"method": "initialized"})

    def send(self, data):
        self.process.stdin.write(json.dumps(data, ensure_ascii=False) + "\n")
        self.process.stdin.flush()

    def receive(self, seconds=90):
        message = self.messages.get(timeout=seconds)
        if "serverExited" in message:
            raise RuntimeError("Codex app server exited unexpectedly")
        if "id" in message and "method" in message:
            # Never approve an unexpected side-effecting request.
            self.send({"id": message["id"], "error": {"code": -32601, "message": "Tools disabled for benchmark"}})
        return message

    def call(self, method, params):
        self.request_id += 1
        ident = self.request_id
        self.send({"id": ident, "method": method, "params": params})
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            msg = self.receive(max(0.1, deadline-time.monotonic()))
            if msg.get("id") == ident:
                if "error" in msg:
                    raise RuntimeError(json.dumps(msg["error"], ensure_ascii=False))
                return msg["result"]
        raise TimeoutError(method)

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
        self.err.close()
