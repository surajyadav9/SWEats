
// Delete item confirmation pop-up
$(document).ready(function(){
    $(".delete-item-form").submit(function(event) {
        if( !confirm('Are you sure that you want to delete?') ) 
            event.preventDefault();
    });
});