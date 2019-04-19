$( document ).ready( function() {
  
    $( '#setup' ).addClass( 'active' );

    setInterval( function () {
        $.post('/get_status')
        .done( function( response ) {
            $( '#status' ).text( response.state );
        });
    }, 5000);
  
    $( '.pdl-setting' ).change( function() {
        $( '#status' ).text( 'Saving settings...' );
        $.post('/update_settings', $( '#settingsForm' ).serialize() )
        .done( function( response ) {
            $( '#status' ).text( response.msg );
            console.log(response.msg);
        });
    });

});
