from flask import Blueprint, render_template, session, redirect, url_for, request, flash, send_from_directory
from functools import wraps

'''
from twilio.rest import Client
import math
import random
from .. import twilio_config as tc
client = Client(tc.KEY, tc.SECRET)
'''

from ..models import AssemblyAdmin, Voters, Religions, Parties, PollingStations, Users,Mandals
from .. import db
import pandas as pd
from ..utils import get_summary

assembly = Blueprint('assembly', __name__)

def is_assembly_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'assembly_admin' in session or 'main_admin' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('home'))
    return wrap

@assembly.route('/panel', methods=['GET','POST'])
def home():
    return render_template('assembly/panel.html', assembly=True)

@assembly.route('/login', methods=['GET','POST'])
def login():
    if 'assembly_admin' in session:
        return redirect(url_for('assembly.home'))
    if request.method=="POST":
        un = request.form.get('username')
        ps = request.form.get('pswrd')

        u = AssemblyAdmin.query.filter_by(username=un).first()
        if u:
            if u.active is True:
                flash("You are already logged in another device!", 'error')
                return redirect(url_for('home'))
            elif u.password == ps:
                '''
                digits = "0123456789"
                otp_ = ''
                for i in range(6):
                    otp_ = otp_+ digits[math.floor(random.random()*10)]
                u.otp = otp_
                msg = client.messages.create(
                    body=f"Your OTP for login is {otp_}",
                    from_= tc.NUMBER,
                    to= u.phone_number
                )
                return redirect(url_for('otp', role="assembly",id=u.id))
                '''
                session['assembly_admin'] = u.id
                u.active = True
                u.otp = ''
                db.session.commit()
                return redirect(url_for('assembly.home'))
                
        flash('Invalid Credentials', 'error')
    return render_template('assembly/login.html')

@assembly.route('/logout')
@is_assembly_in
def state_logout():
    c = AssemblyAdmin.query.filter_by(id=session["assembly_admin"]).first()
    c.active=False
    db.session.commit()
    session.pop('assembly_admin',None)
    return redirect(url_for('home'))

@assembly.route('/reports',methods=['GET','POST'])
@is_assembly_in
def reports():
    assem = AssemblyAdmin.query.filter_by(id=session['assembly_admin']).first()
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
        habitations = request.form.getlist('habitations')
        leaders = request.form.getlist('leaders')
        h_type = request.form.get('h_type')
        f_size = request.form.get('f_size')

        result = Voters.query.filter_by(assembly=assem.assembly, constituency=assem.constituency).all()
        result = [i for i in result if i.modified_by is not None]
        
        mandal = request.form.get('mandal').lower()
        if mandal != "all":
            result = [i for i in result if i.mandal==mandal]
            poll_no = request.form.getlist('stations')
            if 'all' not in poll_no:
                pn = []
                for i in poll_no:
                    p = i.split('-')[0].strip()
                    res = [i for i in result if i.polling_number==p]
                    pn = pn+res
                result = pn
                if 'all' not in habitations:
                    habs = habitations
                    for i in result:
                        if i.habitation not in habs:
                            result.remove(i)
                if 'all' not in leaders:
                    for i in result:
                        if i.influential_leader not in leaders:
                            result.remove(i)
                            
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
                result = [i for i in result if i.beneficiary==beneficiary]
            else:
                asara = request.form.get('asara')
                result = [i for i in result if i.beneficiary.split('-')[1].strip()==asara]
                    
        if res_type != 'all':
            result = [i for i in result if i.residence_type==res_type]
        if party_affiliation != 'all':
            result = [i for i in result if i.party_affiliation==party_affiliation]
        
        gen = request.form.get('generate')
        if gen == 'download':
            report_dict = {
                'PC' : [],
                'AC' : [],
                'mandal' : [], 
                'PS NO.' : [],
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
                'influencer':[],
                'influencer_party':[],
                'residence_type' : [],
                'residence' : [],
                'house type':[],
                'disability':[],
                'modified_by':[],

                'native_district':[],
                'native_state':[],
                'vehicle_type':[],
            }
            for i in result:
                report_dict['PC'].append(i.constituency)
                report_dict['AC'].append(i.assembly)
                report_dict['dob'].append(i.dob)
                report_dict['age'].append(i.age)
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
                report_dict['PS NO.'].append(i.polling_number)
                report_dict['profession'].append(i.profession)
                report_dict['qualification'].append(i.qualification)
                report_dict['relation'].append(i.relation)
                report_dict['religion'].append(i.relation)
                report_dict['residence'].append(i.residence)
                report_dict['residence_type'].append(i.residence_type)
                report_dict['serial_no'].append(i.serial_no)
                report_dict['influencer'].append(i.influencial_leader)
                report_dict['influencer_party'].append(i.local_leader_party)
                report_dict['sub_caste'].append(i.sub_caste)
                report_dict['town'].append(i.town)
                report_dict['working_place'].append(i.working_place)
                report_dict['house type'].append(i.house_type)
                report_dict['disability'].append(i.special_category)
                report_dict['modified_by'].append(i.modified_by)
                report_dict['native_district'].append(i.native_district)
                report_dict['native_state'].append(i.native_state)
                report_dict['modified_by'].append(i.modified_by)
            df = pd.DataFrame(report_dict)
            df.to_excel('app/static/results/result.xlsx')
            return send_from_directory(directory='static',path='results/result.xlsx')
        
        summary = get_summary(result=result, size=f_size)

        return render_template('assembly/report_result.html', summary=summary, result=result)
    
    try:
        print(assem.assembly)
        vs = Mandals.query.filter_by(assembly=assem.assembly).first()
        result = [i.strip() for i in vs.mandals.split(",")]
        mandals=list(set(result))
    except:
        mandals = []
    religions_ = Religions.query.filter_by(state=assem.state).all()
    religions = [i.name for i in religions_]
    parties = Parties.query.all()
    parties = [i.name for i in parties] 
    assembly = assem.assembly

    return render_template('assembly/reports.html', mandals=mandals, religions=religions, assesmbly=assembly,parties=parties, admin=True)

'''
@assembly.route('/u/enter-station', methods=["GET","POST"])
@is_assembly_in
def a_enter_station():
    a = AssemblyAdmin.query.filter_by(id=session['assembly_admin']).first()
    if request.method == "POST":
        mandal = request.form.get('mandal').lower()
        name = request.form.get('st_name').lower()
        num = request.form.get('st_number').lower()
        code = request.form.get('st_code').lower()
        st = PollingStations.query.filter_by(assembly=a.assembly,state=a.state,number=num).first()
        if st:
            flash('Polling station already exists!','warning')
            return redirect(url_for('assembly.a_enter_station'))
        rec = PollingStations(
            state=a.state,
            name=name,
            number=num,
            mandal = mandal,
            assembly = a.assembly,
            party = a.party,
            constituency = a.constituency,
            code=code
        )
        db.session.add(rec)
        db.session.commit()
        flash('Polling Station added!','success')
        return redirect(url_for('assembly.a_enter_station'))
    mandals = Mandals.query.filter_by(state=a.state, assembly=a.assembly, party=a.party, constituency=a.constituency).first().mandals
    mandals = [i.strip() for i in mandals.split(',')]
    return render_template('enter-stations.html', mandals=mandals)

'''


@assembly.route('/assign-user', methods=['GET','POST'])
@is_assembly_in
def assign_user():
    u = AssemblyAdmin.query.filter_by(id=session["assembly_admin"]).first()
    if request.method == "POST":
        poll = request.form.get('poll')
        name = request.form.get('name')
        un = request.form.get('username')
        phone = request.form.get('phone')
        pswd = request.form.get('pswd')
        poll = poll.split('-')[0].strip()
        
        a = Users.query.filter_by(username=un).first()
        if a:
            flash("Give a different username!", 'error')
        elif len(phone.strip())!=10:
            flash("Mobile number must have 10-digits!",'error')
        else:
            us = Users(
                name = name,
                username=un,
                phone_number = phone,
                assembly = u.assembly,
                state=u.state,
                party=u.party,
                constituency = u.constituency,
                password = pswd,
                mandal="",
                polling_station=poll
            )
            db.session.add(us)
            db.session.commit()
            flash("User added successfully!", 'success')
    print(u.assembly)
    ps = PollingStations.query.filter_by(assembly=u.assembly, party=u.party).all()
    return render_template('assembly/assign_user.html', ps=ps)
