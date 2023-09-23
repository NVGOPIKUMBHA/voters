from flask import Blueprint, render_template, session, redirect, url_for, flash,request, send_from_directory
from functools import wraps
from ..utils import get_summary, list_to_str
import pandas as pd

'''
from twilio.rest import Client
import math
import random
from .. import twilio_config as tc
client = Client(tc.KEY, tc.SECRET)
'''

from ..models import *
from .. import db

constituency = Blueprint('constituency', __name__)

def is_constituency_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'constituency_admin' in session or 'main_admin' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('home'))
    return wrap

@constituency.route('/panel', methods=['GET','POST'])
def home():
    return render_template('constituency/panel.html', constituency=True)

@constituency.route('/login', methods=['GET','POST'])
def login():
    if 'constituency_admin' in session:
        return redirect(url_for('constituency.home'))
    if request.method=="POST":
        un = request.form.get('username')
        ps = request.form.get('pswrd')

        u = ConstituencyAdmin.query.filter_by(username=un).first()
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
                return redirect(url_for('otp', role="constituency",id=u.id))
                '''
                session['constituency_admin'] = u.id
                u.active = True
                u.otp = ''
                db.session.commit()
                return redirect(url_for('constituency.home'))
            
        flash('Invalid Credentials', 'error')
    return render_template('constituency/login.html')

@constituency.route('/logout')
@is_constituency_in
def state_logout():
    c = ConstituencyAdmin.query.filter_by(id=session["constituency_admin"]).first()
    c.active=False
    db.session.commit()
    session.pop('constituency_admin',None)
    return redirect(url_for('home'))

@constituency.route('/reports',methods=['GET','POST'])
@is_constituency_in
def reports():
    const = ConstituencyAdmin.query.filter_by(id=session['constituency_admin']).first()
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
        
        result = Voters.query.filter_by(constituency=const.constituency, state=const.state).all()
        
        assembly = request.form.get('assembly')
        if assembly != 'all':
            result = [i for i in result if i.assembly==assembly]
            mandal = request.form.get('mandal').lower()
            if mandal != 'all':
                result = [i for i in result if i.mandal==mandal]
                poll_no = request.form.get('poll_num')
                if poll_no != 'all':
                    p = poll_no.split('-')[0].strip()
                    result = [i for i in result if i.polling_number==p]
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

        return render_template('admin/report_result.html', summary=summary, result=result)
    
    state = const.state
    religions_ = Religions.query.filter_by(state=const.state).all()
    religions = [i.name for i in religions_]
    assems = Constituencies.query.filter(Constituencies.name.like(const.constituency+"%")).first().assemblies
    assems = assems.strip().split(',')
    parties = Parties.query.all()
    parties = [i.name for i in parties]

    return render_template('constituency/reports.html',assemblies=assems,religions=religions,parties=parties,state=state, admin=True) 

'''
@constituency.route('/u/enter-mandals', methods=['GET','POST'])
@is_constituency_in
def enter_mandals():
    constituencies = Constituencies.query.all()
    assems = constituencies[0].assemblies.split(',')
    if request.method == "POST":
        mandal = request.form.get('mandal').lower()
        mandal = mandal.strip()
        
        c = ConstituencyAdmin.query.filter_by(id=session['constituency_admin']).first()
        if c.mandals:
            allmandals = c.mandals+","+list_to_str(mandal)
            allmandals = list(set(allmandals.split(",")))
            c.mandals = list_to_str(allmandals)
        else:
            c.mandals=mandal
        db.session.commit()
        flash("Mandal is added successfully!", 'success')
        return redirect(url_for('constituency.enter_mandals'))
    return render_template('enter-mandals.html', constituencies=constituencies, assemblies=assems)


@constituency.route('/u/enter-assembly-constituencies', methods=["GET","POST"])
@is_constituency_in
def a_enter_assembly_constituency():
    a = ConstituencyAdmin.query.filter_by(id=session['constituency_admin']).first()
    if request.method == "POST":
        const = request.form.get('const').lower()
        assemblies = request.form.get('assemblies')
        assemblies = assemblies.lower().replace(" ","")
        if assemblies[-1]==',':
            assemblies = assemblies[-1]
        state = a.state
        consts = Constituencies.query.filter_by(state=state, name=const).first()
        if consts:
            if consts.assemblies is None:
                consts.assemblies = assemblies
            else:
                consts.assemblies = consts.assemblies + ','+assemblies
            db.session.commit()
            flash('Assemblies added!','success')
            return redirect(url_for('constituency.a_enter_assembly_constituency'))
        flash('Parliamentry constituency doesn\'t exist!','error')
        return redirect(url_for('constituency.a_enter_assembly_constituency'))
    state = a.state
    consts = Constituencies.query.filter_by(state=state).all()
    consts = [i.name for i in consts]
    return render_template('enter-assembly-constituency.html', constituencies = consts)


@constituency.route('/assign-assembly', methods=['GET','POST'])
@is_constituency_in
def assign_assembly():
    a = ConstituencyAdmin.query.filter_by(id=session['constituency_admin']).first()
    if request.method == "POST":
        assembly = request.form.get('assembly')
        name = request.form.get('name')
        un = request.form.get('username')
        phone = request.form.get('phone')
        pswd = request.form.get('pswd')
        mandals = request.form.getlist('mandals')
        print(mandals)
        mandals = list_to_str(mandals)
        print(mandals)
        u = AssemblyAdmin.query.filter_by(username=un,party=a.party).first()
        if u:
            flash("Give a different username!", 'error')
        else:
            us = AssemblyAdmin(
                name = name,
                username=un,
                party=a.party,
                phone_number = phone,
                assembly = assembly,
                mandal=mandals,
                constituency=a.constituency,
                state=a.state,
                password = pswd
            )
            db.session.add(us)
            db.session.commit()
            flash("Assembly member added successfully!", 'success')
    asseml = Constituencies.query.filter_by(name=a.constituency).first()
    assemlmb = asseml.assemblies
    assemblies = [i.strip() for i in assemlmb.split(',')]
    mandals = [i.strip() for i in a.mandals.split(',')]
        
    return render_template('constituency/assign_assembly.html', assemblies=assemblies, mandals=mandals)
'''
