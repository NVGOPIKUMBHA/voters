from flask import Flask, render_template, session, redirect, url_for, request, flash, abort, jsonify, send_from_directory, blueprints
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import pandas as pd
from functools import wraps
from werkzeug.utils import secure_filename
from .utils import get_summary
from .ocr.extract_pdf import extract_pdf
import os
import random

app = Flask(__name__)

#---------Setting configurations of the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a powerful key for security'

key = app.config['SECRET_KEY']

UPLOAD_PATH = 'app/static/pdfs/'

#---------Declaring the ORM
db = SQLAlchemy(app)

#---------These are the main admin credentials
main = {'username': 'harrydev', 'password':'admin123'}

#---------Importing models from models file
from .models import *

#---------Creating tables in database according to the models file
#with app.app_context():
#    db.create_all()

#---------Security of database view
class SecureView(ModelView):
    page_size = 3000
    def is_accessible(self):
        if 'main_admin' in session:
            return True
        else:
            abort

#---------Creating Admin view for the whole database
admin = Admin(app=app)
admin.add_view(SecureView(Voters, db.session))
admin.add_view(SecureView(Constituencies, db.session))
admin.add_view(SecureView(Religions, db.session))
admin.add_view(SecureView(Communities, db.session))
admin.add_view(SecureView(Parties, db.session))
admin.add_view(SecureView(PollingStations, db.session))
admin.add_view(SecureView(Mandals, db.session))
admin.add_view(SecureView(Users, db.session))
admin.add_view(SecureView(AssemblyAdmin, db.session))
admin.add_view(SecureView(ConstituencyAdmin, db.session))
admin.add_view(SecureView(StateAdmin, db.session))

#---------Admin Blueprints
from .admin_views import assembly, user, constituency, state

app.register_blueprint(user.user, url_prefix="/")
app.register_blueprint(assembly.assembly, url_prefix="/assembly")
app.register_blueprint(constituency.constituency, url_prefix="/constituency")
app.register_blueprint(state.state, url_prefix="/state")


# Twilio API
#------------------------------

from twilio.rest import Client
from . import twilio_config as tc
client = Client(tc.KEY, tc.SECRET)

#----------Wraps for security

def is_admin_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'main_admin' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('home'))
    return wrap

#---------Declaring URL endpoints (or Routes)

@app.route('/')
def home():
    st = PollingStations.query.all()
    for i in st:
        db.session.delete(i)
    '''
    a = PollingStations.query.all()
    for i in a:
        db.session.delete(i)
        db.session.commit()
    '''
    if 'state_admin' in session:
        return redirect(url_for('state.home'))
    
    if 'constituency_admin' in session:
        return redirect(url_for('constituency.home'))
    
    if 'assembly_admin' in session:
        return redirect(url_for('assembly.home'))
    
    if 'user' in session:
        return redirect(url_for('user.home'))
    return render_template('home.html')

@app.route('/otp', methods=['GET','POST'])
def otp():
    if request.method=="POST":
        otp_ = request.form.get('otp')
        role = request.form.get('role')
        id = request.form.get('id')
        if role=='user':
            u = Users.query.filter_by(id=int(id)).first()
            if u.otp==otp_:
                session['user'] = u.id
                u.active = True
                u.otp = ''
                db.session.commit()
                return redirect(url_for('user.home'))
        if role=='assembly':
            u = AssemblyAdmin.query.filter_by(id=int(id)).first()
            if u.otp==otp_:
                session['assembly_admin'] = u.id
                u.active = True
                u.otp = ''
                db.session.commit()
                return redirect(url_for('assembly.home'))
        if role=='constituency':
            u = ConstituencyAdmin.query.filter_by(id=int(id)).first()
            if u.otp==otp_:
                session['constituency_admin'] = u.id
                u.active = True
                u.otp = ''
                db.session.commit()
                return redirect(url_for('constituency.home'))
        if role=='state':
            u = StateAdmin.query.filter_by(id=int(id)).first()
            if u.otp==otp_:
                session['state_admin'] = u.id
                u.active = True
                u.otp = ''
                db.session.commit()
                return redirect(url_for('state.home'))
    role = request.args.get('role')
    id_ = request.args.get('id')
    if role and id_:
        return render_template('otp.html', role=role, id=id_)
    return redirect(url_for('home'))
 
#==============================================================
#              API endpoints
#==============================================================

@app.route('/get-subcastes', methods=["POST"])
def get_subcastes():
    comm = request.form.get('community').lower()
    castes = Communities.query.filter_by(name=comm).first()
    try:
        _castes = [i.strip() for i in castes.sub_castes.split(',')]
    except:
        _castes = []
    return jsonify({'subcastes':_castes})

@app.route('/get-communities', methods=["POST"])
def get_communities():
    state = Users.query.filter_by(id=session['user']).first().state
    try:
        coms = Communities.query.filter_by(state=state).all()
        coms = [i.name for i in coms]
    except:
        coms = []
    return jsonify({'communities':coms})

@app.route('/get-assemblies', methods=['POST'])
def get_assemblies():
    con = request.form.get('constituency')
    res = Constituencies.query.filter_by(name=con).first()
    result = res.assemblies.split(',')
    return jsonify({'result': result})

@app.route('/get-stations', methods=['POST'])
def get_stations():
    assem = request.form.get('assembly')
    if assem:
        assem=assem.lower()
        res = PollingStations.query.filter_by(assembly=assem).all()
        result = [i.number+'-'+i.name for i in res]
    else:
        mandal = request.form.get('mandal')
        res = PollingStations.query.filter_by(mandal=mandal).all()
        result = [i.number+'-'+i.name for i in res]
    return jsonify({'result': result})
 
@app.route('/get-mandals', methods=['POST'])
def get_mandals():
    assem = request.form.get('assembly').lower()
    try:
        vs =Mandals.query.filter_by(assembly=assem).first().mandals
        result = [i.strip() for i in vs.split(',')]
    except:
        result = []
    return jsonify({'result': result})

@app.route('/get-ps', methods=['POST'])
def get_ps():
    if request.method== "POST":
        mandal = request.form.get('mandal').lower()
        if mandal:
            mandal = mandal.lower()
        sts = PollingStations.query.filter_by(mandal=mandal).all()
        res = [i.number+'-'+i.name for i in sts]
            
        return jsonify({'result':res})

@app.route('/get-ps-reports', methods=['POST'])
def get_ps_reports():
    if request.method== "POST":
        mandal = request.form.get('mandal').lower()
        assembly = request.form.get('assembly').lower()
        if mandal:
            mandal = mandal.lower()
        voters = Voters.query.filter_by(mandal=mandal).all()
        ps = [int(i.polling_number) for i in voters]
        ps = list(set(ps))
        return jsonify({'result':ps})

@app.route('/get-ps-reports1', methods=['POST'])
def get_ps_reports1():
    if request.method== "POST":
        mandal = request.form.get('mandal').lower()
        assembly = request.form.get('assembly').lower()
        if mandal:
            mandal = mandal.lower()
        voters = Voters.query.filter_by(mandal=mandal).all()
        ps = [int(i.polling_number) for i in voters]
        ps = list(set(ps))
        final_ps = []
        ps_ = PollingStations.query.filter_by(assembly=assembly).all()
        for i in ps_:
            if int(i.number) in ps:
                final_ps.append(i.number+'-'+i.name)
                ps.remove(int(i.number))
        return jsonify({'result':final_ps})

@app.route('/get-pn', methods=["POST"])
def get_pn():
    c = request.form.get('constituency')
    a = request.form.get('assembly')
    print(c,a)
    sts = PollingStations.query.filter_by(constituency=c,assembly=a).all()
    
    stations = [i.number+"-"+i.name for i in sts]
    
    return jsonify({'pn':stations})

@app.route('/get-habitations-leaders', methods=['POST'])
def get_habitations_leaders():
    const = request.form.get('constituency')
    assem = request.form.get('assembly')
    ps = request.form.get('ps')
    
    if const != '' and const is not None:
        vs = Voters.query.filter_by(constituency=const, assembly=assem, polling_number=ps).all()
        hs = [i.influential_leader for i in vs]
        hs1 = [i.habitation for i in vs]
        result = list(set(hs))
        res2=list(set(hs1))
    else:
        vs = Voters.query.filter_by(assembly=assem, poolin_station=ps).all()
        hs = [i.influential_leader for i in vs]
        hs1 = [i.habitation for i in vs]
        result = list(set(hs))
        res2=list(set(hs1))
    
    return jsonify({'result':res2, 'leaders':result})

@app.route('/reports',methods=['GET','POST'])
@is_admin_in
def reports():
    if request.method == "POST":
    
        age = request.form.get('age')
        gender = request.form.get('gender')
        community = request.form.get('community')
        sub_caste = request.form.get('sub_caste')
        religion = request.form.get('religion')
        qualification = request.form.get('qualification')
        profession = request.form.get('profession')
        res_type = request.form.get('res_type')
        party_affiliation = request.form.get('party_affiliation')
        beneficiary = request.form.get('beneficiary')
        h_type = request.form.get('h_type')
        f_size = request.form.get('f_size')

        result = Voters.query.filter_by().all()
        result = [i for i in result if i.modified_by is not None]

        constituency = request.form.get('constituency')
        if constituency != 'all':
            result = [i for i in result if i.constituency==constituency]
            assembly = request.form.get('assembly')
            if assembly != 'all':
                result = [i for i in result if i.assembly==assembly]
                mandal = request.form.get('mandal').lower()
                if mandal != 'all':
                    result = [i for i in result if i.mandal==mandal]
                    poll_no = request.form.get('poll_num')
                    p = poll_no.split('-')[0].strip()
                    if poll_no != 'all':
                        result = [i for i in result if int(i.polling_number)==int(p)]
        
        if h_type != 'all':
            result = [i for i in result if i.house_type == h_type]
        if age != 'all':
            ages = [int(i) for i in age.split('-')]
            result = [i for i in result if int(i.age)>=int(ages[0]) and int(i.age)<=int(ages[1])]
        if gender != 'all':
            result = [i for i in result if i.gender==gender]
        if community != 'all':
            result = [i for i in result if i.community==community]
            if sub_caste != 'all':
                result = [i for i in result if i.sub_caste==sub_caste]
        if religion != 'all':
            result = [i for i in result if i.religion==religion]
        if qualification != 'all':
            result = [i for i in result if i.qualification==qualification]
        if profession != 'all':
            if profession == 'business' or profession == 'self-employed':
                business_type = request.form.get('business_type')
                if business_type != 'all':
                    result = [i for i in result if i.business_type==business_type]
        if beneficiary != 'all':
            if beneficiary != 'asara':
                result = [i for i in result if i.beneficiaries==beneficiary]
            else:
                asara = request.form.get('asara')
                result = [i for i in result if i.beneficiaries.split('-')[1].strip()==asara]
                    
        if res_type != 'all':
            result = [i for i in result if i.residence_type==res_type]
        if party_affiliation != 'all':
            result = [i for i in result if i.party_affiliation==party_affiliation]
        
        gen = request.form.get('generate')
        if gen == 'download':
            report_dict = {
                'constituency' : [],
                'assembly' : [],
                'mandal' : [],
                'polling_number' : [],
                'town' : [],
                'serial_no' : [],
                'epic_no' : [],
                'habitation' : [],
                'house_no' : [],
                'family_no' : [],
                'name' : [],
                'guardian_name' : [],
                'relation' : [],
                'department' : [],
                'dob' : [],
                'age' : [],
                'gender' : [],
                'religion' : [],
                'community' : [],
                'sub_caste' : [],
                'qualification' : [],
                'profession' : [],
                'company' : [],
                'working_place' : [],
                'business_type' : [],
                'is_beneficiary' : [],
                'beneficiaries' : [],
                'email' : [],
                'contact_no' : [],
                'party_affiliation' : [],
                'residence_type' : [],
                'residence' : []
            }
            for i in result:
                report_dict['constituency'].append(i.constituency)
                report_dict['assembly'].append(i.assembly)
                report_dict['age'].append(i.age)
                report_dict['dob'].append(i.dob)
                report_dict['beneficiaries'].append(i.beneficiaries)
                report_dict['business_type'].append(i.business_type)
                report_dict['community'].append(i.community)
                report_dict['company'].append(i.company)
                report_dict['contact_no'].append(i.company)
                report_dict['department'].append(i.department)
                report_dict['email'].append(i.email)
                report_dict['epic_no'].append(i.epic_no)
                report_dict['family_no'].append(i.family_no)
                report_dict['gender'].append(i.gender)
                report_dict['guardian_name'].append(i.guardian_name)
                report_dict['habitation'].append(i.habitation)
                report_dict['house_no'].append(i.house_no)
                report_dict['is_beneficiary'].append(i.is_beneficiary)
                report_dict['mandal'].append(i.mandal)
                report_dict['name'].append(i.name)
                report_dict['party_affiliation'].append(i.party_affiliation)
                report_dict['polling_number'].append(i.polling_number)
                report_dict['profession'].append(i.profession)
                report_dict['qualification'].append(i.qualification)
                report_dict['relation'].append(i.relation)
                report_dict['religion'].append(i.relation)
                report_dict['residence'].append(i.residence)
                report_dict['residence_type'].append(i.residence_type)
                report_dict['serial_no'].append(i.serial_no)
                report_dict['sub_caste'].append(i.sub_caste)
                report_dict['town'].append(i.town)
                report_dict['working_place'].append(i.working_place)
            df = pd.DataFrame(report_dict)
            df.to_excel('app/static/results/result.xlsx')
            return send_from_directory(directory='static',path='results/result.xlsx')
        
        summary = get_summary(result=result, size=f_size)

        return render_template('admin/report_result.html', summary=summary, result=result)

    constituencies = Constituencies.query.filter_by().all()
    constituencies = [i.name for i in constituencies]
    religions_ = Religions.query.filter_by().all()
    religions = [i.name for i in religions_]
    parties = Parties.query.all()
    parties = [i.name for i in parties]

    return render_template('state/reports.html', constituencies = constituencies,religions=religions,parties=parties, admin=True) #, assemblies=assemblies,polling_nos=polling_nos,mandals=mandals,religions=religions,parties=parties)


#==============================================================
#              Main Admin Only
#==============================================================

@app.route('/main/login', methods=['GET','POST'])
def main_login():
    if 'main_admin' in session:
        return render_template('admin/panel.html', main=True)
    if request.method == "POST":
        us = request.form.get('username')
        pswd = request.form.get('pswrd')
        
        if us == main['username'] and pswd==main['password']:
            session['main_admin'] = True
            return render_template('admin/panel.html', main=True)
    return render_template('admin/login.html')

@app.route('/main/logout')
@is_admin_in
def main_logout():
    if 'main_admin' in session:
        session.pop('main_admin', None)
    return redirect(url_for('home'))

@app.route('/upload-pdf', methods=['GET','POST'])
@is_admin_in
def upload_pdf():
    file = request.files('pdf')
    if file.filename != '':
        try:
            f_name = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_PATH, f_name))
        except:
            k = random.randint(100,999)
            f_name= secure_filename(file.filename)+f"{k}"
            file.save(os.path.join(UPLOAD_PATH, f_name))
        result_path = extract_pdf(filename=f_name)
        return send_from_directory(result_path)

    return render_template('admin/upload_pdf.html')

@app.route('/upload-ps',methods = ['GET','POST'])
@is_admin_in
def upload_ps():
    if request.method == "POST":
        exl = request.files['ps_excel']
        party = request.form.get('party').lower().strip()
        #constituency = request.form.get('constituency').lower().strip()
        state = request.form.get('state').lower().strip()
        records = []
        df = pd.read_excel(exl)
        for i in df.index:
            n = (df['PS NAME'][i]).lower().strip()
            try:
                num = int(df['PS NO'][i])
            except:
                num = 1499
            assem =  (df['AC NO & NAME'][i]).lower().strip()
            l = (df['PS LOCATION'][i]).lower().strip()
            const = (df['PC NAME'][i]).lower().strip()
            rec = PollingStations(
                name=n,
                number = num,
                assembly = assem.replace(" ",""),
                location = l,
                party = party,
                constituency= const.replace(" ",""),
                state = state,
                completed_serial_nos = "",
                code = num,
            )
            records.append(rec)
        db.session.add_all(records)
        db.session.commit()
        flash("Success", 'success')
        return redirect(url_for('upload_ps'))
    return render_template('admin/upload_ps.html')

@app.route('/upload-mandals', methods=['GET','POST'])
@is_admin_in
def upload_mandals():
    if request.method == "POST":
        exl = request.files['mandals_excel']
        party = request.form.get('party').lower().strip()
        state = request.form.get('state').lower().strip()
        records = []
        df = pd.read_excel(exl)
        print(df.columns)
        print(df)
        for i in df.index: 
            pc = (df['PC'][i]).lower().strip()
            ac = (df['AC'][i]).lower().strip()
            mandals=(df['MANDALS'][i]).lower().strip()
            rec = Mandals(
                constituency=pc,
                assembly = ac,
                mandals=mandals,
                party = party,
                state = state
            )
            records.append(rec)
        db.session.add_all(records)
        db.session.commit()
        flash("Success", 'success')
        return redirect(url_for('upload_mandals'))
    return render_template('admin/upload_mandals.html')

@app.route('/broadcast',methods=['POST'])
@is_admin_in
def broadcast():
    if 'state_admin' in session or 'main_admin' in session:

        nums = request.form.getlist('numbers[]')
        message = request.form.get('message')

        if nums is None:
            return jsonify({'error':'No numbers found!'})
        nums = list(set(nums))

        total_contacts = len(nums)

        unsent = []
        for i in nums:
            num = i.strip()
            try:
                client.messages.create(
                    body=message,
                    from_= tc.NUMBER,
                    to=num
                )
            except:
                unsent.append(num)
        if unsent != [] or None:
            return jsonify({'sent_count':total_contacts-len(unsent), 'unsent_numbers':unsent})
        return jsonify({'sent_count':total_contacts})
    return jsonify({'error':"You are not authorized!"})

@app.route('/voice-broadcast',methods=['POST'])
@is_admin_in
def voice_broadcast():
    if 'state_admin' in session or 'main_admin' in session:

        nums = request.form.getlist('numbers[]')
        url = request.form.get('message').strip()
        
        if url == '' or url is None:
            return jsonify({'error':'No message found!'})

        if nums is None:
            return jsonify({'error':'No numbers found!'})
        nums = list(set(nums))

        total_contacts = len(nums)

        unsent = []
        for i in nums:
            num = i.strip()
            try:
                client.calls.create(
                    url=url,
                    from_= tc.NUMBER,
                    to=num
                )
            except:
                unsent.append(num)
        if unsent != [] or None:
            return jsonify({'sent_count':total_contacts-len(unsent), 'unsent_numbers':unsent})
        return jsonify({'sent_count':total_contacts})
    return jsonify({'error':"You are not authorized!"})

@app.route('/upload-voters', methods=['GET','POST'])
@is_admin_in
def upload_voters():
    if request.method == "POST":
        f = request.files['voters_excel']
        state = request.form.get('state').lower().strip()
        records = []
        df = pd.read_excel(f)
        for i in df.index: 
            
            g_ = (df['Gender'][i]).lower().strip()
            if g_=="m":
                g = "male"
            elif g_ == "f":
                g = "female"
            else:
                g="other"
            
            r_ = (df['Relation (F/H)'][i]).lower().strip()
            if r_ == 'f':
                r = "father"
            else:
                r = "husband"
                
            rec = Voters(
                name = str((df['Voter Name'][i])).lower().strip(),
                serial_no = str((df['Serial No'][i])).lower().strip(),
                constituency = (df['PC Name'][i]).lower().strip(),
                assembly = (df['AC NO & Name'][i]).lower().strip(),
                polling_number = str((df['PS NO'][i])).lower().strip(),
                house_no = str((df['House No'][i])).lower().strip(),
                gender = g,
                guardian_name = str((df['Father/Husband Name'][i])).lower().strip(),
                relation = r,
                age = str((df['Age'][i])).lower().strip(),
                epic_no = (df['EPIC No'][i]).lower().strip(),
                state = state
            )
            records.append(rec)
        db.session.add_all(records)
        db.session.commit()
        flash("Success", 'success')
        return redirect(url_for('upload_voters'))
    
    return render_template('/admin/upload_voters.html')

#==============================================================
#              Mobile Application API Endpoints
#==============================================================
