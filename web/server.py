import http.cookiejar
import json
import os
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

XUI = "http://127.0.0.1:2053"
WEB = os.environ.get("VPNSTAN_WEB", "/opt/vpnstan/web")

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def xui_request(method, path, data=None, form=False):
    body = None
    headers = {}
    if data is not None:
        if form:
            body = urllib.parse.urlencode(data).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = json.dumps(data).encode()
            headers["Content-Type"] = "application/json"
    req = urllib.request.Request(XUI + path, data=body, headers=headers, method=method)
    with opener.open(req, timeout=30) as r:
        raw = r.read()
        return r.status, r.headers, raw

class Handler(BaseHTTPRequestHandler):
    def _json(self, status, obj, headers=None):
        raw = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        if headers:
            for k,v in headers.items():
                self.send_header(k,v)
        self.end_headers()
        self.wfile.write(raw)

    def _body(self):
        n = int(self.headers.get("Content-Length","0"))
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        if self.path == "/api/health":
            return self._json(200, {"ok": True, "name": "vpnstan", "version": "3x-ui-v2.9.0"})
        if self.path.startswith("/api/inbounds"):
            try:
                status, headers, raw = xui_request("GET", "/panel/api/inbounds/list")
                self.send_response(status)
                self.send_header("Content-Type", headers.get("Content-Type","application/json"))
                self.end_headers()
                self.wfile.write(raw)
            except Exception as e:
                self._json(502, {"success":False,"msg":"3X-UI unavailable","detail":str(e)})
            return
        if self.path.startswith("/api/clients"):
            try:
                status, headers, raw = xui_request("GET", "/panel/api/clients/list")
                self.send_response(status)
                self.send_header("Content-Type", headers.get("Content-Type","application/json"))
                self.end_headers()
                self.wfile.write(raw)
            except Exception as e:
                self._json(502, {"success":False,"msg":"3X-UI unavailable","detail":str(e)})
            return
        return self.static()

    def do_POST(self):
        if self.path == "/api/login":
            try:
                d = self._body()
                status, headers, raw = xui_request(
                    "POST", "/login",
                    {"username":d.get("username",""),"password":d.get("password","")},
                    form=True
                )
                self.send_response(status)
                for c in headers.get_all("Set-Cookie", []) if headers.get_all("Set-Cookie") else []:
                    self.send_header("Set-Cookie", c)
                self.send_header("Content-Type", headers.get("Content-Type","application/json"))
                self.end_headers()
                self.wfile.write(raw)
            except Exception as e:
                self._json(502, {"success":False,"msg":"خطا در اتصال به 3X-UI","detail":str(e)})
            return

        if self.path == "/api/clients/create":
            try:
                d = self._body()
                inbound_id = int(d["inboundId"])
                name = str(d["name"]).strip()
                gb = float(d["gb"])
                days = int(d["days"])
                if not name or gb <= 0 or days <= 0:
                    return self._json(400, {"success":False,"msg":"name/gb/days نامعتبر است"})

                expiry = 0 if days == 0 else __import__("time").time_ns() // 1_000_000 + days*86400000
                client = {
                    "email": name,
                    "totalGB": int(gb * 1024 * 1024 * 1024),
                    "expiryTime": expiry,
                    "enable": True
                }

                # The official 3X-UI API expects client JSON nested inside `settings`
                # for the inbound addClient endpoint.
                payload = {"settings": json.dumps({"clients":[client]}, ensure_ascii=False)}
                status, headers, raw = xui_request(
                    "POST", f"/panel/api/inbounds/addClient",
                    payload, form=True
                )
                self.send_response(status)
                self.send_header("Content-Type", headers.get("Content-Type","application/json"))
                self.end_headers()
                self.wfile.write(raw)
            except Exception as e:
                self._json(400, {"success":False,"msg":"ساخت Client ناموفق بود","detail":str(e)})
            return

        self._json(404, {"success":False,"msg":"Not found"})

    def static(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/" or path == "":
            path = "/index.html"
        if ".." in path:
            return self._json(400, {"error":"bad path"})
        full = os.path.join(WEB, path.lstrip("/"))
        if not os.path.isfile(full):
            return self._json(404, {"error":"not found"})
        mime = "text/plain"
        if full.endswith(".html"): mime="text/html; charset=utf-8"
        elif full.endswith(".js"): mime="application/javascript; charset=utf-8"
        elif full.endswith(".css"): mime="text/css; charset=utf-8"
        with open(full,"rb") as f: raw=f.read()
        self.send_response(200)
        self.send_header("Content-Type",mime)
        self.send_header("Content-Length",str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

port = int(os.environ.get("PORT", os.environ.get("VPNSTAN_PORT","3000")))
ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
