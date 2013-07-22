/*---
Autocomplete functions
---*/
function makeautocomplete(elementid, vidparam, hiddeninput, extra_params)
{
    var extra_parameters = ''
    for(var key in extra_params){
	// FIXME where is this key contains comming from??
	if (key != 'contains')
	{
	    extra_parameters += '&' + key + '=' + extra_params[key];
	}
    }
    // put all your jQuery goodness in here.
    $(elementid).autocomplete("/?vid=" + vidparam + extra_parameters, {
	width: 260,
	selectFirst: false,
	formatItem: function(row){
	    display=row[0] + ' ' +row[1];
	    return display;
	}
    });

    $(elementid).result(function(event, data, formatted) {
	if (data)
	    $(hiddeninput).val(data[2]);
    });
}

function redirect_edit_controller(subject, relation, parent_eid, url)
{
    if (subject == 'True')
    	related_entity_id = 'entityeid_' + relation + '_' + parent_eid + '_subject';
    else
	related_entity_id = 'entityeid_' + relation + '_' + parent_eid + '_object';

    related_entity = $('#' + related_entity_id).val();
    if (related_entity.length > 0){
        controller = "/autocomplete-entity-controller?subject="+subject+"&relation="+relation+"&parent_eid="+parent_eid+"&__redirect="+url+'&'+related_entity_id+'='+related_entity;
        window.location=controller;
    }
    else{
        alert("Please select a value");
    }
}
