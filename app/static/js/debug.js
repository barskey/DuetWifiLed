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
            $( '#hotend-temp' ).text( response.hotend[0].toFixed(1) );
            $( '#hotend-target' ).text( response.hotend[1].toFixed(1) );
            $( '#hotend-percent' ).text( ( response.hotend[2] * 100 ).toFixed(1) );
            $( '#heatbed-temp' ).text( response.bed[0].toFixed(1) );
            $( '#heatbed-target' ).text( response.bed[1].toFixed(1) );
            $( '#heatbed-percent' ).text( ( response.bed[2] * 100 ).toFixed(1) );
            $( '#print-percent' ).text ( response.percent );
            updateTime();
        });
    }

    function refreshLog() {
        $.post( '/debug/get_log' )
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
        $.post( '/debug/status', {'type': $( '#status-type' ).val()} )
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
        $.post( '/debug/sim_mode', {'mode': $(this).prop('checked')} )
        .done( function( response ) {
            console.log( response.result );
        });
    });

    $( 'select.pdwn-sim,input.pdwn-sim' ).change( function() {
        //var status = $( this ).children( 'option:selected' ).val();
        $.post( '/debug/set_printer', $( '#sim-form' ).serialize() );
        refreshStatus();
    });

    $( 'select.pdwn-log' ).change( function() {
        var level = $( this ).children( 'option:selected' ).val();
        $.post( '/debug/set_loglevel', {loglevel: level} )
        .done( function( response ) {
            console.log( response.result );
        });
    });

});
