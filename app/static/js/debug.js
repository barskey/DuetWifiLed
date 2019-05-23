$( document ).ready( function() {
  
    $( '#debug' ).addClass( 'active' );

    function updateTime() {
        var today = new Date();
        $( '#lastupdate' ).text( today.toLocaleString() );
    }

    function refreshStatus() {
        $.post( '/get_status' )
        .done( function( response ) {
            $( '#status' ).val( response.status );
            $( '#printer-state' ).text( response.state );
            $( '#hotend-temp' ).text( response.hotend[0] );
            $( '#hotend-target' ).text( response.hotend[1] );
            $( '#hotend-percent' ).text( response.hotend[2] );
            $( '#heatbed-temp' ).text( response.bed[0] );
            $( '#heatbed-target' ).text( response.bed[1] );
            $( '#heatbed-percent' ).text( response.bed[2] );
            $( '#print-percent' ).text ( response.percent );
            updateTime();
        });
    }

    function refreshLog() {
        $.post( '/get_log' )
        .done( function( response ) {
            $( '#log' ).val( response.log );
            updateTime();
        });
    }

    // refresh status on page load
    refreshStatus();
    refreshLog();

    $( '#refresh-printer' ).click( function() {
        refreshStatus();
    });

    $( '#refresh-log' ).click( function() {
        refreshLog();
    });

    $( '#get-status' ).click( function() {
        $.post( '/debug_status', {'type': $( '#status-type' ).val()} )
        .done( function( response ) {
            $( '#status' ).val( response.status );
        })
    });
    
    $( '#sim-mode-toggle' ).change( function () {
        if ($(this).prop('checked')) {
            $( '#sim-mode-alert' ).removeClass( 'd-none' );
        } else {
            $( '#sim-mode-alert' ).addClass( 'd-none' );
        }
        $.post( '/debug_sim_mode', {'mode': $(this).prop('checked')} );
    });

    $( 'select.pdwn-sim' ).change( function() {
        var status = $( this ).children( 'option:selected' ).val();
        $.post( '/debug_set_printer', $( '#sim-form' ).serialize() );
        refreshStatus();
    });

    $( 'input.pdwn-sim' ).change( function() {
        $.post( '/debug_set_printer', $( '#sim-form' ).serialize() );
        refreshStatus();
    });

});
