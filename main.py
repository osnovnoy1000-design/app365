import sqlite3, os
from datetime import datetime
from random import sample
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle

BG=(0.031,0.031,0.039,1)
CARD=(0.078,0.078,0.094,1)
CARD2=(0.11,0.11,0.14,1)
ACCENT=(0.169,0.431,0.941,1)
GREEN=(0.196,0.784,0.443,1)
GOLD=(0.851,0.663,0.239,1)
WHITE=(1,1,1,1)
GREY=(0.55,0.55,0.58,1)

TASKS=["20 отжиманий","50 приседаний","30 минут ходьбы без телефона","Прочитать 20 страниц","Встать в 6:00","Час без телефона","10 минут медитации","Позвонить родителям","Убрать стол","План на завтра","30 минут тренировки","2 литра воды","Не есть после 20:00","Домашняя еда весь день","Холодный душ утром","8 часов сна","100 прыжков","Прогулка 40 минут","Без газировки весь день","10 000 шагов за день","Утренняя пробежка 15 минут","1 час без сидячего положения","5 английских слов","30 минут без интернета","Подкаст 30 минут","Написать 5 целей","Разобрать одну ошибку","Записать 3 идеи","Сказать нет соблазну","День без жалоб"]

class DB:
    def __init__(self):
        try:
            path=os.path.join(App.get_running_app().user_data_dir,'a.db')
        except:
            path='a.db'
        self.path=path
        c=sqlite3.connect(path)
        c.execute('CREATE TABLE IF NOT EXISTS cfg (id INTEGER PRIMARY KEY CHECK(id=1), load INTEGER, start_date TEXT, last_day TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS td (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, done INTEGER DEFAULT 0)')
        c.execute('CREATE TABLE IF NOT EXISTS hs (id INTEGER PRIMARY KEY AUTOINCREMENT, day INTEGER, date TEXT)')
        c.commit()
        c.close()
    def _c(self):
        return sqlite3.connect(self.path)
    def set_load(self,n):
        d=datetime.now().strftime('%Y-%m-%d')
        with self._c() as c:
            row=c.execute('SELECT id FROM cfg WHERE id=1').fetchone()
            if row:
                c.execute('UPDATE cfg SET load=?, start_date=COALESCE(start_date, ?) WHERE id=1',(n,d))
            else:
                c.execute('INSERT INTO cfg (id, load, start_date, last_day) VALUES (1, ?, ?, ?)',(n,d,d))
    def get_load(self):
        with self._c() as c:
            r=c.execute('SELECT load FROM cfg WHERE id=1').fetchone()
            return r[0] if r else None
    def get_last_day(self):
        with self._c() as c:
            r=c.execute('SELECT last_day FROM cfg WHERE id=1').fetchone()
            return r[0] if r and r[0] else None
    def set_last_day(self,d):
        with self._c() as c:
            c.execute('UPDATE cfg SET last_day=? WHERE id=1',(d,))
    def get_start_date(self):
        with self._c() as c:
            r=c.execute('SELECT start_date FROM cfg WHERE id=1').fetchone()
            return r[0] if r and r[0] else None
    def day_number(self):
        s=self.get_start_date()
        if not s:
            return 1
        d=datetime.strptime(s,'%Y-%m-%d')
        return min((datetime.now()-d).days+1,365)
    def gen_today(self,n):
        with self._c() as c:
            c.execute('DELETE FROM td')
            n=min(n,len(TASKS))
            for t in sample(TASKS,n):
                c.execute('INSERT INTO td (task, done) VALUES (?, 0)',(t,))
    def get_today(self):
        with self._c() as c:
            return c.execute('SELECT id, task, done FROM td ORDER BY id ASC').fetchall()
    def toggle(self,i):
        with self._c() as c:
            c.execute('UPDATE td SET done=1-done WHERE id=?',(i,))
    def count_done(self):
        with self._c() as c:
            return c.execute('SELECT COUNT(*) FROM td WHERE done=1').fetchone()[0]
    def count_all(self):
        with self._c() as c:
            return c.execute('SELECT COUNT(*) FROM td').fetchone()[0]
    def mark_day(self):
        d=datetime.now().strftime('%Y-%m-%d')
        with self._c() as c:
            c.execute('INSERT INTO hs (day, date) VALUES (?, ?)',(self.day_number(),d))
        self.set_last_day(d)
    def day_done_today(self):
        d=datetime.now().strftime('%Y-%m-%d')
        with self._c() as c:
            return c.execute('SELECT COUNT(*) FROM hs WHERE date=?',(d,)).fetchone()[0]
    def total_days(self):
        with self._c() as c:
            return c.execute('SELECT COUNT(*) FROM hs').fetchone()[0]
    def check_new_day(self):
        today=datetime.now().strftime('%Y-%m-%d')
        last=self.get_last_day()
        if last is None:
            return True
        return today!=last

class SetupScreen(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)
        r=BoxLayout(orientation='vertical',padding=dp(24),spacing=dp(10))
        with r.canvas.before:
            Color(*BG)
            bg=Rectangle(pos=r.pos,size=r.size)
        r.bind(pos=lambda i,v:setattr(bg,'pos',v))
        r.bind(size=lambda i,v:setattr(bg,'size',v))
        r.add_widget(Widget(size_hint_y=None,height=dp(60)))
        r.add_widget(Label(text='НАГРУЗКА',font_size=dp(28),bold=True,color=WHITE,size_hint_y=None,height=dp(50)))
        r.add_widget(Label(text='сколько заданий в день?',font_size=dp(13),color=GREY,size_hint_y=None,height=dp(30)))
        r.add_widget(Widget(size_hint_y=None,height=dp(30)))
        self.num=Label(text='5',font_size=dp(100),bold=True,color=ACCENT,size_hint_y=None,height=dp(130))
        r.add_widget(self.num)
        self.desc=Label(text='Норма',font_size=dp(18),color=WHITE,size_hint_y=None,height=dp(36))
        r.add_widget(self.desc)
        r.add_widget(Widget(size_hint_y=None,height=dp(20)))
        self.s=Slider(min=1,max=10,value=5,step=1)
        sw=BoxLayout(size_hint_y=None,height=dp(60),padding=[dp(30),0,dp(30),0])
        sw.add_widget(self.s)
        r.add_widget(sw)
        self.s.bind(value=self.ch)
        r.add_widget(Widget())
        b=Button(text='ПРОДОЛЖИТЬ',size_hint_y=None,height=dp(64),background_normal='',background_down='',background_color=ACCENT,color=WHITE,bold=True,font_size=dp(16))
        b.bind(on_release=self.go)
        r.add_widget(b)
        self.add_widget(r)
    def ch(self,i,v):
        v=int(v)
        self.num.text=str(v)
        if v==1: self.desc.text='Отдых'
        elif v<=3: self.desc.text='Легко'
        elif v<=5: self.desc.text='Норма'
        elif v<=7: self.desc.text='Серьёзно'
        elif v<=9: self.desc.text='Жёстко'
        else: self.desc.text='Пашем'
    def go(self,*a):
        app=App.get_running_app()
        n=int(self.s.value)
        app.db.set_load(n)
        app.db.gen_today(n)
        app.db.set_last_day(datetime.now().strftime('%Y-%m-%d'))
        self.manager.current='main'

class TaskRow(BoxLayout):
    def __init__(self,iid,task,done,on_toggle,**kw):
        super().__init__(orientation='horizontal',size_hint_y=None,height=dp(62),padding=[dp(16),dp(8),dp(8),dp(8)],spacing=dp(8),**kw)
        self.iid=iid
        self.on_toggle=on_toggle
        with self.canvas.before:
            Color(*(CARD2 if done else CARD))
            self._bg=RoundedRectangle(pos=self.pos,size=self.size,radius=[dp(12)])
        self.bind(pos=self._u,size=self._u)
        lbl=Label(text=task,color=GREY if done else WHITE,font_size=dp(14),halign='left',valign='middle',size_hint=(1,1))
        lbl.bind(size=lambda i,v:setattr(i,'text_size',(v[0],None)))
        self.add_widget(lbl)
        ck=Button(text='V' if done else 'O',size_hint=(None,None),size=(dp(44),dp(44)),background_normal='',background_down='',background_color=GREEN if done else (0,0,0,0),color=WHITE,bold=True,font_size=dp(18))
        ck.bind(on_release=lambda x:self.on_toggle(self.iid))
        self.add_widget(ck)
    def _u(self,*a):
        self._bg.pos=self.pos
        self._bg.size=self.size

class MainScreen(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)
        r=BoxLayout(orientation='vertical')
        with r.canvas.before:
            Color(*BG)
            bg=Rectangle(pos=r.pos,size=r.size)
        r.bind(pos=lambda i,v:setattr(bg,'pos',v))
        r.bind(size=lambda i,v:setattr(bg,'size',v))
        top=BoxLayout(size_hint_y=None,height=dp(50),padding=[dp(16),dp(10),dp(16),dp(0)])
        self.day_lbl=Label(text='ДЕНЬ 1 ИЗ 365',font_size=dp(13),color=GREY,bold=True,halign='left',valign='middle')
        self.day_lbl.bind(size=lambda i,v:setattr(i,'text_size',(v[0],None)))
        top.add_widget(self.day_lbl)
        self.days_btn=Button(text='ДНЕЙ: 0',size_hint=(None,None),size=(dp(80),dp(30)),background_normal='',background_down='',background_color=CARD,color=GOLD,bold=True,font_size=dp(11))
        top.add_widget(self.days_btn)
        r.add_widget(top)
        sc=ScrollView()
        self.list_box=BoxLayout(orientation='vertical',spacing=dp(10),size_hint_y=None,padding=[dp(16),dp(8),dp(16),dp(8)])
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        sc.add_widget(self.list_box)
        r.add_widget(sc)
        self.progress=Label(text='',font_size=dp(20),bold=True,color=ACCENT,size_hint_y=None,height=dp(50))
        r.add_widget(self.progress)
        btns=BoxLayout(orientation='horizontal',size_hint_y=None,height=dp(80),spacing=dp(8),padding=[dp(16),0,dp(16),dp(16)])
        new_btn=Button(text='НОВЫЙ ДЕНЬ',background_normal='',background_down='',background_color=CARD,color=GOLD,bold=True,font_size=dp(12))
        new_btn.bind(on_release=self.new_day)
        self.btn=Button(text='ЗАКРЫТЬ ДЕНЬ',background_normal='',background_down='',background_color=ACCENT,color=WHITE,bold=True,font_size=dp(14))
        self.btn.bind(on_release=self.close_day)
        btns.add_widget(new_btn)
        btns.add_widget(self.btn)
        r.add_widget(btns)
        self.add_widget(r)
    def on_pre_enter(self):
        db=App.get_running_app().db
        if db.get_load() is None:
            self.manager.current='setup'
            return
        if db.check_new_day():
            db.gen_today(db.get_load())
            db.set_last_day(datetime.now().strftime('%Y-%m-%d'))
    def on_enter(self):
        self.refresh()
    def refresh(self):
        db=App.get_running_app().db
        self.day_lbl.text='ДЕНЬ '+str(db.day_number())+' ИЗ 365'
        self.days_btn.text='ДНЕЙ: '+str(db.total_days())
        self.list_box.clear_widgets()
        for iid,task,done in db.get_today():
            self.list_box.add_widget(TaskRow(iid,task,done,self.toggle))
        done_n=db.count_done()
        all_n=db.count_all()
        self.progress.text='ВЫПОЛНЕНО: '+str(done_n)+' / '+str(all_n)
        if db.day_done_today()>0:
            self.btn.text='ДЕНЬ ЗАКРЫТ'
            self.btn.disabled=True
            self.btn.background_color=GREEN
        else:
            self.btn.text='ЗАКРЫТЬ ДЕНЬ'
            self.btn.disabled=False
            self.btn.background_color=ACCENT
    def toggle(self,iid):
        App.get_running_app().db.toggle(iid)
        self.refresh()
    def close_day(self,*a):
        db=App.get_running_app().db
        if db.count_done()<db.count_all():
            return
        db.mark_day()
        self.refresh()
    def new_day(self,*a):
        db=App.get_running_app().db
        n=db.get_load() or 5
        db.gen_today(n)
        db.set_last_day(datetime.now().strftime('%Y-%m-%d'))
        self.refresh()

class App365(App):
    def build(self):
        self.title='365'
        self.db=DB()
        sm=ScreenManager(transition=SlideTransition(duration=0.3))
        sm.add_widget(SetupScreen(name='setup'))
        sm.add_widget(MainScreen(name='main'))
        if self.db.get_load() is None:
            sm.current='setup'
        else:
            sm.current='main'
        return sm

if __name__=='__main__':
    App365().run()
