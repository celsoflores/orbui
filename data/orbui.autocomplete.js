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