# -*- coding: utf-8 -*-
"""
カスタムラベルスタジオ - 専用軽量同期サーバー (ポート 51467)
Dropbox共有フォルダ内で全PC自動データ読み書き(同期)を実現します。
"""

import http.server
import json
import os
import sys
import shutil
from datetime import datetime

PORT = 51467
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "label_data.json")
BACKUP_FILE = os.path.join(BASE_DIR, "label_data.backup.json")

class CustomLabelStudioHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        # API: 軽量ステータス確認（3秒ごとの高速ポーリング用）
        if self.path.startswith("/api/status"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._set_cors_headers()
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()

            if os.path.exists(DATA_FILE):
                try:
                    mtime_ms = int(os.path.getmtime(DATA_FILE) * 1000)
                    res = {
                        "exists": True,
                        "updatedAtMs": mtime_ms,
                        "size": os.path.getsize(DATA_FILE)
                    }
                except Exception as e:
                    res = {"exists": False, "error": str(e)}
            else:
                res = {"exists": False, "updatedAtMs": 0}

            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # API: データ読み込み
        if self.path.startswith("/api/data"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._set_cors_headers()
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()

            if os.path.exists(DATA_FILE):
                try:
                    with open(DATA_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    res = {
                        "exists": True,
                        "data": data,
                        "updatedAt": datetime.fromtimestamp(os.path.getmtime(DATA_FILE)).isoformat(),
                        "updatedAtMs": int(os.path.getmtime(DATA_FILE) * 1000)
                    }
                except Exception as e:
                    res = {"exists": False, "error": str(e)}
            else:
                res = {"exists": False, "data": None}

            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            return

        # 通常の静的ファイル配信（HTMLのキャッシュを抑止）
        if self.path == "/" or self.path.startswith("/index.html"):
            super().do_GET()
            return

        super().do_GET()

    def end_headers(self):
        # HTMLファイルのキャッシュを防止し、常に最新の変更がブラウザに届くようにする
        if self.path == "/" or self.path.startswith("/index.html") or self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def do_POST(self):
        # API: データ保存
        if self.path.startswith("/api/data"):
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length)

            try:
                payload = json.loads(post_body.decode("utf-8"))

                # 巻き戻り防止ガード: 既存ファイルの方がクライアントのタイムスタンプより新しい場合の上書きを拒否
                if os.path.exists(DATA_FILE) and not payload.get("force", False):
                    try:
                        current_mtime_ms = int(os.path.getmtime(DATA_FILE) * 1000)
                        client_ms = int(payload.get("updatedAtMs", 0))
                        # 既存ファイルが1.5秒以上新しい場合は巻き戻りと判定
                        if client_ms > 0 and current_mtime_ms > client_ms + 1500:
                            res = {
                                "success": False,
                                "conflict": True,
                                "message": "リモートにさらに新しいデータが存在します（巻き戻りを防止しました）",
                                "remoteUpdatedAtMs": current_mtime_ms
                            }
                            self.send_response(409)
                            self.send_header("Content-Type", "application/json; charset=utf-8")
                            self._set_cors_headers()
                            self.end_headers()
                            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
                            return
                    except Exception as e:
                        print(f"[警告] タイムスタンプ検査中に例外: {e}")

                # 既存データがあれば直前のバックアップを作成
                if os.path.exists(DATA_FILE):
                    try:
                        shutil.copyfile(DATA_FILE, BACKUP_FILE)
                    except Exception as e:
                        print(f"[警告] バックアップ作成に失敗: {e}")

                # 新しいデータを書き込み (アトミックに一時ファイル経由で保存)
                tmp_file = DATA_FILE + ".tmp"
                with open(tmp_file, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                os.replace(tmp_file, DATA_FILE)

                mtime_ms = int(os.path.getmtime(DATA_FILE) * 1000)
                res = {
                    "success": True,
                    "savedAt": datetime.now().isoformat(),
                    "savedAtMs": mtime_ms,
                    "updatedAtMs": mtime_ms,
                    "size": os.path.getsize(DATA_FILE)
                }
                status_code = 200
            except Exception as e:
                res = {"success": False, "error": str(e)}
                status_code = 500

            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        # ログ出力を簡潔に
        sys.stderr.write(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}\n")

def run():
    port = PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    server_address = ("127.0.0.1", port)
    httpd = http.server.HTTPServer(server_address, CustomLabelStudioHandler)
    print("=" * 60)
    print(f"  カスタムラベルスタジオ 自動同期サーバー起動")
    print(f"  URL : http://localhost:{port}/")
    print(f"  共有データファイル: {DATA_FILE}")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nサーバーを停止しました。")
        httpd.server_close()

if __name__ == "__main__":
    run()
