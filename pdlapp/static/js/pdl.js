$( document ).ready( function() {
  
    feather.replace()
  
    $( '.pdl-setting' ).change( function() {
        $( '#status' ).text( 'Saving settings...' );
        $.post('/update_settings', $( '#settingsForm' ).serialize() )
        .done( function( response ) {
            $( '#status' ).text( response.msg );
            console.log(response.msg);
        });
    });

    $( 'a.pdl-action' ).click( function(event) {
        console.log($(event.target));
        console.log($( event.target ).parent().parent().parent().find( 'select' ).attr('id'));
    });

});
