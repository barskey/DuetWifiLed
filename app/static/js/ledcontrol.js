$( document ).ready( function() {
  
    feather.replace()

    $( '#led' ).addClass( 'active' );

    var actionDesc = [
        ['', '', ''],
        ['', '', ''],
        ['Ring shows selected color.', 'Color:', 'Not Used'],
        ['Ring will show percent complete as hotend temperature reaches target.', '% Complete:', 'Background:'],
        ['Ring will show percent complete as heatbed temperature reaches target.', '% Complete:', 'Background:'],
        ['Ring will show percentage of print complete.', '% Complete:', 'Background:'],
        ['Ring changes between two colors switching at specified interval.', 'Color 1:', 'Color 2:'],
        ['Ring fades gradually between two colors over specified interval.', 'Color 1:', 'Color 2:'],
        ['Chase color spins around ring completing one rotation in specified interval.', 'Chase:', 'Background:'],
        ['It\'s a double rainbow!!!', 'Not Used:', 'Not Used:']
    ]

    $( '#color1, #color2' ).spectrum({
        showPaletteOnly: true,
        togglePaletteOnly: true,
        togglePaleteMoreText: 'more',
        togglePaleteLessText: 'less',
        hideAfterPaletteSelect: true,
        preferredFormat: 'rgb',
        color: '#000000',
        palette: [
            ['#fff', '#f00', '#f90', '#ff0'],
            ['#888', '#0f0', '#090', '#0ff'],
            ['#000', '#00f', '#90f', '#f0f']
        ]
    });

    function showActionModal( action, ring, evnt, params ) {
        var $modal = $( '#paramModal' );
        $modal.find( '#interval' ).removeClass( 'is-invalid' );
        $modal.find( '#action-desc' ).text( actionDesc[action][0] );
        $modal.find( '#action-color1label' ).text( actionDesc[action][1] );
        $modal.find( '#action-color2label' ).text( actionDesc[action][2] );
        $modal.find( '#ring' ).val( ring );
        $modal.find( '#event' ).val( evnt );
        $modal.find( '#action' ).val( action );
        $modal.find( '#modal-note' ).removeClass( 'd-none' );

        //console.log(action < 5);
        if( action < 6 ) { // disable interval for these
            $modal.find( '#interval' ).val( '0' );
            $modal.find( '#interval' ).attr( 'readonly', true );
        } else {
            $modal.find( '#interval' ).attr( 'readonly', false );
        }
        if ( action == 2 ) { // disable second color for 2-solid
            $modal.find( '#color1' ).spectrum( 'enable' );
            $modal.find( '#color2' ).spectrum( 'disable' );
        } else if ( action == 9 ) { // disable both colors for 9-rainbow
            $modal.find( '#color1,#color2' ).spectrum( 'disable' );
            $modal.find( '#modal-note' ).addClass( 'd-none' );
        } else {
            $modal.find( '#color1,#color2' ).spectrum( 'enable' );
        }

        $modal.find( '#color1' ).spectrum( 'set', params.color1 );
        $modal.find( '#color2' ).spectrum( 'set', params.color2 );
        $modal.find( '#interval' ).val( params.interval );

        $.post( '/led-stop-ring', {ring: ring} )
        .done( function( response ) {
            $( '#status' ).text( response.msg );
            console.log(response.msg);
        });

        $modal.modal( 'show' );
    }

    $( 'a.pdwn-action' ).click( function() {
        var action = $( this ).parent().parent().find( 'select option:selected' ).val();
        var ring = $( this ).attr( 'id' ).split( '-' )[1];
        var evnt = $( this ).attr( 'id' ).split( '-' )[2];
        //console.log(action, ring, evnt);
        if ( action > 1 ) {
            $.post( '/get_action_params', {'ring': ring, 'event': evnt} )
            .done( function( response ) {
                showActionModal( action, ring, evnt, response.params );
            })
            .fail( function (xhr, status, err) {
                $( '#status' ).text( err )
            });
        }
    });

    $( 'select.pdwn-action' ).change( function() {
        var action = $( this ).children( 'option:selected' ).val();
        var ring = $( this ).attr( 'id' ).split( '-' )[1];
        var evnt = $( this ).attr( 'id' ).split( '-' )[2];
        //console.log(action, ring, evnt);
        if ( action > 1 ) {
            $.post( '/get_action_params', {'ring': ring, 'event': evnt} )
            .done( function( response ) {
                showActionModal( action, ring, evnt, response.params );
            });
        }
    });

    $( '.pdwn-modal' ).change( function() {
        var $modal = $( '#paramModal' );
        // actions 6,7,8,9 need interval, hence can't be blank
        if( ['6','7','8','9'].includes( $modal.find( '#action' ).val() ) &&
        ($modal.find( '#interval' ).val() == ''  || $modal.find( '#interval' ).val() == '0')) {
            $modal.find( '#interval' ).addClass( 'is-invalid' );
            return false;
        }
        //console.log($modal.find('form').serialize());
        // update the params and start test event
        var params = $modal.find( 'form' ).serialize();
        $.post( '/led-change-event', params )
        .done( function( response ) {
            $( '#status' ).text( response.msg );
            console.log(response.msg);
        });
    });

    $( '#paramModal' ).on( 'hide.bs.modal', function(e) {
        var $modal = $( '#paramModal' );
        // actions 6,7,8,9 need interval, hence can't be blank
        if( ['6','7','8','9'].includes( $modal.find( '#action' ).val() ) &&
        ($modal.find( '#interval' ).val() == ''  || $modal.find( '#interval' ).val() == '0')) {
            $modal.find( '#interval' ).addClass( 'is-invalid' );
            return false;
        }
        $modal.modal( 'hide' );
    });

});
