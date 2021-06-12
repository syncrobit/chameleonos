$(document).ready(function(){
    $('.unit-reboot').click(function(e){
        e.preventDefault();
        modalAppend('reboot-modal', 'Reboot', 'Are you sure you want to reboot the unit?', 'Reboot', 'reboot-now');
        
    });

    $('.modal-append').on('click', '.reboot-now', function(){
        $.post( "/reboot", function( data ) {});
        $('.modal-append #reboot-modal .modal-body').html('<strong>Unit is rebooting!</strong><br>' + 
                                                          'Page will automatically refresh in <span id="reboot-timer">60</span> seconds.'
                                                          );
        $(this).prop("disabled", true);
        $('.close-modal').prop("disabled", true);
        $('.close').prop("disabled", true);
    
        var counter = 60;
        setInterval(function() {
            counter--;
            if (counter >= 0) {
                span = document.getElementById("reboot-timer");
                span.innerHTML = counter;
            }
            // Display 'counter' wherever you want to display it.
            if (counter === 0) {
                location.reload();
                clearInterval(counter);
            }
        }, 1000);
    });

    $('.force-resync').click(function(e){
        e.preventDefault();
        modalAppend('resync-modal', 'ReSync', 'Are you sure you want to resync the unit?', 'ReSync', 'resync-now');
    });

    $('.modal-append').on('click', '.resync-now', function(){
        $.post( "/resync", function( data ) {});
        $('.modal-append #resync-modal .modal-body').html('<strong>Unit is resyncing!</strong><br>' + 
                                                          'Your unit is currently resyncing please allow up to 30 minutes for the unit to finish resyncing'  +
                                                          '<br>You can now close this window.'
                                                          );
        $(this).prop("disabled", true);
    });

    $('.enable-pairing').click(function(e){
        $('.pairing-spinner').css("display", "inline-block");
        e.preventDefault();
        $.post( "/pair", function( data ) {}).done(function() {
            toastAppend('pairing-toast', 'Pairing mode enabled for 5 minutes');
            $('.pairing-spinner').css("display", "none");
          });
        
    });

    //Lora Settings 
    $('.lora-settings').click(function(e){
        e.preventDefault();
        var html = getModal('lora-settings');
        if(html !== undefined){
            $.get("/config", function( data ) {
                
                $('.modal-append').html(html);
                $('.modal-append').find('#inputAntennaGain').val(data.pf_antenna_gain);
                $('.modal-append').find('#inputRssiOffset').val(data.pf_rssi_offset);
                $('.modal-append').find('#inputTxPower').val(data.pf_tx_power);
                $('#lora-config-modal').modal('show').on('hidden.bs.modal', function () {
                    $('.modal').remove();
                });  
                
                $('.modal-append').find('#lora-settings-form').validate({
                    rules: {
                      inputAntennaGain: {
                        required: true,
                        digits: true
                      },
                      inputRssiOffset: {
                        required: true,
                        digits: true
                      },
                      inputTxPower:{
                        required: true, 
                        digits: true   
                      }
                    },
                    showErrors: formErrorDisplay,
                    submitHandler: function (ev) {
                      $('#lora-config-modal').modal('hide');
                      $.ajax({
                        type: 'PATCH',
                        url: '/config',
                        data: JSON.stringify({
                          pf_antenna_gain: $('.modal-append').find('#inputAntennaGain').val(),
                          pf_rssi_offset: $('.modal-append').find('#inputRssiOffset').val(),
                          pf_tx_power: $('.modal-append').find('#inputTxPower').val()
                        }),
                        processData: false,
                        contentType: 'application/merge-patch+json',
                        complete: function(xhr, statusText){
                            toastAppend('lora-settings-not', 'Lora Settings successfully applied');
                            $('.modal').remove();
                        }
                     });
                    }
                  });

                  $('.modal-append').find('.restore-default-lora').click(function(e){
                        e.preventDefault()
                        $('#lora-config-modal').modal('hide');
                        $.ajax({
                            type: 'PATCH',
                            url: '/config',
                            data: JSON.stringify({
                              pf_antenna_gain: null,
                              pf_rssi_offset: null,
                              pf_tx_power: null
                            }),
                            processData: false,
                            contentType: 'application/merge-patch+json',
                            complete: function(xhr, statusText){
                                toastAppend('lora-settings-not', 'Lora Settings default values applied.');
                                $('.modal').remove();
                            }
                         });
                  });
            });
        }
    });

    //Led Settings
    $('.led-settings').click(function(e){
        e.preventDefault();
        var html = getModal('led-settings');
        if(html !== undefined){
            $.get("/config", function( data ) {
                $('.modal-append').html(html);
               
                if(data.led_ok_color != "off"){
                    $('.modal-append').find('#powerSwitch').prop("checked", true);
                }else{
                    $('.modal-append').find('#powerSwitch').prop("checked", false);
                }

                $('.modal-append').on("click", "#powerSwitch", function(){
                    $switch = $(this);
                    $.ajax({
                        type: 'PATCH',
                        url: '/config',
                        data: JSON.stringify({
                            led_ok_color: ($switch.is(':checked')) ? "green" : "off"
                          
                        }),
                        processData: false,
                        contentType: 'application/merge-patch+json',
                        complete: function(xhr, statusText){}
                     });
                });

                $('#led-settings-modal').modal('show').on('hidden.bs.modal', function () {
                    $('.modal').remove();
                });   
                console.log(data);
                $('.modal-append').find('#inputBrightness')
                    .attr('data-slider-value', data.led_brightness)
                    .bootstrapSlider().on('slideStop', function(ev) { 
                    $.ajax({
                        type: 'PATCH',
                        url: '/config',
                        data: JSON.stringify({
                            led_brightness: ev.value
                        }),
                        processData: false,
                        contentType: 'application/merge-patch+json',
                        complete: function(xhr, statusText){}
                    }); 
                });
                
                $('.modal-append').on("click", '.btn-led', function(e){
                    e.preventDefault();
                    $btn = $(this);
                    $.ajax({
                        type: 'PATCH',
                        url: '/config',
                        data: JSON.stringify({
                            led_ok_color: $btn.val()
                        }),
                        processData: false,
                        contentType: 'application/merge-patch+json',
                        complete: function(xhr, statusText){}
                    }); 
                });

                $('.modal-append').on('click', '.restore-led-default', function(e){
                    $('#led-settings-modal').modal('hide');
                    e.preventDefault();
                    $.ajax({
                        type: 'PATCH',
                        url: '/config',
                        data: JSON.stringify({
                            led_ok_color: null,
                            led_brightness: null
                        }),
                        processData: false,
                        contentType: 'application/merge-patch+json',
                        complete: function(xhr, statusText){
                            toastAppend('led-settings-not', 'LED Settings default values applied.');
                            $('.modal').remove();
                        }
                    }); 
                });
            });
        }
    });

    //System Settings
    $('.sys-config').click(function(e){
        e.preventDefault();
        var html = getModal('sys-settings');
        if(html !== undefined){
            $.get("/config", function( data ) {
                $('.modal-append').html(html);
                $('.modal-append').find('#inputCPUFreq').val(data.cpu_freq_max);
                $('#sys-settings-modal').modal('show').on('hidden.bs.modal', function () {
                    $('.modal').remove();
                });   

                $('.modal-append').find('#sys-settings-form').validate({
                    rules: {
                        inputCPUFreq: {
                            required: true,
                            digits: true
                      },
                    },
                    showErrors: formErrorDisplay,
                    submitHandler: function (ev) {
                      $('#sys-settings-modal').modal('hide');
                        $.ajax({
                            type: 'PATCH',
                            url: '/config',
                            data: JSON.stringify({
                                cpu_freq_max: $('.modal-append').find('#inputCPUFreq').val(),
                            }),
                            processData: false,
                            contentType: 'application/merge-patch+json',
                            complete: function(xhr, statusText){
                                toastAppend('sys-settings-not', 'System settings succefully applied.');
                            }
                        }); 
                    }
                });

                $('.modal-append').on('click', '.sys-restore-defaults', function(){
                    $.ajax({
                        type: 'PATCH',
                        url: '/config',
                        data: JSON.stringify({
                            cpu_freq_max: null,
                        }),
                        processData: false,
                        contentType: 'application/merge-patch+json',
                        complete: function(xhr, statusText){
                            toastAppend('sys-settings-not', 'System settings default values applied.');
                            $('#sys-settings-modal').modal('hide');
                        }
                    }); 
                });

            });
        }
    });

    //Network Settings
    $('.network-config').click(function(e){
        e.preventDefault();
        var html = getModal('network-settings');
        if(html !== undefined){
            $.get("/config", function( data ) {
                $('.modal-append').html(html);
                $('.modal-append').find('#inputPublicIP').val(data.nat_external_ip);
                $('.modal-append').find('#inputNatExt').val(data.nat_external_port);
                $('.modal-append').find('#inputNatInt').val(data.nat_internal_port);
                $('#network-settings-modal').modal('show').on('hidden.bs.modal', function () {
                    $('.modal').remove();
                }); 
                
                
            });
        }
    });

    //Change Password
    $('.change-pass').click(function(e){
        e.preventDefault();
        var html = getModal('change-pass');
        if(html !== undefined){
            $('.modal-append').html(html);
            $('#change-pass-modal').modal('show').on('hidden.bs.modal', function () {
                $('.modal').remove();
            });
        }
        
        $('.modal-append').on( "blur", "#inputCurrentPass", function(){
            $element = $('.modal-append').find('#inputCurrentPass');
            $button = $('.modal-append').find('.save-password')
            $.ajax({
                url: "/verify_password",
                method: "POST",
                dataType: "json",
                data: JSON.stringify({ password: $element.val()}),
                complete: function(xhr, statusText){
                  if(xhr.status === 204){
                    $element.addClass('is-valid').removeClass('is-invalid');
                    $button.prop('disabled', false);
                  }else{
                    $element.addClass('is-invalid').removeClass('is-valid');
                    $button.prop('disabled', true);
                  }
                }
            });
        });

        $('.modal-append').find('#change-pass-form').validate({
            rules: {
              inputCurrentPass: {
                required: true,
              },
              inputNewPass: {
                required: true,
                minlength: 8,
                notEqual: "admin"
              },
              inputRNewPass:{
                required: true, 
                equalTo: '#inputNewPass'   
              }
            },
            showErrors: formErrorDisplay,
            submitHandler: function (ev) {
              $.ajax({
                type: 'PATCH',
                url: '/config',
                data: JSON.stringify({
                  password: $('.modal-append').find('#inputNewPass').val(),
                  old_password: $('.modal-append').find('#inputCurrentPass').val()
                }),
                processData: false,
                contentType: 'application/merge-patch+json',
                complete: function(xhr, statusText){
                  location.reload();
                }
             });
            }
          });
    });



    //Speed Test
    $('.modal-append').on("click", ".speed-test", function(){
        $('.modal-append').find('.speed-results').html('');
        $('.modal-append').find('.progress').css("display", "flex");
        $('.modal-append').find('.progress-bar').animate({ width: '100%'}, 5000);
        $.get("/nettest", function( data ) {
            $('.modal-append').find('.progress').css("display", "none");
            $('.modal-append').find('.speed-results').html("<strong>Download speed:</strong> " + data.download_speed + 
                                                           " kBytes/s <br><strong>Latency:</strong> " + data.latency + " ms");
            $('.modal-append').find('.progress-bar').animate({ width: '0%'});  
        });
    })

    //Factory Reset
    $('.facotry-reset').click(function(e){
        e.preventDefault();
        var html = getModal('factory-reset');
        if(html !== undefined){
            $('.modal-append').html(html);
            $('#fab-reset-modal').modal('show').on('hidden.bs.modal', function () {
                $('.modal').remove();
            });

            $('.fab-reset').click(function(){
                $.post( "/factory-reset", function( data ) {});
                $('.modal-append #fab-reset-modal .modal-body')
                .html('<strong>Wiping Unit!</strong><br>' + 
                      'Unit will automatically reboot. If you are using wifi please use the app to re-configure wifi settings.');
            });
        }
    });
});

function getModal(modalName){
    var result = null;
    
     $.ajax({
        url: "modals/" + modalName,
        type: 'get',
        dataType: 'html',
        async: false,
        success: function(data) {
            result = data;
        } 
     });
     return result;
}

function toastAppend(id, body){
    $('.toasts-container').html('<div class="toast" id="'+ id +'" data-autohide="true">' +
                                '<div class="toast-header">' +
                                '<i class="far fa-bell text-muted mr-2"></i>' +
                                '<strong class="mr-auto">Notification</strong>' +
                                '<button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">' +
                                '<span>×</span>' +
                                '</button>' +
                                '</div>' +
                                '<div class="toast-body">' + body + '</div>' +
                                '</div>');
    $('#' + id).toast({ delay: 3000 }).toast('show').on('hidden.bs.toast', function () {
        $(this).remove();
      });
}

function modalAppend(id, title, body, buttonText, buttonAction){
    $('.modal-append').html('<div class="modal fade show" id="'+ id +'" aria-modal="true" style="padding-right: 15px;">' +
                      '<div class="modal-dialog">' +
                      '<div class="modal-content">' +
                      '<div class="modal-header">' +
                      '<h5 class="modal-title">'+ title +'</h5>' +
                      '<button type="button" class="close" data-dismiss="modal">' +
                      '<span>×</span>' +
                      '</button>' +
                      '</div>' +
                      '<div class="modal-body">' + body + '</div>' +
                      '<div class="modal-footer">' +
                      '<button type="button" class="btn btn-default close-modal" data-dismiss="modal">Close</button>' +
                      '<button type="button" class="btn btn-primary ' + buttonAction + '">' + buttonText +'</button>' +
                      '</div>' +
                      '</div>' +
                      '</div>' +
                      '</div>');
    $('#' + id).modal('show').on('hidden.bs.modal', function () {
        $('.modal').remove();
    });               
}

jQuery.validator.addMethod("notEqual", function(value, element, param) {
    return this.optional(element) || value != $(param).val();
   }, "This has to be different...");

function formErrorDisplay(errorMap, errorList){
    
	// Clean up any tooltips for valid elements
	$.each(this.validElements(), function (index, element) {
	  var $element = $(element);
	  $element.removeClass("is-invalid");
  });

  // Create new tooltips for invalid elements
  $.each(errorList, function (index, error) {
	  var $element = $(error.element);
	  $element.addClass("is-invalid");
  });
}

Pace.on("done", function(){
    $('.preloader').fadeOut('slow');
});
