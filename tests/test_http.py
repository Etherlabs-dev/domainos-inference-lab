import contextlib
import io
import json
import os
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
import lab_http as h
import lab_cli

class Handler(BaseHTTPRequestHandler):
    status=200
    body={"data":[{"id":"domainos-qwen"}]}
    seen=[]
    def log_message(self,*args): pass
    def do_GET(self):
        type(self).seen.append((self.path,self.headers.get("Authorization")))
        self.send_response(type(self).status)
        if type(self).status==302:
            self.send_header("Location",self.server.base+"/stolen")
        self.end_headers()
        b=type(self).body
        self.wfile.write(b if isinstance(b,bytes) else json.dumps(b).encode())
    def do_POST(self):
        self.rfile.read(int(self.headers['Content-Length']))
        self.do_GET()

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
        cls.server.base=cls.base
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def setUp(self):
        Handler.status=200;Handler.body={"data":[{"id":"domainos-qwen"}]};Handler.seen=[]
    def test_json_and_auth_header(self):
        headers=h.proxy_headers('wk-test','ws-test')
        self.assertIn('data',h.request_json(self.base,'/v1/models',headers))
        self.assertEqual(Handler.seen,[('/v1/models','Bearer wk-test.ws-test')])
    def test_redirect_never_forwards_credentials(self):
        Handler.status=302
        with self.assertRaises(h.StatusError): h.request_json(self.base,'/redirect',{'Authorization':'Bearer secret-test'})
        self.assertEqual(len(Handler.seen),1)
    def test_error_body_not_exposed(self):
        Handler.status=401;Handler.body={'secret':'sensitive-test-marker'}
        with self.assertRaises(h.StatusError) as ctx:h.request_json(self.base,'/v1/models')
        self.assertEqual(str(ctx.exception),'HTTP 401')
    def test_invalid_json(self):
        Handler.body=b'not json'
        with self.assertRaises(h.LabError):h.request_json(self.base,'/v1/models')
    def test_non_object(self):
        Handler.body=[]
        with self.assertRaises(h.LabError):h.request_json(self.base,'/v1/models')
    def test_completion_and_usage_allowlist(self):
        Handler.body={'choices':[{'message':{'content':'Hello'}}],'usage':{'total_tokens':3,'private':'hidden','prompt_tokens':True}}
        self.assertEqual(h.completion(self.base,{}),('Hello',{'total_tokens':3}))
    def test_post_503_is_not_retried(self):
        Handler.status=503
        with self.assertRaises(h.StatusError):h.completion(self.base,{})
        self.assertEqual(len(Handler.seen),1)
    def test_malformed_completion(self):
        with self.assertRaises(h.LabError):h.completion(self.base,{})
    def test_response_size_limit(self):
        Handler.body=b'x'*101
        with patch.object(h,'MAX_BODY',100), self.assertRaises(h.LabError):h.request_json(self.base,'/v1/models')

class LogicTests(unittest.TestCase):
    def test_reject_unsafe_endpoints(self):
        for value in ['http://example.modal.run','https://x.modal.run@evil.com','https://x.modal.run/?token=a','https://x.modal.run/v1','https://evil.com','https://x.modal.run:bad']:
            with self.subTest(value=value),self.assertRaises(h.LabError):h.endpoint(value)
        self.assertEqual(h.endpoint('https://example.modal.run/'),'https://example.modal.run')
        self.assertEqual(h.endpoint('http://127.0.0.1:8888',local=True),'http://127.0.0.1:8888')
    def test_reject_header_injection(self):
        with self.assertRaises(h.LabError):h.proxy_headers('wk-test\nInjected','ws-test')
    def test_readiness_503_then_200(self):
        clock=[0];calls=[]
        def send(*a,**kw):
            calls.append(1)
            if len(calls)<3:raise h.StatusError(503)
            return {'data':[{'id':'domainos-qwen'}]}
        self.assertEqual(h.wait_ready('x',{},budget=20,interval=6,clock=lambda:clock[0],sleep=lambda v:clock.__setitem__(0,clock[0]+v),send=send),3)
    def test_readiness_deadline(self):
        clock=[0]
        def send(*a,**kw):raise h.StatusError(503)
        with self.assertRaises(h.LabError):h.wait_ready('x',{},budget=10,interval=6,clock=lambda:clock[0],sleep=lambda v:clock.__setitem__(0,clock[0]+v),send=send)
        self.assertEqual(clock[0],10)
    def test_readiness_401_not_retried(self):
        def send(*a,**kw):raise h.StatusError(401)
        with self.assertRaises(h.StatusError):h.wait_ready('x',{},send=send)
    def test_missing_model_fails_readiness(self):
        with self.assertRaises(h.LabError):h.wait_ready('x',{},send=lambda *a,**k:{'data':[]})
    def test_cloud_scripts_refuse_without_opt_in(self):
        for script in ['cloud_client.py','cloud_inference_test.py','readiness_test.py','security_test.py']:
            r=subprocess.run([sys.executable,script],capture_output=True,text=True)
            self.assertEqual(r.returncode,2,script)
            self.assertIn('Cloud traffic is disabled',r.stderr)
    def test_imports_do_not_send_requests(self):
        r=subprocess.run([sys.executable,'-c','import cloud_client,cloud_inference_test,readiness_test,security_test,client,auth_test'],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(r.stdout,'')
    def test_security_positive_and_negative_controls(self):
        sequence=[h.StatusError(401),h.StatusError(403),{'data':[{'id':'domainos-qwen'}]}]
        with patch.object(sys,'argv',['security_test.py','--allow-cloud']),patch.object(lab_cli,'endpoint',return_value='unused'),patch.object(lab_cli,'credentials',return_value={}),patch.object(lab_cli,'request_json',side_effect=sequence),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lab_cli.run_cloud('security'),0)
    def test_security_unexpected_status_and_access_fail(self):
        for value in [h.StatusError(503), {'data':[]}]:
            with patch.object(sys,'argv',['security_test.py','--allow-cloud']),patch.object(lab_cli,'endpoint',return_value='unused'),patch.object(lab_cli,'request_json',side_effect=value if isinstance(value,Exception) else None,return_value=value),contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(lab_cli.run_cloud('security'),1)

class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec=importlib.util.spec_from_file_location('audit','scripts/audit_secrets.py')
        cls.audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.audit)
    def test_hardcoded_generic_key_detected(self):
        value='Ab7'+'K9pQ2mX4vZ8rT6'
        found=self.audit.scan('source.py',f'api_key = {value!r}'.encode(),python=True)
        self.assertIn('hardcoded_credential_assignment',[x['kind'] for x in found])
        self.assertNotIn(value,json.dumps(found))
    def test_env_key_detected(self):
        raw=('LOCAL_API_KEY='+'random'+'Credential123').encode()
        self.assertTrue(self.audit.scan('.env',raw))
    def test_placeholder_allowed(self):
        self.assertEqual(self.audit.scan('.env.example',b'MODAL_PROXY_SECRET=ws-REPLACE'),[])
    def test_proxy_literal_detected(self):
        raw=('ws-'+'A1b2C3d4E5f6G7h8').encode()
        self.assertTrue(self.audit.scan('capture.log',raw))
    def test_personal_path_detected(self):
        raw=('/'+'Users/'+'review-person/project').encode()
        self.assertTrue(self.audit.scan('README.md',raw,identifiers=True))
    def test_binary_requires_review(self):
        self.assertEqual(self.audit.scan('capture',b'\xff')[0]['kind'],'binary_requires_manual_review')

class AdditionalLogicTests(unittest.TestCase):
    def test_default_readiness_one_request(self):
        with patch.object(sys,'argv',['readiness_test.py','--allow-cloud']),patch.object(lab_cli,'endpoint',return_value='unused'),patch.object(lab_cli,'credentials',return_value={}),patch.object(lab_cli,'request_json',side_effect=h.StatusError(503)) as send,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lab_cli.run_cloud('readiness'),1)
            self.assertEqual(send.call_count,1)
    def test_readiness_budget_must_be_finite(self):
        for budget in [0,-1,float('nan'),float('inf')]:
            with self.assertRaises(h.LabError):h.wait_ready('x',{},budget=budget)
    def test_remote_entrypoints_guard_cloud(self):
        import ast
        for name in ['gpu_test.py','modal_test.py']:
            from pathlib import Path
            tree=ast.parse(Path(name).read_text())
            main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
            # Execute only the local function body, with remote objects that fail if touched.
            main.decorator_list=[]
            namespace={};exec(compile(ast.Module(body=[main],type_ignores=[]),name,'exec'),namespace)
            with self.assertRaises(SystemExit):namespace['main']()


class ModelResponseTests(unittest.TestCase):
    def test_malformed_models_response_is_actionable(self):
        for value in [None, {}, "invalid", [], [None], [{"id":"wrong"}]]:
            with self.assertRaises(h.LabError): h.require_model({"data":value})


class LocalAuthTests(unittest.TestCase):
    def test_invalid_local_key_rejected(self):
        with patch.object(sys,'argv',['auth_test.py']),patch.object(lab_cli,'completion',side_effect=h.StatusError(401)),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lab_cli.run_local_security(),0)
    def test_invalid_local_key_accepted_fails(self):
        with patch.object(sys,'argv',['auth_test.py']),patch.object(lab_cli,'completion',return_value=('text',{})),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lab_cli.run_local_security(),1)
    def test_unexpected_local_failure_fails(self):
        with patch.object(sys,'argv',['auth_test.py']),patch.object(lab_cli,'completion',side_effect=h.StatusError(500)),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lab_cli.run_local_security(),1)
