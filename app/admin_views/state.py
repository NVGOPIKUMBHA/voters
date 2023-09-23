from flask import Blueprint, render_template, session, redirect, url_for, flash, request, send_from_directory, jsonify
from functools import wraps
import pandas as pd
from ..utils import get_summary

from twilio.rest import Client
import math
import random
from .. import twilio_config as tc
client = Client(tc.KEY, tc.SECRET)


from .. import db
from ..models import *

state = Blueprint('state', __name__)

def is_state_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'state_admin' in session or 'main_admin' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('home'))
    return wrap

@state.route('/panel', methods=['GET','POST'])
def home():
    return render_template('state/panel.html', state=True)


@state.route('/login', methods=['GET','POST'])
def login():
    if request.method=="POST":
        un = request.form.get('username')
        ps = request.form.get('pswrd')

        u = StateAdmin.query.filter_by(username=un).first()
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
                return redirect(url_for('otp', role="state",id=u.id))
                '''
                session['state_admin'] = u.id
                u.active = True
                u.otp = ''
                db.session.commit()
                return redirect(url_for('state.home'))
                
        flash('Invalid Credentials', 'error')
    return render_template('state/login.html')

@state.route('/logout')
@is_state_in
def state_logout():
    u = StateAdmin.query.filter_by(id=session['state_admin']).first()
    u.active = False
    db.session.commit()
    session.pop('state_admin',None)
    return redirect(url_for('home'))

@state.route('/reports',methods=['GET','POST'])
@is_state_in
def reports():
    s = StateAdmin.query.filter_by(id=session['state_admin']).first()
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

        result = Voters.query.filter_by(state=s.state).all()
        result = [i for i in result if i.modified_by is not None]

        constituency = request.form.get('constituency')
        if constituency != 'all':
            result = [i for i in result if i.constituency==constituency]
            assembly = request.form.get('assembly')
            if assembly != 'all':
                result = [i for i in result if i.assembly==assembly]
                poll_no = request.form.get('poll_num')
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
                'phone_type':[],
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
                report_dict['phone_type'].append(i.phone_type)
            df = pd.DataFrame(report_dict)
            df.to_excel('app/static/results/result.xlsx')
            return send_from_directory(directory='static',path='results/result.xlsx')
        
        summary = get_summary(result=result, size=f_size)

        return render_template('admin/report_result.html', summary=summary, result=result)

    constituencies = Constituencies.query.filter_by().all()
    constituencies = [i.name for i in constituencies]
    religions_ = Religions.query.filter_by(state=s.state).all()
    religions = [i.name for i in religions_]
    parties = Parties.query.all()
    parties = [i.name for i in parties]

    return render_template('state/reports.html', constituencies = constituencies,religions=religions,parties=parties, admin=True) 

@state.route('/u/enter-religion', methods=["GET","POST"])
@is_state_in
def a_enter_religion():
    if request.method == "POST":
        s = StateAdmin.query.filter_by(id=session['state_admin']).first()
        rel = request.form.get('religion').lower()
        state = s.state
        rels = Religions.query.filter_by(name=rel,state=state).first()
        if rels:
            flash('Religion already exists!', 'warning')
            return redirect(url_for('state.a_enter_religion'))
        relig = Religions(
            name=rel.strip(),
            state=state
        )
        db.session.add(relig)
        db.session.commit()
        flash('Religion added!','success')
        return redirect(url_for('state.a_enter_religion'))
    return render_template('enter-religion.html')

@state.route('/u/enter-community', methods=["GET","POST"])
@is_state_in
def a_enter_community():
    if request.method == "POST":
        s = StateAdmin.query.filter_by(id=session['state_admin']).first()
        state = s.state
        com = request.form.get('community').lower()
        coms = Communities.query.filter_by(state=state,name=com).first()
        if coms:
            flash('Community already exist!','warning')
            return redirect(url_for('state.a_enter_community'))
        
        consti = Communities(
            state=state,
            name=com
        )
        
        db.session.add(consti)
        db.session.commit()
        flash('Community added!','success')
        return redirect(url_for('state.a_enter_community'))
    return render_template('enter-community.html')

'''
@state.route('/u/enter-constituency', methods=["GET","POST"])
@is_state_in
def a_enter_constituency():
    if request.method == "POST":
        s = StateAdmin.query.filter_by(id=session['state_admin']).first()
        const = request.form.get('const').lower()
        state = s.state
        consts = Constituencies.query.filter_by(state=state, name=const).first()
        if consts:
            flash('Constituency already exist!','warning')
            return redirect(url_for('state.a_enter_constituency'))
        
        consti = Constituencies(
            state=state,
            name=const
        )
        
        db.session.add(consti)
        db.session.commit()
        flash('Constituency added!','success')
        return redirect(url_for('state.a_enter_constituency'))
    return render_template('enter-constituency.html')

'''


@state.route('/u/enter-subcaste', methods=["GET","POST"])
@is_state_in
def a_enter_subcaste():
    s = StateAdmin.query.filter_by(id=session['state_admin']).first()
    state = s.state
    if request.method == "POST":
        caste = request.form.get('caste').lower()
        sc = request.form.get('sub_castes').lower()
        sc = sc.replace(" ","")
        scs = Communities.query.filter_by(name=caste,state=state).first()
        if scs:
            if scs.sub_castes is None:
                scs.sub_castes = sc
            else:
                if sc in scs.sub_castes.split(','):
                    flash('Sub caste already exists!','warning')
                    return redirect(url_for('a_enter_subcaste'))
                scs.sub_castes = scs.sub_castes +","+sc
            db.session.commit()
            flash('Subcaste added!','success')
            return redirect(url_for('state.a_enter_subcaste'))
    castes = Communities.query.filter_by(state=state).all()
    castes = [i.name for i in castes]
    return render_template('enter-subcaste.html', castes = castes)

@state.route('/u/enter-parties', methods=["GET","POST"])
@is_state_in
def a_enter_parties():
    if request.method == "POST":
        const = request.form.get('party').lower()
        leader = request.form.get('leader').lower()
        consts = Parties.query.filter_by(leader_name=leader, name=const).first()
        
        a = StateAdmin.query.filter_by(id=session['state_admin']).first()
        if consts:
            flash('Party already exist!','warning')
            return redirect(url_for('state.a_enter_parties'))
        
        consti = Parties(
            leader_name=leader,
            name=const,
            party = a.party,
            state = a.state
        )

        db.session.add(consti)
        db.session.commit()
        flash('Party added!','success')
        return redirect(url_for('state.a_enter_parties'))
    return render_template('enter-parties.html')




'''
@state.route('/assign-constituency', methods=['GET','POST'])
@is_state_in
def assign_constituency():
    a = StateAdmin.query.filter_by(id=session['state_admin']).first()
    if request.method == "POST":
        const = request.form.get('const')
        name = request.form.get('name')
        un = request.form.get('username')
        phone = request.form.get('phone')
        pswd = request.form.get('pswd')
        
        u = AssemblyAdmin.query.filter_by(username=un,party=a.party).first()
        if u:
            flash("Give a different username!", 'error')
        else:
            us = ConstituencyAdmin(
                name = name,
                username=un,
                phone_number = phone,
                constituency = const,
                party=a.party,
                state=a.state,
                password = pswd
            )
            db.session.add(us)
            db.session.commit()
            flash("Constituency added successfully!", 'success') 
    consts = Constituencies.query.filter_by(state=a.state).all()
    consts_ = [i.name for i in consts]
    
    return render_template('state/assign_constituency.html', consts=consts_)
'''