"""Send a supplied task script to the installed Blender Foundation MCP addon.

Uses the local addon protocol read from the user's installed extension.
The live Blender scene and sandbox remain in control; no preferences are changed.
"""
import socket,json,sys
from pathlib import Path
code=Path(sys.argv[1]).read_text(encoding='utf-8')
with socket.create_connection(('localhost',9876),timeout=10) as s:
    s.settimeout(45)
    s.sendall((json.dumps({'type':'execute','code':code,'strict_json':True})+'\0').encode())
    result=b''
    while b'\0' not in result:
        chunk=s.recv(1024*1024)
        if not chunk:break
        result+=chunk
    data=json.loads(result.rstrip(b'\0'))
    print(json.dumps(data,indent=2))
    if data.get('status')!='ok':raise SystemExit(1)
