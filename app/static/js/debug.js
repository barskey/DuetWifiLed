$( document ).ready( function() {
  
    $( '#debug' ).addClass( 'active' );

    setInterval( function () {
        $.post('/get_status')
        .done( function( response ) {
            $( '#lastupdate' ).text( Date() );
        });
    }, 5000);

});
