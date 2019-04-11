$( document ).ready( function() {
  
    $( '#setup' ).addClass( 'active' );
  
    $( '.pdl-setting' ).change( function() {
        $( '#status' ).text( 'Saving settings...' );
        $.post('/update_settings', $( '#settingsForm' ).serialize() )
        .done( function( response ) {
            $( '#status' ).text( response.msg );
            console.log(response.msg);
        });
    });

});
