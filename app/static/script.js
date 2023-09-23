
$('#businessFields').hide()
$('#rbusinessFields').hide()
$('#rbeneficiaryList').hide()
$('#showAsara').hide()
$('#govtFields').hide()
$('#normalFields').hide()
$('#showResidence').hide()
$('#beneficiariesList').hide()
$('#religiousFields').hide()
 

$(document).on('change','#profession' ,function(){
    var p = $(this).val()
    if (p === "self-employed" || p === "business"){
        $("#businessFields").show(300)
        $("#normalFields").hide()
        $('#govtFields').hide()
        $('#religiousFields').hide()
    }
    else if (p=== "private-employee"){
        $("#normalFields").show(300)
        $("#businessFields").hide()
        $('#govtFields').hide()
        $('#religiousFields').hide()
    }
    else if (p === "govt-employee"){
        $('#govtFields').show()
        $("#businessFields").hide()
        $("#normalFields").hide()
        $('#religiousFields').hide()
    }
    else if(p === "religious-leader"){
        $('#govtFields').hide()
        $("#businessFields").hide()
        $("#normalFields").hide()
        $('#religiousFields').show(300)
    }
    else{
        $('#govtFields').hide()
        $("#businessFields").hide()
        $("#normalFields").hide()
        $('#religiousFields').hide()
    }
})

function closeMessage(){
    $('.success').hide(300)
    $('.error').hide(300)
    $('.warning').hide(300)
}

$(document).on('change','#mymandal', function(){
    var c = $('#mymandal').val()
    $.ajax({
        type : 'post',
        url : '/get-ps',
        data : {'mandal':c}
    })
    .done(function(response){
        if(response.result){
            $("#changeps").empty()
            response.result.forEach(a => {
                $("#changeps").append('<option value='+a+'>'+a+'</option>')
            });
        }
        else{
            alert('An error occured!')
        }
    })
})

$(document).on('change','#selectedConstituency', function(){
    var c = $('#selectedConstituency').val()
    $.ajax({
        type : 'post',
        url : '/get-assemblies',
        data : {'constituency':c}
    })
    .done(function(response){
        if(response.result){
            $("#changeAssembly").empty()
            $("#changeAssembly").append('<option value="none">--SELECT--</option>')
            response.result.forEach(a => {
                $("#changeAssembly").append('<option value='+a+'>'+a+'</option>')
            });
        }
        else{
            alert('An error occured!')
        }
    })
})

$(document).on('change','#religion',function(){
    let v = $(this).val()
    if (v=='muslim'){
        $('#community').empty()
        $('#showSubcastes').empty()
        $('#community').append('<option value="muslim">muslim</option>')
        $('#showSubcastes').append('<option value="muslim">muslim</option>')
    }
    else{

        $.ajax({
            type : "post",
            url : "/get-communities",
        })
        .done(function(response){
            $('#community').empty()
            $('#community').append('<option value="none">--select--</option>')
            j=1;
            response.communities.forEach(s => {
                $('#community').append(
                    '<option value='+s+'>'+j+'. '+s+'</option>')
                j++;
            });
        })
 
    }
})


$(document).on('change','#is_beneficiary', function(){
    var b = $(this).val()
    if(b === 'yes'){
        $('#beneficiariesList').show(300)
    }
    else{
        $('#beneficiariesList').hide(300)
    }
})

$(document).on('change','#residence', function(){
    var b = $(this).val()
    if(b === 'non-local'){
        $('#showResidence').show(300)
    }
    else{
        $('#showResidence').hide(300)
    }
})

$(document).on('change','#community' ,function(){
    var p = $(this).val()
    if(p=='north indian' || p=='north'){
        $('#showSubcastes').empty()
        $('#showSubcastes').append('<option value="north indian">North Indian</option>')
    }
    else{
        $.ajax({
            type : "post",
            url : "/get-subcastes",
            data : {'community':p}
        })
        .done(function(response){
            $('#showSubcastes').empty()
            $('#showSubcastes').append('<option value="none">--select--</option>')
            j=1;
            response.subcastes.forEach(s => {
                $('#showSubcastes').append('<option value='+s+'>'+j+'. '+s+'</option>')
                j++;
            });
        })
    }
})

$(document).on('change','#rcommunity' ,function(){
    var p = $(this).val()
    $.ajax({
        type : "post",
        url : "/get-subcastes",
        data : {'community':p}
    })
    .done(function(response){
        $('#showSubcastes').empty()
        $('#showSubcastes').append('<option value="all">all</option>')
        j=1;
        response.subcastes.forEach(s => {
            $('#showSubcastes').append('<option value='+s+'>'+j+'. '+s+'</option>')
            j++;
        });
    })
})

$(document).on('change','#beneficiary' ,function(){
    var p = $(this).prop('checked')
    if(p === true){
        $('#showAsara').show(300)
    }
    else{
        $('#showAsara').hide(300)
    }
})

$(document).on('submit','#initialdata form', function(e){
    $.ajax({
        type : 'post',
        url: '/get-form',
        data : $('#initialdata form').serialize()
    })
    .done(function(response){
        if (response.form){
            $('#add-form').append(response.form)
        }
    })
    e.preventDefault()
})

$(document).on('change','#rselectedConstituency',function(){
    c = $('#rselectedConstituency').val()
    if (c !== 'all'){
        $.ajax({
            type : 'post',
            url : '/get-assemblies',
            data : {'constituency':c}
        })
        .done(function(response){
            if(response.result){
                $("#rchangeAssembly").empty()
                $("#rchangeAssembly").append('<option value="all">ALL</option>')
                response.result.forEach(a => {
                    $("#rchangeAssembly").append('<option value='+a+'>'+a+'</option>')
                });
            }
            else{
                alert('An error occured!')
            }
        })
    }
    else{
        $("#rchangeAssembly").empty()
        $("#rchangeAssembly").append('<option value="all">ALL</option>')
        $("#rpollingNo").empty()
        $("#rpollingNo").append('<option value="all">ALL</option>')
        $("#rmandal").empty()
        $("#rmandal").append('<option value="all">ALL</option>')
    }
})

$(document).on('change','#armandal',function(){
    c = $('#armandal').val()
    a = $('#rchangeAssembly').val()
    if (c !== 'all'){
        $.ajax({
            type : 'post',
            url : '/get-ps-reports',
            data : {'mandal':c,'assembly':a}
        })
        .done(function(response){
            if(response.result){
                $("#rpollingNo").empty()
                $("#rpollingNo").append('<div class="checkbox"><input type="checkbox" name="stations" value="all"><span>ALL</span></div>')
                response.result.forEach(a => {
                    $("#rpollingNo").append('<div class="checkbox"><input type="checkbox" name="stations" value="'+a+'"><span>'+a+'</span></div>')
                });
            }
            else{
                alert('An error occured!')
            }
        })
    }
})

$(document).on('change','#rchangeAssembly',function(){
    c = $('#rchangeAssembly').val()
    if (c !== 'all'){
        $.ajax({
            type : 'post',
            url : '/get-mandals',
            data : {'assembly':c}
        })
        .done(function(response){
            if(response.result){
                $("#rmandal").empty()
                $("#rmandal").append('<option value="all">ALL</option>')
                response.result.forEach(a => {
                    $("#rmandal").append('<option value='+a+'>'+a+'</option>')
                });
            }
            else{
                alert('An error occured!')
            }
        })
    }
    else{
        $("#rpollingNo").empty()
        $("#rpollingNo").append('<option value="all">ALL</option>')
        $("#rmandal").empty()
        $("#rmandal").append('<option value="all">ALL</option>')
    }
})


$(document).on('change','#rmandal',function(){
    c = $('#rmandal').val()
    d = $('#rchangeAssembly').val()
    if (c !== 'all'){
        $.ajax({
            type : 'post',
            url : '/get-ps-reports',
            data : {'mandal':c,'assembly':d}
        })
        .done(function(response){
            if(response.result){
                $("#rpollingNo").empty()
                $("#rpollingNo").append('<option value="all">ALL</option>')
                response.result.forEach(a => {
                    $("#rpollingNo").append('<option value='+a+'>'+a+'</option>')
                });
            }
            else{
                alert('An error occured!')
            }
        })
    }
    else{
        $("#rpollingNo").empty()
        $("#rpollingNo").append('<option value="all">ALL</option>')
    }
})

$(document).on('click','#rpollingNo', function(){
    let cons = $('#rselectedConstituency').val()
    let assem = $('#rchangeAssembly').val()
    let p = $('#rpollingNo').val()
    $.ajax({
        type:'post',
        url:'/get-habitations-leaders',
        data:{'assembly':assem, 'ps':p, 'constituency':cons}
    })
    .done(function(response){
        if(response.result){
            $('#showHabitations').empty()
            response.result.forEach(h => {
                $('#showHabitations').append('<div class="checkbox"><input type="checkbox" name="habitations" value="'+h+'"><span>'+h+'</span></div>')
            })
        }
        if (response.leaders){
            $('#showLeaders').empty()
            response.leaders.forEach(h => {
                if(h!=null){
                $('#showLeaders').append('<div class="checkbox"><input type="checkbox" name="leaders" value="'+h+'"><span>'+h+'</span></div>')
                }
            })
        }
    })
})


$(document).on('change','#rprofession' ,function(){
    var p = $(this).val()
    if (p === "self-employed" || p === "business"){
        $("#rbusinessFields").show(300)
    }
    else{
        $("#rbusinessFields").hide()
    }
})

$(document).on('change', '#rprofession input[type="radio"]',function(){
    var d = $(this).val()
    if (d==='yes'){
        $('#rbeneficiaryList').show()
    }
    else{
        $('#rbeneficiaryList').hide()
    }
})

$(document).on('change','#rbeneficiary',function(){
    var b = $(this).val()
    if (b==='asara'){
        $('#showAsara').show()
    }
    else{
        $('#showAsara').hide()
    }
})


$(document).on('change','#changeAssembly',function(){
    let c = $('#selectedConstituency').val()
    let a = $('#changeAssembly').val()
    $.ajax({
        type : 'post',
        url : '/get-pn',
        data : {'assembly':a, 'constituency':c}
    })
    .done(function(response){
        console.log(response)
        if(response.pn){
            $("#polling_stations").empty()
            $("#polling_stations").append('<option value="none">--select--</option>')
            response.pn.forEach(a => {
                $("#polling_stations").append('<option value='+a+'>'+a+'</option>')
            });
        }
    })

})


$(document).on('submit','#broadcast-form',function(e){
    let msg = $('#broadcast-form textarea[name="message"]').val()
    let nums = $('.mycontacts')
    let finalNUms = []
    nums.each(function(){
        finalNUms.push($(this).html())
    })
    $.ajax({
        type: 'post',
        url: '/broadcast',
        data : {'message':msg,'numbers':finalNUms}
    })
    .done(function(response){
        if(response.error){
            alert(response.error)
        }
        if(response.sent_count){
            alert("The message was sent to "+response.sent_count+" voters.")
        }
        if(response.unsent_numbers){
            alert("The message was not sent to "+response.unsent_numbers+" voters.")
        }
    })
    e.preventDefault()
})

$(document).on('submit','#voice-broadcast-form',function(e){
    let msg = $('#voice-broadcast-form textarea[name="message"]').val()
    let nums = $('.mycontacts')
    let finalNUms = []
    nums.each(function(){
        finalNUms.push($(this).html())
    })
    $.ajax({
        type: 'post',
        url: '/voice-broadcast',
        data : {'message':msg,'numbers':finalNUms}
    })
    .done(function(response){
        if(response.error){
            alert(response.error)
        }
        if(response.sent_count){
            alert("The message was sent to "+response.sent_count+" voters.")
        }
        if(response.unsent_numbers){
            alert("The message was not sent to "+response.unsent_numbers+" voters.")
        }
    })
    e.preventDefault()
})

$(document).on('change','#myserial',function(){
    let v = $(this).val()
    $.ajax({
        type : "post",
        url : "/check-serial",
        data : {'s':v}
    })
    .done(function(response){
        if (response.notfilled){
            $('.input-field input[name="voter_name"]').val("")
            $('.input-field input[name="house_no"]').val("")
            $('.input-field input[name="father_name"]').val("")
            $('.input-field input[name="age"]').val("")
            $('.input-field input[name="epic_no"]').val("")
        }
        else{
            data = response.data

            $('.input-field input[name="voter_name"]').val(data.name)
            $('.input-field input[name="voter_name"]').prop('disabled', true);

            $('.input-field input[name="house_no"]').val(data.house_no)
            $('.input-field input[name="house_no"]').prop('disabled', true);

            $('.input-field input[name="father_name"]').val(data.guardian)
            $('.input-field input[name="father_name"]').prop('disabled', true);

            //$('.input-field input[name="relation"]').prop('type','text')
            $('.input-field select[name="relation"]').val(data.relation)
            $('.input-field select[name="relation"]').prop('disabled',true)

            $('.input-field input[name="age"]').val(data.age)
            $('.input-field input[name="age"]').prop('disabled', true);

            $('.input-field input[name="epic_no"]').val(data.epic_no)
            $('.input-field input[name="epic_no"]').prop('disabled', true);

            //$('.input-field input[name="gender"]').prop('type','text')
            $('.input-field select[name="gender"]').val(data.gender)
            $('.input-field select[name="gender"]').prop('disabled',true)
        }
    })
})

/*
let ctx = document.getElementById('myChart').getContext('2d');

let myChart = new Chart(ctx, {
    type: 'pie',
    data:{
        datasets:[{
            data: [30, 10, 40, 20],
            backgroundColor: ['#FB3640', '#EFCA08', '43AA8B', '#253D5B']
        }],
        labels: ['Pizza', 'Tago', 'Hotdog', 'Sushi']
    },
    OPTIONS: {
        responsive: true
    }
})
*/