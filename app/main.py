import json, uuid
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from .db import init_db, conn, now, log_action
from .llm import analyze
from .qualification import qualify, route


app=FastAPI(title='Northstar Analytics Sales Assistant')
templates=Jinja2Templates(directory='templates')
init_db()

@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    c=conn(); leads=c.execute('SELECT * FROM conversations ORDER BY updated_at DESC').fetchall(); c.close()
    return templates.TemplateResponse('index.html', {'request':request,'leads':leads})

@app.get('/api/leads/{cid}')
def lead(cid):
    c=conn(); conv=c.execute('SELECT * FROM conversations WHERE id=?',(cid,)).fetchone(); msgs=c.execute('SELECT * FROM messages WHERE conversation_id=? ORDER BY id',(cid,)).fetchall(); acts=c.execute('SELECT * FROM actions WHERE conversation_id=? ORDER BY id DESC',(cid,)).fetchall(); c.close()
    return {'conversation':dict(conv) if conv else None,'messages':[dict(x) for x in msgs],'actions':[dict(x) for x in acts]}

def ingest(channel,sender_id,sender_name,body,provider_message_id=None):
    c=conn(); cid=f'{channel.lower()}_{sender_id}'
    existing=c.execute('SELECT id FROM conversations WHERE id=?',(cid,)).fetchone()
    if not existing:
        c.execute('INSERT INTO conversations(id,channel,sender_id,sender_name,created_at,updated_at) VALUES(?,?,?,?,?,?)',(cid,channel,sender_id,sender_name,now(),now()))
    c.execute('INSERT INTO messages(conversation_id,direction,body,provider_message_id,created_at) VALUES(?,?,?,?,?)',(cid,'inbound',body,provider_message_id,now()))
    c.execute('UPDATE conversations SET updated_at=? WHERE id=?',(now(),cid)); c.commit(); c.close()
    log_action(cid,'inquiry_received',f'{channel} inquiry received')
    return cid

@app.post('/api/test/inquiry')
def test_inquiry(channel: str=Form(...), sender: str=Form(...), message: str=Form(...)):
    cid=ingest(channel,sender,sender,message)
    return {'conversation_id':cid}

@app.post('/api/leads/{cid}/process')
def process(cid):
    c=conn(); rows=c.execute('SELECT direction,body FROM messages WHERE conversation_id=? ORDER BY id',(cid,)).fetchall(); conv=c.execute('SELECT * FROM conversations WHERE id=?',(cid,)).fetchone(); c.close()
    result=analyze([dict(r) for r in rows])
    q=qualify(result.get('extracted_facts',{}))
    status=q['status']; rep=route(result.get('extracted_facts',{}).get('country')) if status=='qualified' else None
    c=conn(); c.execute('UPDATE conversations SET status=?,assigned_rep=?,qualification_json=?,updated_at=? WHERE id=?',(status,rep,json.dumps(q),now(),cid));
    if result.get('reply'):
        c.execute('INSERT INTO messages(conversation_id,direction,body,created_at) VALUES(?,?,?,?)',(cid,'outbound',result['reply'],now()))
    c.commit(); c.close(); log_action(cid,'qualification',json.dumps({'status':status,'evidence':q['evidence'],'missing':q['missing']}))
    if rep: log_action(cid,'routing',f'assigned={rep}')
    return {'status':status,'assignment':rep,'qualification':q,'reply':result.get('reply')}

@app.post('/api/leads/{cid}/takeover')
def takeover(cid):
    c=conn(); c.execute('UPDATE conversations SET takeover=1 WHERE id=?',(cid,)); c.commit(); c.close(); log_action(cid,'takeover','Automation stopped by human'); return {'ok':True}

# Real provider webhook endpoints. They validate/parse only after provider credentials are configured.
@app.get('/webhooks/meta')
def meta_verify(request: Request):
    from os import getenv
    q=request.query_params
    if q.get('hub.verify_token')==getenv('META_VERIFY_TOKEN'):
        return int(q.get('hub.challenge','0'))
    return JSONResponse({'error':'verification failed'},status_code=403)

@app.post('/webhooks/meta')
async def meta_webhook(request: Request):
    payload=await request.json(); return {'received':True,'note':'Provider payload accepted; channel-specific parsing should create an inquiry via ingest().' }
