// https://stackoverflow.com/a/36145278

var chosen_inds = cb_obj.active;

var chosen_widget_groups = [];

for (var i = 0; i < group_list.length; ++ i){
    if (chosen_inds.includes(i)){
        chosen_widget_groups.push(group_list[i])
    };
};

to_select_inds = []

for (var i = 0; i < source.data['index'].length; ++ i){
    if (chosen_widget_groups.includes(source.data['widget_group'][i])){
        to_select_inds.push(i)
    };
};

source.selected.indices = to_select_inds;
source.change.emit();