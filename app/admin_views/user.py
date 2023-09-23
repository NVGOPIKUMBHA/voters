from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify, make_response
from functools import wraps
from ..models import Users, PollingStations, Constituencies, Voters, Religions, Communities, Parties, AssemblyAdmin, Mandals
from ..utils import list_to_str
import json
import jwt
from .. import key

'''
from twilio.rest import Client
import math
import random
from .. import twilio_config as tc
client = Client(tc.KEY, tc.SECRET)
'''

from .. import db

user = Blueprint('user', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        if request.method=='POST':
            token = request.get_json()['token']
        else:
            token = request.args.get('token')
        if not token:
            return jsonify({'status':False,'message':"Token is missing!"})
        try:
            data = jwt.decode(token,key=key,algorithms='HS256')
            id_ = data['id']
        except Exception as e:
            print(e)
            return jsonify({'status':False,"message":"Invalid Token!"})
        return f(id_,*args,*kwargs)
    return decorated

def is_user_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('home'))
    return wrap

@user.route('/panel', methods=['GET','POST'])
@is_user_in
def home():
    u = Users.query.filter_by(id=session['user']).first()
    a = AssemblyAdmin.query.filter_by(assembly=u.assembly,party=u.party).first()
    assembly_head = a.name
    return render_template('user_panel.html', user=True, mla=assembly_head, assembly = u.assembly)

@user.route('/login', methods=['GET','POST'])
def login():
    if 'user' in session:
        return redirect(url_for('user.input'))
    if request.method=="POST":
        un = request.form.get('username')
        ps = request.form.get('pswrd')

        u = Users.query.filter_by(username=un).first()
        if u:
            #if u.active is True:
            #    flash("You are already logged in another device!", 'error')
            #    return redirect(url_for('user.home'))
            if u.password == ps:
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
                return redirect(url_for('otp', role="user",id=u.id))
                '''
                session['user'] = u.id
                #u.active = True
                u.otp = ''
                db.session.commit()
                return redirect(url_for('user.home'))

        flash('Invalid Credentials', 'error')
    return render_template('login.html')

@user.route('/logout')
@is_user_in
def user_logout():
    u = Users.query.filter_by(id=session['user']).first()
    u.active = False
    db.session.commit()
    session.pop('user',None)
    return redirect(url_for('home'))

@user.route('/input', methods=['GET','POST'])
@is_user_in
def input():
    u=Users.query.filter_by(id=session['user']).first()
    state = u.state
    if request.method == "POST":
        const = request.form.get('constituency')
        assembly = request.form.get('assembly')
        number = request.form.get('polling_station')
        code = request.form.get('code')
        print(const, assembly, number, code)
        try:
            if const!="" and assembly!="" and number!="" and code!="":
                station = PollingStations.query.filter_by(number=int(number.split('-')[0]),assembly=assembly,code=code,state=state).first()
                print(station)
                if station:
                    if u.assembly == assembly.lower() and (u.polling_station) == (station.number): #+"-"+station.name):
                        poll_name = station.name
                        loc = station.location
                        return redirect(url_for('user.entry',loc=loc, constituency=const,poll_name=poll_name, assembly=assembly, poll_num = station.number))
                    flash('You are not authorized here!','error')
                else:
                    flash('Incorrect Polling station code!','error')
            else:
                flash('Invalid constituency!','error')
        except:
            flash('Invalid details!','error')
    consts = Constituencies.query.filter_by(state=state).all()
    consts_ = [i.name for i in consts]
    assemblies = []
    return render_template('input.html', constituencies=consts_, assemblies=assemblies)

@user.route('/entry',methods=["GET","POST"])
@is_user_in
def entry():
    u = Users.query.filter_by(id=session['user']).first()
    if request.method=="POST":
        mandal = request.form.get('mandal').lower()
        serial_no = request.form.get('serial_no')
        consti = request.form.get('constituency')
        epic_no = request.form.get('epic_no')
        assembly = request.form.get('assembly')
        poll_no = request.form.get('polling_no')
        poll_name = request.form.get('poll_name')
        main_village = request.form.get('main_village')
        habitation = request.form.get('habitation')
        house_no = request.form.get('house_no')
        family_no = request.form.get('family_no')
        voter_name = request.form.get('voter_name')
        father_name = request.form.get('father_name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        relation = request.form.get('relation')
        religion = request.form.get('religion')
        community = request.form.get('community')
        ht = request.form.get('house_type')
        sub_caste = request.form.get('sub_caste')
        qualification = request.form.get('qualification')
        number = request.form.get('contact_no')
        special_cat = request.form.get('special_category')
        email = request.form.get('email')
        party_affiliation = request.form.get('party_affiliation')
        loc_ = request.form.get('location')
        influencer = request.form.get('leader')
        influencer_party = request.form.get('influencer_party')
        vt = request.form.getlist('vehicle')
        dob = request.form.get('dob')
        native_district = request.form.get('native_district')
        native_state = request.form.get('native_state')
        phone_type = request.form.get('phone_type')
        if native_district:
            native_district=native_district.lower().strip()
        else:
            native_district=""
        if native_state:
            native_state=native_state.lower().strip()
        else:
            native_state=""
        
        if 'none' not in vt:
            vt = list_to_str(vt)
        else:
            vt = "none"

        if number is not None:
            if len(number)!=10:
                flash("Enter valid contact number")
                return redirect(url_for('user.entry',loc=loc_, constituency=consti,poll_name=poll_name, assembly = assembly, poll_num=poll_no))
            try:
                k = int(number)
            except:
                flash("Enter valid contact number")
                return redirect(url_for('user.entry',loc=loc_, constituency=consti,poll_name=poll_name, assembly = assembly, poll_num=poll_no))
        else:
            number = ""

        profession = request.form.get('profession')
        if profession =='religious-leader':
            reli = request.form.get('religious_leader')
            profession = reli
        else:
            company = request.form.get('company')
            w_place = request.form.get('working_place')
            dept = request.form.get('department')

        res_type = request.form.get('residence_type')
        if res_type != 'local':
            residence = request.form.get('residence')
        else:
            residence =""
        
        bt = request.form.get('business_type')
        benf = request.form.get('is_beneficiary')
        bens=None

        if benf == "yes":
            lis = request.form.getlist('beneficiary')
            ben=""
            if 'asara' in lis:
                asr = request.form.get('asara')
                lis.remove('asara')
                ben = list_to_str(lis)
                bens = ben + ','+asr.strip()
            else:
                bens = list_to_str(lis)
        else:
            benf = ""
            
        voter = Voters.query.filter_by(epic_no=epic_no).first()
        if voter:
            voter.mandal = mandal
            voter.habitation = habitation
            voter.family_no = u.polling_station.split('-')[0]+'/'+family_no
            voter.town = main_village
            voter.department = dept
            voter.dob = dob
            voter.community = community
            voter.sub_caste = sub_caste
            voter.qualification = qualification
            voter.profession = profession
            voter.company =company
            voter.working_place = w_place
            voter.business_type = bt
            voter.is_beneficairy = benf
            voter.beneficiaries = bens
            voter.email = email
            voter.contact_no = number
            voter.party_affiliation = party_affiliation
            voter.residence_type = res_type
            voter.residence = residence
            voter.modified_by = u.phone_number
            voter.special_category = special_cat
            voter.house_type = ht
            voter.influential_leader = influencer
            voter.local_leader_party = influencer_party
            voter.vehicle_type = vt
            voter.phone_type = phone_type
            
            flash('Voter is updated successfully!', 'success')
            ps = PollingStations.query.filter_by(number=int(poll_no),assembly=u.assembly,party=u.party,state=u.state).first()
            if ps.completed_serial_nos != "":
                ps_ = ps.completed_serial_nos+','+serial_no
            else:
                ps_ = serial_no
            ps.completed_serial_nos = ps_
            db.session.commit()
            
            return redirect(url_for('user.entry',loc=loc_, constituency=consti,poll_name=poll_name, assembly = assembly, poll_num=poll_no))
        
        voter = Voters(
            mandal = mandal,
            serial_no = serial_no,
            epic_no = epic_no,
            constituency = consti,
            assembly=assembly,
            polling_number = poll_no,
            habitation = habitation,
            town = main_village,
            house_no = house_no,
            family_no = u.polling_station.split('-')[0]+'/'+family_no,
            name = voter_name,
            guardian_name = father_name,
            department = dept,
            age = age,
            dob=dob,
            native_district=native_district,
            native_state = native_state,
            gender = gender,
            relation = relation,
            religion = religion,
            community = community,
            sub_caste = sub_caste,
            qualification = qualification,
            profession = profession,
            company = company,
            working_place = w_place,
            business_type = bt,
            is_beneficiary = benf,
            beneficiaries = bens,
            email = email,
            contact_no=number,
            party_affiliation=party_affiliation,
            residence_type = res_type,
            house_type=ht,
            residence = residence,
            state = u.state,
            influential_leader = influencer,
            local_leader_party = influencer_party,
            modified_by = u.phone_number,
            vehicle_type = vt,
            phone_type=phone_type
        )    
        db.session.add(voter)
        ps = PollingStations.query.filter_by(number=int(poll_no),assembly=u.assembly,party=u.party,state=u.state).first()
        if ps.completed_serial_nos != "":
            ps_ = ps.completed_serial_nos+','+serial_no
        else:
            ps_ = serial_no
        ps.completed_serial_nos = ps_
        db.session.commit()
        flash('Voter added succssfully!', 'success')
        return redirect(url_for('user.entry', loc=loc_, constituency=consti,poll_name=poll_name, assembly = assembly, poll_num=poll_no))

    const = request.args.get('constituency')
    poll_no = request.args.get('poll_num')
    assembly = request.args.get('assembly')
    poll_name = request.args.get('poll_name')
    loc = request.args.get('loc')
 
    a = AssemblyAdmin.query.filter_by(assembly=u.assembly, party=u.party).first()
    state = u.state
    mandals = Mandals.query.filter_by(assembly=a.assembly).first().mandals
    mandals = [i.strip() for i in mandals.split(',')]
    religions = Religions.query.filter_by(state=state).all()
    communities = Communities.query.filter_by(state=state).all()
    constituencies = Constituencies.query.filter_by(state=state).all()
    parties = Parties.query.all()
    ps = PollingStations.query.filter_by(number=poll_no,state=u.state,assembly=u.assembly,party=u.party).first()
    if ps.completed_serial_nos:
        ps_serials = [int(i) for i in ps.completed_serial_nos.split(',')]
    else:
        ps_serials=[]
    serials = [i for i in range(1,1500) if i not in ps_serials]
    parties = [i.name for i in parties]

    return render_template('new_entry.html',loc=loc, mandals=mandals, serials=serials, constituency=const, poll_num=poll_no,poll_name=poll_name, assembly=assembly, constituencies= constituencies, religions=religions,communities=communities, parties=parties)

@user.route('/check-serial', methods=['POST'])
def check_serial():
    u = Users.query.filter_by(id=session['user']).first()
    s = request.form.get('s').strip()
    vs = Voters.query.filter_by(serial_no=s,assembly=u.assembly,state=u.state).first()
    if vs:
        da = {
            'name':vs.name,
            'age':vs.age,
            'epic_no':vs.epic_no,
            'house_no':vs.house_no,
            'gender':vs.gender,
            'relation':vs.relation,
            'guardian':vs.guardian_name
        }
        return jsonify({'filled':True, 'data':da})
    else:
        return jsonify({'notfilled':True})


#===========================================================================
#                   Mobile Application API Endpoints
#===========================================================================

@user.route('/m/login', methods=['GET','POST'])
def m_login():
    if request.method=="POST":
        un = request.get_json()['username']
        ps = request.get_json()['password']

        u = Users.query.filter_by(username=un).first()
        if u:
            #if u.active is True:
            #    flash("You are already logged in another device!", 'error')
            #    return jsonify({'status':'not ok', 'error':'You are already logged in another device!'})
            #elif u.password == ps:
            if u.password == ps:
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
                return jsonify({'status':'ok', 'role':'user', id=u.id})
                '''
                u.active = True
                u.otp = ''
                db.session.commit()
                p= PollingStations.query.filter_by(party=u.party,constituency=u.constituency,assembly=u.assembly).first()
                data = {
                    'name': u.name,
                    'polling_station':p.name,
                    'constituency':u.constituency,
                    'assembly':u.assembly,
                    'party':u.party,
                    'location': p.location,
                    'poll_no':p.number
                }

                token = jwt.encode({'id':u.id, 'p_name':p.name}, key=key, algorithm='HS256')
                
                return jsonify({'status':'ok', 'user':data, 'token':token})

        return jsonify({'status':'not ok','error':'Invalid Credentials!'})
    
    return jsonify({'status':'ok'})

@user.route('/m/logout', methods=["POST"])
@token_required
def m_user_logout(id_):
    try:
        u = Users.query.filter_by(id=int(id_)).first()
        u.active = False
        db.session.commit()
        return jsonify({'status':True})
    except Exception as e:
        return jsonify({'status':False, 'error':e})

@user.route('/m/input', methods=['GET','POST'])
@token_required
def m_input(id_):
    print("i am out....")
    if request.method == "POST":
        print("i am post")
        u=Users.query.filter_by(id=int(id_)).first()
        state = u.state
        mandal = u.mandal
        const = request.get_json()['constituency']
        assembly = request.get_json()['assembly']
        number = request.get_json()['poll_num']
        code = request.get_json()['code']

        print(const, assembly, number, code)
        
        if const!="" and assembly!="" and number!="" and code!="":
            station = PollingStations.query.filter_by(number=int(number),assembly=assembly,code=code,state=state).first()
            print(station)
            if station:
                if u.assembly == assembly.lower() and int(u.polling_station.split('-')[0]) == int(station.number):
                    poll_name = station.name
                    loc = station.location
                    return jsonify({'status':'ok','loc':loc, 'constituency':const,'poll_name':poll_name,'location':station.location, 'assembly':assembly, 'poll_num' :station.number})
                return jsonify({'status':'not_ok','error':"You are not authorized here"})
            else:
                return jsonify({'status':'not_ok','error':"An error occured"})
        else:
            return jsonify({'status':'not_ok','error':"Invalid Constituency"})
    else:
        u=Users.query.filter_by(id=int(id_)).first()
        state = u.state
        mandal = u.mandal
    consts = Constituencies.query.filter_by(state=state).all()
    consts_ = [i.name for i in consts]
    consts_ = list(set(consts_))
    assemblies = []
    return jsonify({'status':'ok','constituencies':consts_, 'assemblies':assemblies})

@user.route('/m/entry',methods=["GET","POST"])
@token_required
def m_entry(id_):
    if request.method=="POST":
        u = Users.query.filter_by(id=int(id_)).first()
        mandal = request.get_json()['mandal'].lower()
        serial_no = request.get_json()['serial_no']
        consti = request.get_json()['constituency']
        epic_no = request.get_json()['epic_no']
        assembly = request.get_json()['assembly']
        poll_no = request.get_json()['polling_no']
        poll_name = request.get_json()['poll_name']
        main_village = request.get_json()['main_village']
        habitation = request.get_json()['habitation']
        house_no = request.get_json()['house_no']
        family_no = request.get_json()['family_no']
        voter_name = request.get_json()['voter_name']
        father_name = request.get_json()['father_name']
        age = request.get_json()['age']
        gender = request.get_json()['gender']
        relation = request.get_json()['relation']
        religion = request.get_json()['religion']
        community = request.get_json()['community']
        ht = request.get_json()['house_type']
        sub_caste = request.get_json()['sub_caste']
        qualification = request.get_json()['qualification']
        number = request.get_json()['contact_no']
        special_cat = request.get_json()['special_category']
        email = request.get_json()['email']
        party_affiliation = request.get_json()['party_affiliation']
        influencer = request.get_json()['leader']
        influencer_party = request.get_json()['influencer_party']
        vt = request.get_json()['vehicle']
        dob = request.get_json()['dob']
        native_district = request.form.get('native_district')
        phone_type = request.form.get_json()['phone_type']
        native_state = request.form.get('native_state')
        if native_district:
            native_district=native_district.lower().strip()
        else:
            native_district=""
        if native_state:
            native_state=native_state.lower().strip()
        else:
            native_state=""
        
        if 'none' not in vt:
            vt = list(set(vt))
            vt = list_to_str(vt)
        else:
            vt = "none"

        if number is not None:
            if len(number)!=10:
                flash("Enter valid contact number")
                return jsonify({'status':'not ok','error':'Enter valid contact number!', "constituency":consti, "ps_name":poll_name, "assembly": assembly, "ps_no":poll_no})
            try:
                k = int(number)
            except:
                return jsonify({'status':'not ok','error':'Enter valid contact number!', "constituency":consti, "ps_name":poll_name, "assembly": assembly, "ps_no":poll_no})
        else:
            number = ""
        profession = request.get_json()['profession']
        company = request.get_json()['company']
        w_place = request.get_json()['working_place']

        dept = request.get_json()['department']

        res_type = request.get_json()['residence_type']
        if res_type != 'local':
            residence = request.get_json()['residence']
        else:
            residence =""
        
        bt = request.get_json()['business_type']
        benf = request.get_json()['is_beneficiary']
        bens=None
        if benf == "yes":
            lis = request.get_json()['beneficiary']
            lis=list(set(lis))
            ben=""
            if 'asara' in lis:
                asr = request.get_json()['asara']
                asr=list_to_str(asr)
                lis.remove('asara')
                ben = list_to_str(lis)
                bens = ben + ','+asr.strip()
            else:
                bens = list_to_str(lis)
        else:
            benf = ""

        voter = Voters.query.filter_by(epic_no=epic_no).first()
        if voter:
            voter.mandal = mandal
            voter.habitation = habitation
            voter.town = main_village
            voter.department = dept
            voter.community = community
            voter.sub_caste = sub_caste
            voter.qualification = qualification
            voter.profession = profession
            voter.company =company
            voter.dob = dob
            voter.native_district=native_district
            voter.native_state = native_state
            voter.working_place = w_place
            voter.business_type = bt
            voter.is_beneficairy = benf
            voter.beneficiaries = bens
            voter.email = email
            voter.contact_no = number
            voter.party_affiliation = party_affiliation
            voter.residence_type = res_type
            voter.residence = residence
            voter.modified_by = u.phone_number
            voter.special_category = special_cat
            voter.phone_type = phone_type
            voter.house_type = ht
            voter.influential_leader = influencer
            voter.local_leader_party = influencer_party
            voter.vehicle_type = vt
            
            flash('Voter is updated successfully!', 'success')
            ps = PollingStations.query.filter_by(number=int(poll_no),assembly=u.assembly,party=u.party,state=u.state).first()
            if ps.completed_serial_nos != "":
                ps_ = ps.completed_serial_nos+','+serial_no
            else:
                ps_ = serial_no
            ps.completed_serial_nos = ps_
            db.session.commit()
            
            return jsonify({'status':'ok', "constituency":consti, "ps_name":poll_name, "assembly": assembly, "ps_no":poll_no})

        voter = Voters(
            mandal = mandal,
            serial_no = serial_no,
            epic_no = epic_no,
            constituency = consti,
            assembly=assembly,
            polling_number = poll_no,
            habitation = habitation,
            town = main_village,
            house_no = house_no,
            family_no = family_no,
            name = voter_name,
            guardian_name = father_name,
            department = dept,
            age = age,
            dob = dob,
            native_district=native_district,
            native_state = native_state,
            gender = gender,
            relation = relation,
            religion = religion,
            community = community,
            sub_caste = sub_caste,
            qualification = qualification,
            profession = profession,
            company = company,
            working_place = w_place,
            business_type = bt,
            is_beneficiary = benf,
            beneficiaries = bens,
            email = email,
            contact_no=number,
            party_affiliation=party_affiliation,
            residence_type = res_type,
            house_type=ht,
            residence = residence,
            state = u.state,
            influential_leader = influencer,
            local_leader_party = influencer_party,
            modified_by = u.phone_number,
            vehicle_type = vt,
            phone_type = phone_type
        )
        db.session.add(voter)
        ps = PollingStations.query.filter_by(number=int(poll_no),assembly=u.assembly,party=u.party,state=u.state).first()
        if ps.completed_serial_nos != "":
            ps_ = ps.completed_serial_nos+','+serial_no
        else:
            ps_ = serial_no
        ps.completed_serial_nos = ps_
        db.session.commit()
        return jsonify({'entered':True, "constituency":consti, "ps_name":poll_name, "assembly": assembly, "ps_no":poll_no})

    u = Users.query.filter_by(id=int(id_)).first()
    const = request.args.get('constituency')
    poll_no = request.args.get('poll_num')
    assembly = request.args.get('assembly')
    poll_name = request.args.get('poll_name')
 
    a = AssemblyAdmin.query.filter_by(assembly=u.assembly, party=u.party, state=u.state).first()
    state = u.state
    mandals = Mandals.query.filter_by(assembly=a.assembly).first().mandals
    mandals = [i.strip() for i in mandals.split(',')]
    religions = Religions.query.filter_by(state=state).all()
    religions = [i.name for i in religions]
    communities = Communities.query.filter_by(state=state).all()
    communities = [i.name for i in communities]
    constituencies = Constituencies.query.filter_by(state=state).all()
    constituencies = [i.name for i in constituencies]
    parties = Parties.query.all()
    ps = PollingStations.query.filter_by(number=poll_no,state=u.state,assembly=u.assembly,party=u.party).first()
    if ps.completed_serial_nos:
        ps_serials = [int(i) for i in ps.completed_serial_nos.split(',')]
    else:
        ps_serials=[]
    serials = [i for i in range(1,1500) if i not in ps_serials]
    parties = [i.name for i in parties]

    return jsonify({'status':'ok', "mandals":mandals, "serials":serials, "constituency":const, "ps_no":poll_no,"ps_name":poll_name, "assembly":assembly, "constituencies":constituencies, "religions":religions,"communities":communities, "parties":parties})

@user.route('/m/check-serial', methods=['POST'])
@token_required
def m_check_serial(id_):

    u = Users.query.filter_by(id=int(id_)).first()
    s = request.get_json()['serial-no'].strip()
    vs = Voters.query.filter_by(serial_no=s,assembly=u.assembly,state=u.state).first()
    if vs:
        da = {
            'name':vs.name,
            'age':vs.age,
            'epic_no':vs.epic_no,
            'house_no':vs.house_no,
            'gender':vs.gender,
            'relation':vs.relation,
            'guardian':vs.guardian_name
        }
        return jsonify({'filled':True, 'data':da, 'notfilled':False})
    else:
        return jsonify({'notfilled':True, 'filled':False})

@user.route('/m/get-subcastes', methods=["POST"])
@token_required
def m_get_subcastes():
    comm = request.get_json()['community'].lower()
    castes = Communities.query.filter_by(name=comm).first()
    try:
        _castes = [i.strip() for i in castes.sub_castes.split(',')]
    except:
        _castes = []
    return jsonify({'subcastes':_castes})


@user.route('/m/get-communities', methods=["POST"])
@token_required
def m_get_communities():
    state = Users.query.filter_by(id=int(request.args.get('id'))).first().state
    try:
        coms = Communities.query.filter_by(state=state).all()
        coms = [i.name for i in coms]
    except:
        coms = []
    return jsonify({'communities':coms})

@user.route('/m/get-assemblies', methods=['POST'])
@token_required
def m_get_assemblies():
    con = request.get_json()['constituency']
    res = Constituencies.query.filter_by(name=con).first()
    result = res.assemblies.split(',')
    result = [i.strip() for i in result]
    return jsonify({'assemblies': result})

@user.route('/m/get-pn', methods=["POST"])
@token_required
def m_get_pn():
    c = request.get_json()['constituency']
    a = request.get_json()['assembly']
    
    sts = PollingStations.query.filter_by(constituency=c,assembly=a).all()
    
    stations = [i.number+"-"+i.name for i in sts]
    
    return jsonify({'pn':stations})


#Unused
@user.route('/m/get-ps', methods=['POST'])
@token_required
def m_get_ps():
    if request.method== "POST":
        mandal = request.get_json()['mandal'].lower()
        if mandal:
            mandal = mandal.lower()
        sts = PollingStations.query.filter_by(mandal=mandal).all()
        res = [i.number+'-'+i.name for i in sts]
        return jsonify({'ps':res})


'''
@user.route('/m/get-mandals', methods=['POST'])
def m_get_mandals():
    assem = request.get_json()['assembly').lower()
    try:
        vs = Voters.query.filter_by(assembly=assem).all()
        result = [i.mandal.strip() for i in vs]
        result=list(set(result))
    except:
        result = []
    return jsonify({'mandals': result})
'''

@user.route('/m/otp', methods=['POST'])
@token_required
def m_otp():
    if request.method=="POST":
        otp_ = request.get_json()['otp']
        role = request.get_json()['role']
        id = request.get_json()['id']
        if role=='user':
            u = Users.query.filter_by(id=int(id)).first()
            if u.otp==otp_:
                session['user'] = u.id
                u.active = True
                u.otp = ''
                db.session.commit()
                return jsonify({'status':'ok'})
        return jsonify({'status':'not ok','error':'Invalid OTP!'})


