from app import db

class Voters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial_no = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    epic_no = db.Column(db.String(20), nullable=False)
    mandal = db.Column(db.String(30))
    polling_number = db.Column(db.String(20), nullable=False)
    age = db.Column(db.String(20))
    gender = db.Column(db.String(20), nullable=False)
    constituency = db.Column(db.String(20), nullable=False)
    habitation = db.Column(db.String(20))
    house_no = db.Column(db.String(20))
    family_no = db.Column(db.String(20))
    guardian_name = db.Column(db.String(20))
    relation = db.Column(db.String(20))
    native_district = db.Column(db.String(20))
    native_state = db.Column(db.String(20))
    religion = db.Column(db.String(20))
    community = db.Column(db.String(20))
    sub_caste = db.Column(db.String(20))
    qualification = db.Column(db.String(20))
    profession = db.Column(db.String(20))
    company = db.Column(db.String(20))
    department = db.Column(db.String(20))
    working_place = db.Column(db.String(20))
    business_type = db.Column(db.String(20))
    is_beneficiary = db.Column(db.String(20))
    beneficiaries  = db.Column(db.Text)
    contact_no = db.Column(db.String(20))
    email = db.Column(db.String(20))
    assembly = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    town = db.Column(db.String(20))
    house_type=db.Column(db.String(20))
    residence_type = db.Column(db.String(20))
    residence = db.Column(db.String(60))
    vehicle_type = db.Column(db.String)
    party_affiliation=db.Column(db.String(20))
    dob = db.Column(db.String)
    phone_type = db.Column(db.String(20))
    
    influential_leader = db.Column(db.String(50))
    local_leader_party = db.Column(db.String(20))
    
    special_category = db.Column(db.String(30))
    modified_by = db.Column(db.String(15))

class PollingStations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    party = db.Column(db.String, nullable=False)
    state = db.Column(db.String(20), nullable=False)
    assembly = db.Column(db.String(50), nullable=False)
    constituency =db.Column(db.String(20), nullable=False)
    mandal = db.Column(db.String(50))
    location = db.Column(db.Text)
    completed_serial_nos = db.Column(db.Text)
    number = db.Column(db.String(20))
    code = db.Column(db.String(20)) 

class Mandals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    constituency =db.Column(db.String(20), nullable=False)
    assembly = db.Column(db.String(50), nullable=False)
    mandals = db.Column(db.Text)
    party = db.Column(db.String, nullable=False)
    state = db.Column(db.String(20), nullable=False)

class Constituencies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    assemblies = db.Column(db.Text)
    party = db.Column(db.String, nullable=False)
    state = db.Column(db.String(20), nullable=False)
    
class Religions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False)

class Communities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    sub_castes = db.Column(db.Text)
 
class Parties(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    leader_name = db.Column(db.String(50))
    party = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    polling_station = db.Column(db.String, nullable=False)
    constituency =db.Column(db.String(20), nullable=False)
    assembly = db.Column(db.String, nullable=False)
    mandal = db.Column(db.String(50))
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    party = db.Column(db.String(60), nullable=False)
    active = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(10))

class AssemblyAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    party = db.Column(db.String,nullable=False)
    state = db.Column(db.String, nullable=False)
    assembly = db.Column(db.String, nullable=False)
    mandal = db.Column(db.String(50))
    party = db.Column(db.String(60), nullable=False)
    constituency = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    active = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(10))

class ConstituencyAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    constituency = db.Column(db.String(50), nullable=False)
    party = db.Column(db.String,nullable=False)
    state = db.Column(db.String, nullable=False)
    mandals = db.Column(db.Text)
    party = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    active = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(10))

class StateAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    party = db.Column(db.String,nullable=False)
    state = db.Column(db.String, nullable=False)    
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    party = db.Column(db.String(60), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    active = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(10))
