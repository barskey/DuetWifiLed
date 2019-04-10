$( document ).ready( function() {
  
    feather.replace()
  
    $( '.pdl-setting' ).change( function() {

        $.post('/update_settings', $( '#settingsForm' ).serialize() )
        .done( function( response ) {
            console.log(response.msg);
        });
    });

});
