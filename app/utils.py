def list_to_str(string):
    s = ""
    if string != "":
        for i in string:
            s+=i+","
        return s[:-1]
    return s

def get_summary(result, size='all'):
    siz=size
    res = result
    summ = {
        'age':{'18-29':0,'30-45':0,'46-57':0,'30-57':0,'58+':0,'70+':0,'sum':0},
        'gender':{'male':0,'female':0,'others':0,'sum':0},
        'religion':{'sum':0},
        'community':{'sum':0},
        'education':{'sum':0},
        'profession':{'sum':0},
        'party-affiliation':{'sum':0},
        'residence-type':{'sum':0},
        'house-type': {'sum':0},
        'sub-caste':{'sum':0},
        'special-category':{'sum':0},
        'individual-beneficiaries':{'sum':0},
        
        'family_size':{1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0,'sum':0},
        'local_leader':{'sum':0},
        'vehicle-type':{'sum':0},
        'utils':{}
    }
    families = []
    for i in res:
        try:
            families.append(i.family_no.strip())
        except:
            pass
        
        if int(i.age)<=29:
            summ['age']['18-29']+=1
            summ['age']['sum']+=1
        elif 30 <= int(i.age) and int(i.age) <= 45:
            summ['age']['30-45']+=1
            summ['age']['sum']+=1
        elif 30<= int(i.age) and int(i.age)<=57:
            summ['age']['30-57']+=1
            summ['age']['sum']+=1
        elif int(i.age)>=57 and int(i.age)<=70:
            summ['age']['58+']+=1
            summ['age']['sum']+=1
        else:
            summ['age']['70+']+=1
            summ['age']['sum']+=1
        
        c = i.gender
        try:
            summ['gender'][c]+=1
            summ['gender']['sum']+=1
        except:
            summ['gender'].update({c:1})
            summ['gender']['sum']+=1
        
        c = i.religion
        if c is not None:
            try:
                summ['religion'][c]+=1
                summ['religion']['sum']+=1
            except:
                summ['religion'].update({c:1})
                summ['religion']['sum']+=1
        
        c = i.community
        if c is not None:
            try:
                summ['community'][c]+= 1
                summ['community']['sum']+=1
            except:
                summ['community'].update({c:1})
                summ['community']['sum']+=1
        
        c = i.qualification
        if c is not None:
            try:
                summ['education'][c]+=1
                summ['education']['sum']+=1
            except:
                summ['education'].update({c:1})
                summ['education']['sum']+=1

        c=i.profession
        if c is not None:
            try:
                summ['profession'][c]+=1
                summ['profession']['sum']+=1
            except:
                summ['profession'].update({c:1})
                summ['profession']['sum']+=1

        c = i.party_affiliation
        if c is not None:
            try:
                summ['party-affiliation'][c]+=1
                summ['party-affiliation']['sum']+=1
            except:
                summ['party-affiliation'].update({c:1})
                summ['party-affiliation']['sum']+=1

        c = i.residence_type
        if c is not None:
            try:
                summ['residence-type'][c]+=1
                summ['residence-type']['sum']+=1
            except:
                summ['residence-type'].update({c:1})
                summ['residence-type']['sum']+=1
        
        c = i.house_type
        if c is not None:
            try:
                summ['house-type'][c]+=1
                summ['house-type']['sum']+=1
            except:
                summ['house-type'].update({c:1})
                summ['house-type']['sum']+=1
        
        c = i.sub_caste
        if c is not None:
            try:
                summ['sub-caste'][c] +=1
                summ['sub-caste']['sum']+=1
            except:
                summ['sub-caste'].update({c:1})
                summ['sub-caste']['sum']+=1
                
        c = i.special_category
        if c is not None:
            try:
                summ['special-category'][c] +=1
                summ['special-category']['sum']+=1
            except:
                summ['special-category'].update({c:1})
                summ['special-category']['sum']+=1

        ibs = i.beneficiaries
        if ibs is not None:
            for k in ibs.split(','):
                j = k.strip()
                try:
                    summ['individual-beneficiaries'][j]+=1
                    summ['individual-beneficiaries']['sum']+=1
                except:
                    if j=='':
                        continue
                    summ['individual-beneficiaries'].update({j:1})
                    summ['individual-beneficiaries']['sum']+=1
        
        lok = i.influential_leader
        if lok is not None:
            try:
                summ['local_leader'][lok]+=1
                summ['local_leader']['sum']+=1
            except:
                summ['local_leader'].update({lok:1})
                summ['local_leader']['sum']+=1
        
        lok = i.vehicle_type
        if lok is not None:
            for j in lok.split(','):
                try:
                    summ['vehicle-type'][j]+=1
                    summ['vehicle-type']['sum']+=1
                except:
                    summ['vehicle-type'].update({j:1})
                    summ['vehicle-type']['sum']+=1
        
    
    religions = list(summ['religion'].keys())
    summ['utils'].update({'religions':religions[1:]})
    
    communities = list(summ['community'].keys())
    summ['utils'].update({'communities':communities[1:]})
    
    castes = list(summ['sub-caste'].keys())
    summ['utils'].update({'castes':castes[1:]})
    
    specials = list(summ['special-category'].keys())
    summ['utils'].update({'specials':specials[1:]})
    
    bens = list(summ['individual-beneficiaries'].keys())
    summ['utils'].update({'bens':bens[1:]})
    
    edus = list(summ['education'].keys())
    summ['utils'].update({'edus':edus[1:]})
    
    pro = list(summ['profession'].keys())
    summ['utils'].update({'pro':pro[1:]})
    
    aff = list(summ['party-affiliation'].keys())
    summ['utils'].update({'aff':aff[1:]})
    
    vehicle = list(summ['vehicle-type'].keys())
    summ['utils'].update({'vehicle':vehicle[1:]})
    
    house = list(summ['house-type'].keys())
    summ['utils'].update({'house':house[1:]})
    
    resd = list(summ['residence-type'].keys())
    summ['utils'].update({'resd':resd[1:]})
    
    leader = list(summ['local_leader'].keys())
    summ['utils'].update({'leader':leader[1:]})
    
    return summ