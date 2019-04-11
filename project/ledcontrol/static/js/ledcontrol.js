$( document ).ready( function() {
  
    feather.replace()

    $( '#led' ).addClass( 'active' );

    var actionDesc = [
        ['', '', ''],
        ['', '', ''],
        ['Ring shows selected color.', 'Color:', 'Not Used'],
        ['Ring will show percent complete as hotend temperature reaches target.', '% Complete:', 'Background:'],
        ['Ring will show percent complete as heatbed temperature reaches target.', '% Complete:', 'Background:'],
        ['Ring changes between two colors switching at specified interval.', 'Color 1:', 'Color 2:'],
        ['Ring fades gradually between two colors over specified interval.', 'Color 1:', 'Color 2:'],
        ['Chase color spins around ring completing one rotation in specified interval.', 'Chase:', 'Background:']
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

        //console.log(action < 5);
        if( action < 5 ) { // disable interval for these
            $modal.find( '#interval' ).val( '0' );
            $modal.find( '#interval' ).attr( 'readonly', true );
        } else {
            $modal.find( '#interval' ).attr( 'readonly', false );
        }
        if ( action == 2 ) { // disable second color for 2-solid
            $modal.find( '#color2' ).spectrum( 'disable' );
        } else {
            $modal.find( '#color2' ).spectrum( 'enable' );
        }

        $modal.find( '#color1' ).spectrum( 'set', params.color1 );
        $modal.find( '#color2' ).spectrum( 'set', params.color2 );
        $modal.find( '#interval' ).val( params.interval );
        $modal.modal( 'show' );
    }

    $( 'a.pdl-action' ).click( function() {
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

    $( 'select.pdl-action' ).change( function() {
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

    $( '#modalDone' ).click( function() {
        var $modal = $( '#paramModal' );
        if( ['5','6','7'].includes( $modal.find( '#action' ).val() ) && $modal.find( '#interval' ).val() == '' ) {
            $modal.find( '#interval' ).addClass( 'is-invalid' );
            return false;
        }
        console.log($modal.find('form').serialize());
        $.post( '/update_action', $modal.find('form').serialize() )
        .done( function( response ) {
            $( '#status' ).text( response.msg );
            console.log(response.msg);
        });
        $modal.modal( 'hide' );
    });

});