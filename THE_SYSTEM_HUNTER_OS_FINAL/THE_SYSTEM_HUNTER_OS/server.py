import os, json, sqlite3, hashlib, hmac, base64, secrets, datetime, mimetypes
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
ROOT=os.path.dirname(os.path.abspath(__file__)); DB=os.environ.get('DB_PATH',os.path.join(ROOT,'system.sqlite3')); PORT=int(os.environ.get('PORT','3000')); SECRET=os.environ.get('JWT_SECRET','CHANGE_THIS_SECRET')
con=sqlite3.connect(DB,check_same_thread=False); con.row_factory=sqlite3.Row; con.execute('PRAGMA foreign_keys=ON'); con.execute('PRAGMA journal_mode=WAL')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def today(): return datetime.date.today().isoformat()
def uid(): return secrets.token_hex(16)
def hashpw(p):
 s=secrets.token_bytes(16); return base64.b64encode(s).decode()+':'+hashlib.scrypt(p.encode(),salt=s,n=16384,r=8,p=1).hex()
def checkpw(p,h):
 try:s,hh=h.split(':'); return hmac.compare_digest(hashlib.scrypt(p.encode(),salt=base64.b64decode(s),n=16384,r=8,p=1).hex(),hh)
 except:return False
def token(u):
 raw=f'{u}.{int(datetime.datetime.now(datetime.timezone.utc).timestamp())+2592000}'.encode(); sig=hmac.new(SECRET.encode(),raw,hashlib.sha256).digest(); return base64.urlsafe_b64encode(raw+b'.'+sig).decode()
def auth(t):
 try:
  raw=base64.urlsafe_b64decode(t.encode()); data,sig=raw.rsplit(b'.',1); uid0,exp=data.decode().split('.',1)
  if int(exp)<int(datetime.datetime.now(datetime.timezone.utc).timestamp()) or not hmac.compare_digest(hmac.new(SECRET.encode(),data,hashlib.sha256).digest(),sig): return None
  return uid0
 except:return None
schema='''
CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,email TEXT UNIQUE,password_hash TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS profiles(id TEXT PRIMARY KEY,user_id TEXT UNIQUE,hunter_name TEXT NOT NULL,avatar TEXT DEFAULT '',theme TEXT DEFAULT 'dark',timezone TEXT DEFAULT 'UTC',currency TEXT DEFAULT 'DZD',academic_year TEXT DEFAULT '',bac_date TEXT DEFAULT '',notifications INTEGER DEFAULT 1,created_at TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS stats(id TEXT PRIMARY KEY,user_id TEXT,name TEXT,description TEXT DEFAULT '',stat_xp INTEGER DEFAULT 0,created_at TEXT,UNIQUE(user_id,name),FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS quests(id TEXT PRIMARY KEY,user_id TEXT,title TEXT,category TEXT DEFAULT 'Personal',difficulty TEXT DEFAULT 'Normal',status TEXT DEFAULT 'Not Started',date TEXT,deadline TEXT,xp_reward INTEGER DEFAULT 30,credit_reward INTEGER DEFAULT 10,xp_earned INTEGER DEFAULT 0,credits_earned INTEGER DEFAULT 0,stat_id TEXT,skill_id TEXT,mission_id TEXT,priority TEXT DEFAULT 'Medium',boss_quest INTEGER DEFAULT 0,notes TEXT DEFAULT '',created_at TEXT,updated_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,FOREIGN KEY(stat_id) REFERENCES stats(id) ON DELETE SET NULL,FOREIGN KEY(skill_id) REFERENCES skills(id) ON DELETE SET NULL,FOREIGN KEY(mission_id) REFERENCES missions(id) ON DELETE SET NULL);
CREATE TABLE IF NOT EXISTS missions(id TEXT PRIMARY KEY,user_id TEXT,title TEXT,year INTEGER,quarter TEXT,month INTEGER,category TEXT DEFAULT '',status TEXT DEFAULT 'Active',priority TEXT DEFAULT 'Medium',deadline TEXT,progress INTEGER DEFAULT 0,xp_reward INTEGER DEFAULT 0,credit_reward INTEGER DEFAULT 0,boss_fight INTEGER DEFAULT 0,victory_condition TEXT DEFAULT '',why_it_matters TEXT DEFAULT '',notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS skills(id TEXT PRIMARY KEY,user_id TEXT,name TEXT,category TEXT DEFAULT '',status TEXT DEFAULT 'Learning',skill_xp INTEGER DEFAULT 0,target TEXT DEFAULT '',deadline TEXT,source TEXT DEFAULT '',source_url TEXT DEFAULT '',notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS daily_logs(id TEXT PRIMARY KEY,user_id TEXT,date TEXT,top1 TEXT DEFAULT '',top2 TEXT DEFAULT '',top3 TEXT DEFAULT '',energy INTEGER DEFAULT 0,focus INTEGER DEFAULT 0,notes TEXT DEFAULT '',closed INTEGER DEFAULT 0,created_at TEXT,UNIQUE(user_id,date),FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS prayers(id TEXT PRIMARY KEY,user_id TEXT,date TEXT,fajr INTEGER DEFAULT 0,dhuhr INTEGER DEFAULT 0,asr INTEGER DEFAULT 0,maghrib INTEGER DEFAULT 0,isha INTEGER DEFAULT 0,UNIQUE(user_id,date),FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS quran_logs(id TEXT PRIMARY KEY,user_id TEXT,date TEXT,pages INTEGER DEFAULT 0,minutes INTEGER DEFAULT 0,surah TEXT DEFAULT '',notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS charity_logs(id TEXT PRIMARY KEY,user_id TEXT,date TEXT,amount REAL DEFAULT 0,type TEXT DEFAULT 'Sadaqah',notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS books(id TEXT PRIMARY KEY,user_id TEXT,title TEXT,author TEXT DEFAULT '',status TEXT DEFAULT 'Want to Read',pages INTEGER DEFAULT 0,pages_read INTEGER DEFAULT 0,started TEXT,finished TEXT,category TEXT DEFAULT '',notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS school_tasks(id TEXT PRIMARY KEY,user_id TEXT,subject TEXT,task TEXT,type TEXT DEFAULT 'Homework',status TEXT DEFAULT 'Not Started',priority TEXT DEFAULT 'Medium',deadline TEXT,grade REAL,estimated_min INTEGER DEFAULT 0,actual_min INTEGER DEFAULT 0,notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS lessons(id TEXT PRIMARY KEY,user_id TEXT,subject TEXT,title TEXT,chapter TEXT DEFAULT '',status TEXT DEFAULT 'Not Started',progress INTEGER DEFAULT 0,deadline TEXT,notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS study_sessions(id TEXT PRIMARY KEY,user_id TEXT,date TEXT,subject TEXT,minutes INTEGER DEFAULT 0,focus_score INTEGER DEFAULT 0,notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS fitness_logs(id TEXT PRIMARY KEY,user_id TEXT,date TEXT,workout TEXT,type TEXT DEFAULT 'Strength',duration INTEGER DEFAULT 0,performance TEXT DEFAULT '',energy INTEGER DEFAULT 0,notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS meals(id TEXT PRIMARY KEY,user_id TEXT,date TEXT,meal_type TEXT,food TEXT,water_ml INTEGER DEFAULT 0,protein_note TEXT DEFAULT '',energy INTEGER DEFAULT 0,notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS hygiene_logs(id TEXT PRIMARY KEY,user_id TEXT,date TEXT,shower INTEGER DEFAULT 0,teeth_am INTEGER DEFAULT 0,teeth_pm INTEGER DEFAULT 0,skincare INTEGER DEFAULT 0,hair INTEGER DEFAULT 0,room INTEGER DEFAULT 0,clothes INTEGER DEFAULT 0,notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS savings_goals(id TEXT PRIMARY KEY,user_id TEXT,goal TEXT,target REAL,current REAL DEFAULT 0,deadline TEXT,priority TEXT DEFAULT 'Medium',status TEXT DEFAULT 'Active',notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS finance_transactions(id TEXT PRIMARY KEY,user_id TEXT,date TEXT,description TEXT,type TEXT,amount REAL,category TEXT DEFAULT '',notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS shopping_items(id TEXT PRIMARY KEY,user_id TEXT,item TEXT,price REAL DEFAULT 0,priority TEXT DEFAULT 'Medium',category TEXT DEFAULT '',need_or_want TEXT DEFAULT 'Want',status TEXT DEFAULT 'Planned',link TEXT DEFAULT '',notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS rewards(id TEXT PRIMARY KEY,user_id TEXT,reward TEXT,cost INTEGER,category TEXT DEFAULT '',description TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS credit_transactions(id TEXT PRIMARY KEY,user_id TEXT,description TEXT,date TEXT,type TEXT,amount INTEGER,quest_id TEXT,reward_id TEXT,created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS universities(id TEXT PRIMARY KEY,user_id TEXT,university TEXT,country TEXT DEFAULT '',program TEXT DEFAULT '',degree TEXT DEFAULT '',deadline TEXT,status TEXT DEFAULT 'Researching',scholarship TEXT DEFAULT '',tuition REAL,requirements TEXT DEFAULT '',documents TEXT DEFAULT '',website TEXT DEFAULT '',priority TEXT DEFAULT 'Medium',notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS scholarships(id TEXT PRIMARY KEY,user_id TEXT,scholarship TEXT,organization TEXT DEFAULT '',country TEXT DEFAULT '',eligibility TEXT DEFAULT '',deadline TEXT,status TEXT DEFAULT 'Research',amount REAL,requirements TEXT DEFAULT '',documents TEXT DEFAULT '',website TEXT DEFAULT '',notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS pomodoro_sessions(id TEXT PRIMARY KEY,user_id TEXT,date TEXT,started_at TEXT,ended_at TEXT,duration INTEGER DEFAULT 25,subject TEXT DEFAULT '',completed INTEGER DEFAULT 0,notes TEXT DEFAULT '',created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS reviews(id TEXT PRIMARY KEY,user_id TEXT,kind TEXT,period TEXT,data TEXT DEFAULT '{}',created_at TEXT,UNIQUE(user_id,kind,period),FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
'''
# create tables that are referenced before later declarations without FK resolution issue in SQLite
con.executescript(schema)
resources={
'quests': ['title','category','difficulty','status','date','deadline','xp_reward','credit_reward','stat_id','skill_id','mission_id','priority','boss_quest','notes'],
'missions':['title','year','quarter','month','category','status','priority','deadline','progress','xp_reward','credit_reward','boss_fight','victory_condition','why_it_matters','notes'],
'skills':['name','category','status','skill_xp','target','deadline','source','source_url','notes'],
'books':['title','author','status','pages','pages_read','started','finished','category','notes'],
'school_tasks':['subject','task','type','status','priority','deadline','grade','estimated_min','actual_min','notes'],
'lessons':['subject','title','chapter','status','progress','deadline','notes'],
'study_sessions':['date','subject','minutes','focus_score','notes'],
'fitness_logs':['date','workout','type','duration','performance','energy','notes'],
'meals':['date','meal_type','food','water_ml','protein_note','energy','notes'],
'hygiene_logs':['date','shower','teeth_am','teeth_pm','skincare','hair','room','clothes','notes'],
'savings_goals':['goal','target','current','deadline','priority','status','notes'],
'finance_transactions':['date','description','type','amount','category','notes'],
'shopping_items':['item','price','priority','category','need_or_want','status','link','notes'],
'rewards':['reward','cost','category','description'],
'universities':['university','country','program','degree','deadline','status','scholarship','tuition','requirements','documents','website','priority','notes'],
'scholarships':['scholarship','organization','country','eligibility','deadline','status','amount','requirements','documents','website','notes'],
'quran_logs':['date','pages','minutes','surah','notes'],
'charity_logs':['date','amount','type','notes'],
'pomodoro_sessions':['date','started_at','ended_at','duration','subject','completed','notes'],
'stats':['name','description','stat_xp'],
'reviews':['kind','period','data']}
nums={'xp_reward','credit_reward','progress','month','year','skill_xp','pages','pages_read','estimated_min','actual_min','minutes','focus_score','duration','energy','water_ml','shower','teeth_am','teeth_pm','skincare','hair','room','clothes','target','current','amount','price','cost','boss_fight','grade','tuition','completed','stat_xp'}
def lvl(x): return int((max(0,x)/250)**0.5)+1
def rank(l): return 'SSS-RANK' if l>=250 else 'SS-RANK' if l>=175 else 'S-RANK' if l>=120 else 'A-RANK' if l>=80 else 'B-RANK' if l>=50 else 'C-RANK' if l>=25 else 'D-RANK' if l>=10 else 'E-RANK'
def profile(uid0):
 p=dict(con.execute('SELECT * FROM profiles WHERE user_id=?',(uid0,)).fetchone()); xp=con.execute("SELECT COALESCE(SUM(xp_earned),0) FROM quests WHERE user_id=? AND status='Complete'",(uid0,)).fetchone()[0] or 0; cr=con.execute('SELECT COALESCE(SUM(amount),0) FROM credit_transactions WHERE user_id=?',(uid0,)).fetchone()[0] or 0; l=lvl(xp); lo=250*(l-1)**2; hi=250*l**2
 p.update(totalXP=int(xp),credits=int(cr),level=l,rank=rank(l),xpFloor=lo,xpCeiling=hi,xpToNext=max(0,hi-xp),progress=max(0,min(1,(xp-lo)/max(1,hi-lo))),activeQuests=con.execute("SELECT COUNT(*) FROM quests WHERE user_id=? AND status!='Complete'",(uid0,)).fetchone()[0],completedQuests=con.execute("SELECT COUNT(*) FROM quests WHERE user_id=? AND status='Complete'",(uid0,)).fetchone()[0])
 return p
def ensure_day(uid0,d):
 r=con.execute('SELECT * FROM daily_logs WHERE user_id=? AND date=?',(uid0,d)).fetchone()
 if not r: con.execute('INSERT INTO daily_logs(id,user_id,date,created_at) VALUES(?,?,?,?)',(uid(),uid0,d,now())); con.commit()

def dashboard(uid0):
 d=today(); ensure_day(uid0,d)
 prayer=dict(con.execute('SELECT * FROM prayers WHERE user_id=? AND date=?',(uid0,d)).fetchone() or {'date':d,'fajr':0,'dhuhr':0,'asr':0,'maghrib':0,'isha':0})
 pq=sum(prayer.get(x,0) for x in ['fajr','dhuhr','asr','maghrib','isha'])
 week=(datetime.date.fromisoformat(d)-datetime.timedelta(days=6)).isoformat()
 xpweek=con.execute("SELECT COALESCE(SUM(xp_earned),0) FROM quests WHERE user_id=? AND status='Complete' AND date>=?",(uid0,week)).fetchone()[0] or 0
 finance=con.execute("SELECT COALESCE(SUM(CASE WHEN type='Income' THEN amount WHEN type='Expense' THEN -amount ELSE 0 END),0) FROM finance_transactions WHERE user_id=?",(uid0,)).fetchone()[0] or 0
 return {'profile':profile(uid0),'today':d,'quests':[dict(x) for x in con.execute("SELECT * FROM quests WHERE user_id=? AND (date=? OR (status!='Complete' AND deadline<=?)) ORDER BY status='Complete', priority DESC, deadline LIMIT 30",(uid0,d,d)).fetchall()],'prayer':prayer,'prayerPct':pq*20,'quranToday':dict(con.execute('SELECT COALESCE(SUM(pages),0) pages,COALESCE(SUM(minutes),0) minutes FROM quran_logs WHERE user_id=? AND date=?',(uid0,d)).fetchone()),'school':[dict(x) for x in con.execute("SELECT * FROM school_tasks WHERE user_id=? AND status!='Complete' ORDER BY deadline LIMIT 6",(uid0,)).fetchall()],'lessons':[dict(x) for x in con.execute("SELECT * FROM lessons WHERE user_id=? AND status!='Complete' ORDER BY deadline LIMIT 6",(uid0,)).fetchall()],'books':[dict(x) for x in con.execute("SELECT * FROM books WHERE user_id=? AND status='Reading' LIMIT 5",(uid0,)).fetchall()],'skills':[dict(x) for x in con.execute("SELECT * FROM skills WHERE user_id=? ORDER BY skill_xp DESC LIMIT 8",(uid0,)).fetchall()],'missions':[dict(x) for x in con.execute("SELECT * FROM missions WHERE user_id=? AND status!='Complete' ORDER BY boss_fight DESC,deadline LIMIT 6",(uid0,)).fetchall()],'financeBalance':finance,'xpWeek':xpweek,'overdue':con.execute("SELECT COUNT(*) FROM quests WHERE user_id=? AND status!='Complete' AND deadline IS NOT NULL AND deadline<?",(uid0,d)).fetchone()[0]}
class H(BaseHTTPRequestHandler):
 def send(self,status,data,ctype='application/json'):
  self.send_response(status); self.send_header('Content-Type',ctype); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Headers','Content-Type, Authorization'); self.send_header('Access-Control-Allow-Methods','GET,POST,PATCH,DELETE,OPTIONS'); self.end_headers(); self.wfile.write(data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode())
 def body(self):
  n=int(self.headers.get('Content-Length','0')); return json.loads(self.rfile.read(n) or b'{}')
 def uid(self):
  a=self.headers.get('Authorization',''); return auth(a[7:]) if a.startswith('Bearer ') else None
 def do_OPTIONS(self): self.send(204,b'')
 def do_GET(self):
  p=urlparse(self.path); path=p.path; qs=parse_qs(p.query)
  if path=='/api/health':
   u=self.uid();
   if not u:return self.send(401,{'error':'Unauthorized'})
   checks={'orphaned':con.execute("SELECT COUNT(*) FROM quests q LEFT JOIN users u ON u.id=q.user_id WHERE u.id IS NULL").fetchone()[0],'negative_xp':con.execute('SELECT COUNT(*) FROM quests WHERE user_id=? AND xp_reward<0',(u,)).fetchone()[0],'negative_money':con.execute('SELECT COUNT(*) FROM finance_transactions WHERE user_id=? AND amount<0',(u,)).fetchone()[0]}; return self.send(200,{'status':'ONLINE' if not any(checks.values()) else 'WARNING','checks':checks})
  if path.startswith('/api/'):
   u=self.uid();
   if not u:return self.send(401,{'error':'Unauthorized'})
   parts=path[5:].strip('/').split('/')
   if parts[0]=='me': return self.send(200,profile(u))
   if parts[0]=='dashboard': return self.send(200,dashboard(u))
   if parts[0]=='analytics':
    days=int(qs.get('days',['30'])[0]); start=(datetime.date.today()-datetime.timedelta(days=days-1)).isoformat(); rows=[]
    for i in range(days):
     d=(datetime.date.today()-datetime.timedelta(days=days-1-i)).isoformat(); xp=con.execute("SELECT COALESCE(SUM(xp_earned),0) FROM quests WHERE user_id=? AND status='Complete' AND date=?",(u,d)).fetchone()[0] or 0; done=con.execute("SELECT COUNT(*) FROM quests WHERE user_id=? AND status='Complete' AND date=?",(u,d)).fetchone()[0]; total=con.execute("SELECT COUNT(*) FROM quests WHERE user_id=? AND date=?",(u,d)).fetchone()[0]; rows.append({'date':d,'xp':xp,'done':done,'total':total})
    return self.send(200,{'days':rows,'totals':{'study':con.execute('SELECT COALESCE(SUM(minutes),0) FROM study_sessions WHERE user_id=? AND date>=?',(u,start)).fetchone()[0],'fitness':con.execute('SELECT COALESCE(SUM(duration),0) FROM fitness_logs WHERE user_id=? AND date>=?',(u,start)).fetchone()[0],'quranPages':con.execute('SELECT COALESCE(SUM(pages),0) FROM quran_logs WHERE user_id=? AND date>=?',(u,start)).fetchone()[0],'quests':con.execute("SELECT COUNT(*) FROM quests WHERE user_id=? AND status='Complete' AND date>=?",(u,start)).fetchone()[0]}})
   if parts[0]=='prayer' and len(parts)==2: return self.send(200,dict(con.execute('SELECT * FROM prayers WHERE user_id=? AND date=?',(u,parts[1])).fetchone() or {'date':parts[1],'fajr':0,'dhuhr':0,'asr':0,'maghrib':0,'isha':0}))
   if parts[0]=='day' and len(parts)==2: ensure_day(u,parts[1]); return self.send(200,dict(con.execute('SELECT * FROM daily_logs WHERE user_id=? AND date=?',(u,parts[1])).fetchone()))
   t=parts[0]
   if t in resources: 
    rows=[dict(x) for x in con.execute(f'SELECT * FROM {t} WHERE user_id=? ORDER BY created_at DESC',(u,)).fetchall()]
    return self.send(200,rows)
   return self.send(404,{'error':'Unknown resource'})
  fp=os.path.join(ROOT,'public',path.lstrip('/') or 'index.html');
  if os.path.isfile(fp): self.send(200,open(fp,'rb').read(),mimetypes.guess_type(fp)[0] or 'application/octet-stream')
  else:self.send(200,open(os.path.join(ROOT,'public','index.html'),'rb').read(),'text/html')
 def do_POST(self):
  path=urlparse(self.path).path; b=self.body()
  if path=='/api/auth/signup':
   if not b.get('email') or not b.get('password') or not b.get('hunterName') or len(b['password'])<8:return self.send(400,{'error':'اسم المستخدم والبريد وكلمة مرور 8 أحرف على الأقل مطلوبة.'})
   try:
    u=uid(); con.execute('INSERT INTO users VALUES(?,?,?,?)',(u,b['email'].lower(),hashpw(b['password']),now())); con.execute('INSERT INTO profiles VALUES(?,?,?,?,?,?,?,?,?,?,?)',(uid(),u,b['hunterName'],'','dark','UTC','DZD','','',1,now()));
    for n in ['Knowledge','Fitness','Skills','Language','Discipline','Spirit']: con.execute('INSERT INTO stats VALUES(?,?,?,?,?,?)',(uid(),u,n,'',0,now()))
    con.commit(); return self.send(200,{'token':token(u),'profile':profile(u)})
   except sqlite3.IntegrityError:return self.send(400,{'error':'الحساب موجود مسبقًا.'})
  if path=='/api/auth/login':
   r=con.execute('SELECT * FROM users WHERE email=?',(b.get('email','').lower(),)).fetchone();
   if not r or not checkpw(b.get('password',''),r['password_hash']):return self.send(401,{'error':'بيانات الدخول غير صحيحة.'})
   return self.send(200,{'token':token(r['id']),'profile':profile(r['id'])})
  u=self.uid();
  if not u:return self.send(401,{'error':'Unauthorized'})
  if path.startswith('/api/quests/') and path.endswith('/complete'):
   qid=path.split('/')[-2]; q=con.execute('SELECT * FROM quests WHERE id=? AND user_id=?',(qid,u)).fetchone();
   if not q:return self.send(404,{'error':'Quest not found'})
   if q['status']=='Complete':return self.send(200,{'quest':dict(q),'profile':profile(u)})
   xp=max(0,int(q['xp_reward'] or 0)); cr=max(0,int(q['credit_reward'] or 0)); con.execute("UPDATE quests SET status='Complete',xp_earned=?,credits_earned=?,updated_at=? WHERE id=?",(xp,cr,now(),qid));
   if cr: con.execute('INSERT INTO credit_transactions VALUES(?,?,?,?,?,?,?,?,?)',(uid(),u,'Quest: '+q['title'],today(),'Quest Reward',cr,qid,None,now()))
   if q['stat_id']:con.execute('UPDATE stats SET stat_xp=stat_xp+? WHERE id=?',(xp,q['stat_id']))
   if q['skill_id']:con.execute('UPDATE skills SET skill_xp=skill_xp+? WHERE id=?',(xp,q['skill_id']))
   if q['mission_id']:
    total=con.execute('SELECT COUNT(*) FROM quests WHERE user_id=? AND mission_id=?',(u,q['mission_id'])).fetchone()[0]; done=con.execute("SELECT COUNT(*) FROM quests WHERE user_id=? AND mission_id=? AND status='Complete'",(u,q['mission_id'])).fetchone()[0]; prog=round(done/total*100) if total else 0; con.execute('UPDATE missions SET progress=?,status=? WHERE id=?', (prog,'Complete' if prog==100 else 'Active',q['mission_id']))
   con.commit(); return self.send(200,{'quest':dict(con.execute('SELECT * FROM quests WHERE id=?',(qid,)).fetchone()),'profile':profile(u),'levelUp':profile(u)['level']})
  if path.startswith('/api/rewards/') and path.endswith('/purchase'):
   rid=path.split('/')[-2]; r=con.execute('SELECT * FROM rewards WHERE id=? AND user_id=?',(rid,u)).fetchone(); bal=profile(u)['credits'];
   if not r:return self.send(404,{'error':'Reward not found'})
   if bal<r['cost']:return self.send(400,{'error':'الرصيد غير كافٍ.'})
   con.execute('INSERT INTO credit_transactions VALUES(?,?,?,?,?,?,?,?,?)',(uid(),u,'Reward: '+r['reward'],today(),'Reward Purchase',-abs(r['cost']),None,rid,now())); con.commit(); return self.send(200,{'profile':profile(u)})
  if path=='/api/day/close':
   d=b.get('date',today()); ensure_day(u,d); con.execute('UPDATE daily_logs SET closed=1 WHERE user_id=? AND date=?',(u,d)); con.commit(); return self.send(200,{'ok':True,'nextDate':(datetime.date.fromisoformat(d)+datetime.timedelta(days=1)).isoformat()})
  if path.startswith('/api/'):
   t=path[5:].strip('/').split('/')[0]
   if t in resources:
    fs=resources[t]; cols=['id','user_id']+fs+['created_at']; vals=[]
    for f in fs:
     v=b.get(f)
     if v is None:v=0 if f in nums else ''
     vals.append(v)
    con.execute(f"INSERT INTO {t}({','.join(cols)}) VALUES({','.join('?' for _ in cols)})",[uid(),u,*vals,now()]); con.commit(); return self.send(200,dict(con.execute(f'SELECT * FROM {t} WHERE id=?',(con.execute('SELECT id FROM '+t+' WHERE user_id=? ORDER BY created_at DESC LIMIT 1',(u,)).fetchone()[0],)).fetchone()))
  return self.send(404,{'error':'Unknown endpoint'})
 def do_PUT(self):
  path=urlparse(self.path).path;b=self.body();u=self.uid();
  if not u:return self.send(401,{'error':'Unauthorized'})
  if path.startswith('/api/prayer/'):
   d=path.split('/')[-1]; vals=[1 if b.get(k) else 0 for k in ['fajr','dhuhr','asr','maghrib','isha']]; con.execute('INSERT INTO prayers VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(user_id,date) DO UPDATE SET fajr=excluded.fajr,dhuhr=excluded.dhuhr,asr=excluded.asr,maghrib=excluded.maghrib,isha=excluded.isha',(uid(),u,d,*vals)); con.commit(); return self.send(200,dict(con.execute('SELECT * FROM prayers WHERE user_id=? AND date=?',(u,d)).fetchone()))
  if path.startswith('/api/day/'):
   d=path.split('/')[-1];ensure_day(u,d); allowed=['top1','top2','top3','energy','focus','notes']; vals=[b.get(k,'') for k in allowed]; con.execute('UPDATE daily_logs SET '+','.join(k+'=?' for k in allowed)+' WHERE user_id=? AND date=?',vals+[u,d]);con.commit();return self.send(200,dict(con.execute('SELECT * FROM daily_logs WHERE user_id=? AND date=?',(u,d)).fetchone()))
  return self.send(404,{'error':'Unknown endpoint'})
 def do_PATCH(self):
  path=urlparse(self.path).path;b=self.body();u=self.uid();
  if not u:return self.send(401,{'error':'Unauthorized'})
  if path=='/api/profile':
   allowed=[k for k in ['hunter_name','avatar','theme','timezone','currency','academic_year','bac_date','notifications'] if k in b]
   if allowed:con.execute('UPDATE profiles SET '+','.join(k+'=?' for k in allowed)+' WHERE user_id=?',[b[k] for k in allowed]+[u]);con.commit()
   return self.send(200,profile(u))
  parts=path[5:].strip('/').split('/');t=parts[0] if parts else ''
  if t in resources and len(parts)>1:
   row=con.execute(f'SELECT * FROM {t} WHERE id=? AND user_id=?',(parts[1],u)).fetchone();
   if not row:return self.send(404,{'error':'Not found'})
   allowed=[k for k in b if k in row.keys() and k not in ('id','user_id','created_at')]
   if allowed:con.execute(f'UPDATE {t} SET '+','.join(k+'=?' for k in allowed)+' WHERE id=? AND user_id=?',[b[k] for k in allowed]+[parts[1],u]);con.commit()
   return self.send(200,dict(con.execute(f'SELECT * FROM {t} WHERE id=?',(parts[1],)).fetchone()))
  return self.send(404,{'error':'Unknown endpoint'})
 def do_DELETE(self):
  path=urlparse(self.path).path;u=self.uid();
  if not u:return self.send(401,{'error':'Unauthorized'})
  parts=path[5:].strip('/').split('/');t=parts[0] if parts else ''
  if t in resources and len(parts)>1:con.execute(f'DELETE FROM {t} WHERE id=? AND user_id=?',(parts[1],u));con.commit();return self.send(200,{'ok':True})
  return self.send(404,{'error':'Unknown endpoint'})
print(f'⚡ THE SYSTEM running on http://localhost:{PORT}')
ThreadingHTTPServer(('0.0.0.0',PORT),H).serve_forever()
