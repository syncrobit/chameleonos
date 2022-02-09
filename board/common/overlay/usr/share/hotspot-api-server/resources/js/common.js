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
                        number: true
                      },
                      inputRssiOffset: {
                        required: true,
                        number: true
                      },
                      inputTxPower:{
                        required: true, 
                        digits: true, 
                        min: 12,
                        max: 27  
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
                $('.modal-append').find('#powerSwitch').prop("checked", (data.led_ok_color != "off") ? true : false);
    
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
                var $switch = $('.modal-append').find('#wifiSwitch');
                $switch.prop("checked", data.external_wifi_antenna);
                
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
                                external_wifi_antenna: ($switch.is(':checked')) ? true : false
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
                
                $('.modal-append').find('#network-settings-form').validate({
                    rules: {
                        inputNatExt: {
                            digits: true
                        },
                        inputNatInt: {
                            digits: true
                        },
                    },
                    showErrors: formErrorDisplay,
                    submitHandler: function (ev) {
                      $('#network-settings-modal').modal('hide');
                        $.ajax({
                            type: 'PATCH',
                            url: '/config',
                            data: JSON.stringify({
                                nat_external_ip: $('.modal-append').find('#inputPublicIP').val(),
                                nat_external_port: $('.modal-append').find('#inputNatExt').val(),
                                nat_internal_port: $('.modal-append').find('#inputNatInt').val()
                            }),
                            processData: false,
                            contentType: 'application/merge-patch+json',
                            complete: function(xhr, statusText){
                                toastAppend('net-settings-not', 'Network settings succefully applied.');
                            }
                        }); 
                    }
                });

                $('.restore-network-settings').click(function(e){
                    e.preventDefault();
                    $('#network-settings-modal').modal('hide');
                    $.ajax({
                        type: 'PATCH',
                        url: '/config',
                        data: JSON.stringify({
                            nat_external_ip: null,
                            nat_external_port: null,
                            nat_internal_port: null
                        }),
                        processData: false,
                        contentType: 'application/merge-patch+json',
                        complete: function(xhr, statusText){
                            toastAppend('net-settings-not', 'Network settings default values applied.');
                        }
                    }); 
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
                                                           " kBytes/s <br><strong>Latency:</strong> " + data.latency + " ms<br>" +
                                                           "<strong>Public IP:</strong> " + data.public_ip + "<br>" +
                                                           "<strong>SB API Reachable:</strong> " + ((data.sb_api_reachable) ? "Yes" : "No") +
                                                           "<br><strong>Helium API Reachable:</strong> " + ((data.helium_api_reachable) ? "Yes" : "No"));
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
                $.post( "/factory_reset", function( data ) {});
                $('.modal-append #fab-reset-modal .modal-body')
                .html('<strong>Wiping Unit!</strong><br>' + 
                      'Unit will automatically reboot. If you are using wifi please use the app to re-configure wifi settings.');
            });
        }
    });

    //Logs
    $('.logs-show').click(function(e){
        e.preventDefault();
        var log = $(this).data('id');
        var html = getModal('logs');
        if(html !== undefined){
            $('.modal-append').html(html);

            $.get( "/logs/" + log, function( data ) {
                $( ".log-content" ).html( data );
                $('#logs-modal').modal('show').on('hidden.bs.modal', function () {
                    $('.modal').remove();
                });
            });
        }
    });

    //Remote Support
    $('.remote-support').click(function(e){
        e.preventDefault();
        var html = getModal('remote-support');
        if(html !== undefined){
            $('.modal-append').html(html);
            $.get( "/config", function( data ) {
                $('.modal-append').find('#remoteSwitch').prop("checked", data.remote_enabled);
                $('#remote-support-modal').modal('show').on('hidden.bs.modal', function () {
                    $('.modal').remove();
                });
                $('.modal-append').on('click', '#remoteSwitch', function(){
                    $('#remote-support-modal').modal('hide');
                    $switch = $(this);
                    $.ajax({
                        type: 'PATCH',
                        url: '/config',
                        data: JSON.stringify({
                            remote_enabled: ($switch.is(':checked')) ? true : false
                          
                        }),
                        processData: false,
                        contentType: 'application/merge-patch+json',
                        complete: function(xhr, statusText){
                            toastAppend('rs-settings-not', 'Remote support changes applied.');
                        }
                     });

                });
            });    
        }
    });

    //Check Firmware Update
    $.get( "/fwupdate", function( data ) {
        if(data.current !== data.latest){
            $('.firmware-update-wrapper').show();
        }else{
            $('.firmware-update-wrapper').hide();
        }
    });

    //Firmware Update button
    $('.update-firmware').click(function(e){
        e.preventDefault();
        var html = getModal('fw-update');
        if(html !== undefined){
            $('.modal-append').html(html);
            $('.modal-append').find('#fw-update-modal').modal({backdrop: 'static', keyboard: false})
            $('.modal-append').find('#fw-update-modal').modal('show'); 

            $.ajax({
                type: 'PATCH',
                url: '/fwupdate',
                processData: false,
                contentType: 'application/merge-patch+json',
                complete: function(xhr, statusText){}
             });

             setInterval(function(){ 
                $.get( "/fwupdate", function( data ) {
                    if(data.status == "idle"){
                        location.reload();
                    }else{
                        $('.modal-append').find('.fw-upd-status').html(data.status);
                    }
                    
                });
             }, 1000);
        }
    });

    //Miner Settings
    $('.miner-config').click(function(e){
        e.preventDefault();
        var html = getModal('miner-settings');
        if(html !== undefined){
            $.get("/config", function( data ) {
                $('.modal-append').html(html);
                $('.tooltip-show').tooltip('show');
                $('.modal-append').find('#disablesync').prop("checked", data.force_sync_enabled);
                $('.modal-append').find('#reboot-realy').prop("checked", data.panic_on_relayed);
                $('.modal-append').find('#reboot-unreachable').prop("checked", data.panic_on_unreachable);
                $('.modal-append').find('#periodic-reboot').prop("checked", data.periodic_reboot);
                $('.modal-append').find('#peer-reset').prop("checked", data.periodic_reset_peers);
                $('#miner-settings-modal').modal('show').on('hidden.bs.modal', function () {
                    $('.modal').remove();
                });

                //Disable Sync
                $('.modal-append').on('click', '#disablesync', function(){
                    $disableSwitch = $(this);
                    $.ajax({
                        type: 'PATCH',
                        url: '/config',
                        data: JSON.stringify({
                            force_sync_enabled: ($disableSwitch.is(':checked')) ? true : false
                        
                        }),
                        processData: false,
                        contentType: 'application/merge-patch+json',
                        complete: function(xhr, statusText){
                            toastAppend('is-settings-not', 'Instant sync settings applied.');
                        }
                    });
                });

                //Reboot Relay
                $('.modal-append').on('click', '#reboot-realy', function(){
                    $relaySwitch = $(this);
                    $.ajax({
                        type: 'PATCH',
                        url: '/config',
                        data: JSON.stringify({
                            panic_on_relayed: ($relaySwitch.is(':checked')) ? true : false
                        
                        }),
                        processData: false,
                        contentType: 'application/merge-patch+json',
                        complete: function(xhr, statusText){
                            toastAppend('rr-settings-not', 'Reboot relayed settings applied.');
                        }
                    });
                });

                //Reboot Unreachable
                $('.modal-append').on('click', '#reboot-unreachable', function(){
                    $unreachableSwitch = $(this);
                    $.ajax({
                        type: 'PATCH',
                        url: '/config',
                        data: JSON.stringify({
                            panic_on_unreachable: ($unreachableSwitch.is(':checked')) ? true : false
                        
                        }),
                        processData: false,
                        contentType: 'application/merge-patch+json',
                        complete: function(xhr, statusText){
                            toastAppend('ru-settings-not', 'Reboot unreachable settings applied.');
                        }
                    });
                });
            });

            //Periodic Reboot
            $('.modal-append').on('click', '#periodic-reboot', function(){
                $periodicReboot = $(this);
                $.ajax({
                    type: 'PATCH',
                    url: '/config',
                    data: JSON.stringify({
                        periodic_reboot: ($periodicReboot.is(':checked')) ? true : false
                    
                    }),
                    processData: false,
                    contentType: 'application/merge-patch+json',
                    complete: function(xhr, statusText){
                        toastAppend('pr-settings-not', 'Periodic reboot settings applied.');
                    }
                });
            });

            //Periodic Peer Reset
            $('.modal-append').on('click', '#peer-reset', function(){
                $periodicPeerReset = $(this);
                $.ajax({
                    type: 'PATCH',
                    url: '/config',
                    data: JSON.stringify({
                        periodic_reset_peers: ($periodicPeerReset.is(':checked')) ? true : false
                    
                    }),
                    processData: false,
                    contentType: 'application/merge-patch+json',
                    complete: function(xhr, statusText){
                        toastAppend('ppr-settings-not', 'Periodic peer reset settings applied.');
                    }
                });
            });
        }
    });

    //Help Modal
    $('.help-dialog').click(function(e){
        e.preventDefault();
        var html = getModal('help');
        if(html !== undefined){
            $.ajax({
                type: 'POST',
                url: '/sbapi/maker/',
                data: JSON.stringify({
                    action: 'getMakerHelp',
                    serial: os_prefix
                
                }),
                contentType : 'application/json',
                success: function(data){
                    data = JSON.parse(data);
                    $('.modal-append').html(html);
                    $('.troubleshoot-button').click(function(){
                        window.open(
                            data.maker.kb_link,
                            '_blank'
                          );
                    });

                    $('#help-modal').modal('show').on('hidden.bs.modal', function () {
                        $('.modal').remove();
                    });

                $('.send-ticket').click(function(e){
                    $('.main-step').hide();
                    $('.submit-ticket-body').toggle("slide", {direction: "down"}, 200);
                    $('.submit-ticket').show();
                });
                }
            }); 
        }
    });

    //Onboard Modal
    $('.onboard-unit').click(function(e){
        e.preventDefault();
        $('.onboard-spinner').show();
        var html = getModal('onboard');
        if(html !== undefined){
            var gw_address = getGwAddress();
            $.ajax({
                type: 'POST',
                url: '/sbapi/maker/',
                data: JSON.stringify({
                    action: 'checkOnboarded',
                    gw: gw_address
                
                }),
                contentType : 'application/json',
                success: function(data){
                    data = JSON.parse(data);
                    console.log(data)
                    $('.modal-append').html(html);
                    
                    if(!data.gw_status){
                        $('.view-explorer-m').attr("href", "https://explorer.helium.com/hotspots/" + gw_address);
                        $('.onboard-available').hide();
                        $('.onboard-wallet-cli').hide()
                        $('.onboard-unavailable').show();
                        $('.onboard-unit').hide();
                    }else{
                        $('.onboard-unavailable').hide();
                        $('.onboard-wallet-cli').hide();
                        $('.onboard-available').show();
                        $('.onboard-unit').show();
                        $('.inputPayer').val(data.maker.maker_address).prop('disabled', true);
                    }

                    $('#onboard-modal').modal('show').on('hidden.bs.modal', function () {
                        $('.modal').remove();
                    });
                    $('.onboard-spinner').hide();

                    $('.modal-append').find('#onboard-form').validate({
                        rules: {
                          inputOwner: {
                            required: true,
                          },
                        },
                        showErrors: formErrorDisplay,
                        submitHandler: function (ev) {
                          $.ajax({
                            type: 'POST',
                            url: '/txn/add_gateway',
                            data: JSON.stringify({
                              owner: $('.modal-append').find('#inputOwner').val(),
                              payer: $('.modal-append').find('#inputPayer').val()
                            }),
                            contentType: 'application/json',
                            success: function(data){
                                $('.onboard-unavailable').hide();
                                $('.onboard-available').hide();
                                $('.onboard-unit').hide();
                                
                                if(isBase64(data)){
                                    var qrcode = new QRCode(document.getElementById("onboard-qrcode"), {
                                        text: "helium://add_gateway/:" + data,
                                        width: 128,
                                        height: 128,
                                        colorDark : "#000000",
                                        colorLight : "#ffffff",
                                        correctLevel : QRCode.CorrectLevel.H
                                    });

                                    $('.onboard-success').val('helium-wallet --format json hotspots add --onboarding "' + gw_addr + '" "' + data + '" --commit');
                                }else{
                                    $('.onboard-success').val('Onboarding transaction failed, please try again later...');
                                }
                                
                                $('.onboard-wallet-cli').show();
                            }
                         });
                        }
                      });
                }
            });    
        }

    });

    $('.reset-pass').click(function(e){
        e.preventDefault();
        var html = getModal('reset-password');
        if(html !== undefined){
            $('.modal-append').html(html);
            $('#reset-pass-modal').modal('show').on('hidden.bs.modal', function () {
                $('.modal').remove();
            });

            $.post( "/reset_password", function( data ) {});

            $('.modal-append').find('#reset-pass-form').validate({
                rules: {
                    inputChallenge: {
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
                    $element = $('.modal-append').find('#inputChallenge');
                    $button = $('.modal-append').find('.re-save-password');
                    $.ajax({
                        url: "/reset_password",
                        method: "POST",
                        dataType: "json",
                        data: JSON.stringify({ code: $element.val(), password: $('.modal-append').find('#inputNewPass').val()}),
                        beforeSend: function(){
                            $button.prop('disabled', true);
                        },
                        complete: function(xhr, statusText){
                            if(xhr.status === 403){
                                $element.addClass('is-valid').removeClass('is-invalid');
                                setTimeout(function(){ $button.prop('disabled', false); }, 2000);
                            }else{
                                toastAppend('rp-changd-not', 'Pasword reset successful. Please login with your new password');
                            }
                        }
                    });
                }
              });
            
        }
    });

    //Troubleshoot
    $('.gw-troubleshoot').click(function(e){
        e.preventDefault();
        var html = getModal('troubleshoot');
        if(html !== undefined){
            $('.modal-append').html(html);
            $('#troubleshoot-modal').modal('show').on('hidden.bs.modal', function () {
                $('.modal').remove();
            });

            $.get("/troubleshoot", function(data) {
                $('.t-eth').html((data.hardware.ethernet_present) ? "Good" : "Not present");
                $('.t-dlspeed').html(data.network.download_speed + " kBytes/s");
                $('.t-region').html((data.miner.region_ok) ? "Selected" : "No Region");
                $('.t-wifi').html((data.hardware.wifi_present) ? "Good" : "Not Present");
                $('.t-latency').html(data.network.latency + " ms");
                $('.t-listening').html((data.miner.listening) ? "Yes" : "No");
                $('.t-ble').html((data.hardware.bluetooth_present) ? "Good" : "Not present");
                $('.t-sb-api').html((data.network.sb_api_reachable) ? "Reachable" : "Cannot be reached");
                $('.t-reachable').html((data.miner.reachable) ? "Yes" : "Cannot be reached");
                $('.t-concentrator').html((data.hardware.concentrator_present) ? "Present" : "Not Present");
                $('.t-helium-api').html((data.network.helium_api_reachable) ? "Reachable" : "Cannot be reached");
                $('.t-relayed').html((data.miner.direct) ? "No" : "Yes");
                $('.t-hnetwork').html((data.miner.ping) ? "Yes" : "No");
                $('.t-ecc').html((data.hardware.ecc_present) ? "Present" : "Absent");
                $('.t-eccprov').html((data.hardware.ecc_provisioned) ? "Yes" : "No");
            });   
        }
    });

    //Peer Book
    $('.peer-book').click(function(e){
        e.preventDefault();
        var html = getModal('peerbook');
        if(html !== undefined){
            $('.modal-append').html(html);
            $.get("/peers/book", function(data) {
                $.each( data, function( key, value ) {
                    $('.peerbook-content').append('<tr id="'+ value.address +'">' +
                                                '<th scope="row">' + value.name + '</th>' +
                                                '<td>' + value.local + '</td>' +
                                                '<td>' + value.remote + '</td>' +
                                                '<td>' + value.p2p + '</td>' +
                                                '<td><i class="fas fa-spinner fa-spin pairing-spinner"></i></td>' +
                                                '</tr>');                             
                });
            
                $('#peerbook-modal').modal('show').on('hidden.bs.modal', function () {
                    $('.modal').remove();
                });

                //Ping each Peer
                $.each( data, function( key, value ) {
                    $.get("/peers/ping?address=" + value.address, function(data) {
                        var peer_id = $('.peerbook-content').find('#' + value.address);
                        if(data.round_trip_time == null){
                            peer_id.css("background-color", "#ff3b30").css("color", "#ffff");
                        }else if(data.round_trip_time > 500){
                            peer_id.css("background-color", "#ff9500").css("color", "#ffff");
                        }else{
                            peer_id.css("background-color", "#1abd36").css("color", "#ffff");
                        }
                        peer_id.find('td:nth-child(5)').html((data.round_trip_time == null) ? "N/A" : data.round_trip_time + " ms").css("color", "#ffff");
                    });
                });
            }); 
        } 
    });

    $('.peer-config').click(function(e){
        e.preventDefault();
        var html = getModal('peer-settings');
        if(html !== undefined){
            $('.modal-append').html(html);

            $('.btn-ping-peer').click(function(){
                var address = $('#inputAddress');
                if(!$.trim(address.val()).length) { // zero-length string AFTER a trim
                    address.removeClass('is-valid').addClass('is-invalid');
                }else{
                    address.removeClass('is-invalid').addClass('is-valid');
                    $('.peer-pc').html('Pinging...');
                    $.get("/peers/ping?address=" + address.val(), function(data) {
                        var result;
                        if(data.round_trip_time == null){
                            result = '<span class="badge badge-danger">N/A</span>';
                        }else if(data.round_trip_time > 500){
                            result = '<span class="badge badge-warning">'+ data.round_trip_time +' ms</span>';
                        }else{
                            result = '<span class="badge badge-success">'+ data.round_trip_time +' ms</span>';
                        }
                        $('.peer-pc').html(result);
                    });
                }
                
            });

            $('.btn-connect-peer').click(function(){
                var address = $('#inputAddress');
                if(!$.trim(address.val()).length) { // zero-length string AFTER a trim
                    address.removeClass('is-valid').addClass('is-invalid');
                }else{
                    address.removeClass('is-invalid').addClass('is-valid');
                    $.get("/peers/connect?address=" + address.val(), function(data) {
                        var result;
                        if(data.success){
                            result = '<span class="badge badge-success">Added</span>';
                        }else{
                            result = '<span class="badge badge-danger">Could not be added</span>';
                        }
                        $('.peer-pc').html(result);
                    });

                }
            });

            $('.btn-reset-peerbook').click(function(){
                $.post("/peers/reset", function(data) {}).done(function() {
                    toastAppend('ppb-reset-not', 'PeerBook succssfully reset.');
                });
            });

            $('#peer-settings-modal').modal('show').on('hidden.bs.modal', function () {
                $('.modal').remove();
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

function isBase64(str) {
    var base64regex = /^([0-9a-zA-Z+/]{4})*(([0-9a-zA-Z+/]{2}==)|([0-9a-zA-Z+/]{3}=))?$/;
    return base64regex.test(str);
}

function getSummary(){

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
