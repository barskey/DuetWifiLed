$( document ).ready( function() {
  
    $( '#setup' ).addClass( 'active' );

    setInterval( function () {
        $.post('/get_status')
        .done( function( response ) {
            console.log(response);
            $( '#status' ).text( 'Printer state ' + response.state );
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
