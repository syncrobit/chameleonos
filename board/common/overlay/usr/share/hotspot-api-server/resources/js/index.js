var miner_height, gw_addr, os_prefix;
$(document).ready(function(){
  
    //Check if Password is default
    $.ajax({
      url: "/verify_password",
      method: "POST",
      dataType: "json",
      data: JSON.stringify({ password: "admin"}),
      complete: function(xhr, statusText){
        if(xhr.status === 204){
          var html = getModal('change-default');
          if(html !== undefined){
            $('.modal-append').html(html);
            $('.modal-append').find('#change-default-modal').modal({backdrop: 'static', keyboard: false})
            $('.modal-append').find('#change-default-modal').modal('show'); 

            $('.modal-append').find('#change-default-form').validate({
              rules: {
                inputNewPass: {
                  required: true,
                  minlength: 8
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
                    old_password: 'admin'
                  }),
                  processData: false,
                  contentType: 'application/merge-patch+json',
                  complete: function(xhr, statusText){
                    location.reload();
                  }
               });
              }
            });

          } 
        }
      }
    });

    //Quick Summary
    $.get( "/summary?quick=true", function( data ) {
      gw_addr = data.address
      os_prefix = data.os_prefix
      $('.sb-serial').html(os_prefix +"-"+ data.serial_number);
      $('.fw-version').html(data.fw_version);
      $('.eth-mac').html(data.eth_mac);
      $('.wlan-mac').html(data.wlan_mac);
      $('.miner-address').html((gw_addr == null) ? 'N/A' : gw_addr);
      $('.temperature').html(data.temperature + " &deg;C");
      $('.uptime').html(convertime(data.uptime));
      $('.current-time').html(moment.unix(data.time).utc().format('YYYY-MM-DD H:m:s') + " UTC");
      
      //Get Logo
      $.ajax({
        url:'resources/img/' + os_prefix + '_logo.png',
        type:'HEAD',
        success:function(){
          $('.brand-logo').html('<img src="resources/img/' + os_prefix + '_logo.png" alt="" height="20">' +
                                '<span class="sb-slogan">Powered By SyncroB.it</span>')
        },
        error: function(){
          $('.brand-logo').html('<span class="sb-logo">SyncroB.it</span>');
        }
      });
      
      //Last Panic
      if(data.last_panic != null){
        $('.gw-notifications').html('<a href="javascript:void(0);" class="dropdown-notification-item">' +
                               '<div class="dropdown-notification-icon">' +
                               '<i class="fa fa-exclamation-triangle fa-lg fa-fw text-warning"></i>' +
                               '</div>' +
                               '<div class="dropdown-notification-info">' +
                               '<div class="title panic-title"> ' +
                               '<strong>Service: </strong>' + data.last_panic.service + '<br> <strong>Message: </strong>' + data.last_panic.message + '</div>' +
                               '<div class="time panic-time">' + timeSince(data.last_panic.timestamp) + ' ago' +'</div>' +
                               '</div>' +
                               '</a>');
        if(timeSince(data.last_panic.timestamp) < 2){
          $('.gw-label').show();
        }                         
      }else{
        $('.gw-notifications').html('<a href="javascript:void(0);" class="dropdown-notification-item">' +
                                    '<div class="dropdown-notification-info">' +
                                    '<div class="title panic-title" style="text-align:center;"> No new notifications...</div>' +
                                    '</div>' +
                                    '</a>');
        $('.gw-label').hide();
      }


      //Stats
      var storage_percent = ((data.storage_used/data.storage_total) * 100).toFixed(2) + "%";
      var mem_percent = (((data.mem_used + data.swap_used)/(data.mem_total + data.swap_total)) * 100).toFixed(2) + "%";
      $('.cpu-usage').html(data.cpu_usage + "%");
      $('.cpu-progress').css('width', data.cpu_usage + "%");
      $('.storage-usage').html(formatBytes(data.storage_used) + "/" + formatBytes(data.storage_total));
      $('.storage-progress').css('width', storage_percent);
      $('.storage-per-used').html(storage_percent);
      $('.memory_usge').html(formatBytes(data.mem_used + data.swap_used) + "/" + formatBytes(data.mem_total + data.swap_total))
      $('.mem-per-used').html(mem_percent);
      $('.mem-progress').css('width', mem_percent);
      
      
    }).done(function(){
      $.get( "/summary", function( data ) {
        $('.explorer-view').attr("href", "https://explorer.helium.com/hotspots/" + data.address);
        $('.miner-name').html((data.hotspot_name == null) ? 'N/A' : data.hotspot_name);
        $('.miner-region').html((data.region == null) ? 'N/A' : data.region);
        $('.concentrator-model').html((data.concentrator_model == null) ? 'N/A' : data.concentrator_model);
        $('.listen-addr').html((data.miner_listen_addr == null) ? 'N/A' : data.miner_listen_addr);
        $('.miner_height').html((data.miner_height == null) ? '0' : formatNumber(data.miner_height));
        $('.relayed').html((data.miner_listen_addr == null) ? 'N/A' : (/\/p2p/i.test(data.miner_listen_addr)) ? 'Yes' : 'No')
        $('.listener-ok').html((data.miner_listen_ok == true) ? 'Yes' : (data.miner_listen_ok == false) ? 'Forwarding/NAT issue' : 'Relayed/Timedout');
        miner_height = (data.miner_height === null) ? 0: data.miner_height;
      }).done(function(){
        $.get( "/stats", function( data ) {
          $('.chain-height').html(formatNumber(data.blockchain_height));
          $('.oracle-price').html(data.oracle_price + " USD");
          $('.monthly-earnings').html(data.rewards_30d + " HNT");
          $('.daily-earnings').html(data.rewards_1d + " HNT")
          $('.weekly-earnings').html(data.rewards_7d + " HNT");
          $('.is-sync').html(((miner_height < (data.api_height.replace(/,/g, '') - 250)) ? 'Out of Sync' : 'Synced') + ' (' + ((miner_height / data.api_height.replace(/,/g, '')) * 100).toFixed(2) + "%)");
          $('.etl-is-sync').html(((data.blockchain_height < (data.api_height.replace(/,/g, '') - 250)) ? 'Out of Sync' : 'Synced') + ' (' + ((data.blockchain_height.replace(/,/g, '') / data.api_height.replace(/,/g, '')) * 100).toFixed(2) + "%)");
          $('.difference').html(calculateDifference(data.rewards_7d, data.last_week) + '%');
        })
      });

    });

    //Live stats
    setInterval(function(){ 
      $.get( "/summary?quick=true", function( data ) {
        var mem_percent = (((data.mem_used + data.swap_used)/(data.mem_total + data.swap_total)) * 100).toFixed(2) + "%";
        $('.cpu-usage').html(data.cpu_usage + "%");
        $('.cpu-progress').css('width', data.cpu_usage + "%");
        $('.memory_usge').html(formatBytes(data.mem_used + data.swap_used) + "/" + formatBytes(data.mem_total + data.swap_total))
        $('.mem-per-used').html(mem_percent);
        $('.mem-progress').css('width', mem_percent);
        $('.gw-status').removeClass('gw_lora_ready gw_power_up gw_ip_ready gw_miner_syncing gw_updating_firmware gw_no_net gw_panic gw_rebooting')
        .addClass('gw_' + data.current_state);
      });

      //Check NetConnection
      $.get( "/nettest?latency=true", function( data ) {
        if(data.latency === null){
          $('.network-activity-wrapper').show();
        }else{
          $('.network-activity-wrapper').hide();
        }
      });
    }, 5000);

    $('.refresh-summary').click(function(e){
      e.preventDefault();
        
      var button = $('.refresh-icon');
      button.addClass('fa-spin');
      $.get( "/summary", function( data ) {
        $('.miner-name').html((data.hotspot_name == null) ? 'N/A' : data.hotspot_name);
        $('.miner-region').html((data.region == null) ? 'N/A' : data.region);
        $('.concentrator-model').html((data.concentrator_model == null) ? 'N/A' :data.concentrator_model);
        $('.listen-addr').html((data.miner_listen_addr == null) ? 'N/A' : data.miner_listen_addr);
        $('.current-time').html(moment.unix(data.time).utc().format('YYYY-MM-DD H:m:s') + " UTC");
        $('.relayed').html((data.miner_listen_addr == null) ? 'N/A' : (/\/p2p/i.test(data.miner_listen_addr)) ? 'Yes' : 'No')
        button.removeClass('fa-spin');
      });
    });

    //Activity
    function getActivity(){
      $.get( "/activity", function( data ) {
        if(Object.keys(data).length > 0){
          $('#activity').html('<table class="table" id="activity_tbl">' +
                              '<thead class="thead-dark">' +
                              '<tr>' +
                              '<th scope="col">Block</th>' +
                              '<th scope="col">Time</th>' +
                              '<th scope="col">Type</th>' +
                              '<th scope="col">Amount</th>' +
                              '</tr>' +
                              '</thead>' +
                              '<tbody></tbody>' +
                              '</table>');
          $.each(data, function(index, element) {
            $('#activity').find("#activity_tbl tbody").append('<tr>' +
                                  '<th scope="row">' + formatNumber(element.block) + '</th>' +
                                  '<td>' + moment.unix(element.time).utc().format('YYYY-MM-DD H:m:s') + ' UTC</td>' +
                                  '<td><span class="badge badge-primary">' + element.type + '</span></td>' +
                                  '<td>' + element.amount + ' HNT</td>' +
                                  '</tr>');               
            });
        }
      });
    }

    getActivity();

    $('.refresh-activity').click(function(e){
      e.preventDefault();
      $('.activity-icon').addClass('fa-spin');
      setTimeout(function() {
        $('.activity-icon').removeClass("fa-spin");
      }, 800);
      getActivity();
    });
    
});

function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatNumber(num) {
  return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
}

function calculateDifference(now, lastweek){
  
  var percent = (((now-lastweek)/now) * 100.0).toFixed(2);
  percent     = +percent || 0
  var icon    = (now > lastweek) ? '<i class="fa fa-caret-up"></i>' : '<i class="fa fa-caret-down"></i>';
  
  return icon + '<b>' + percent + '</b>';
}

function getGwAddress(){
  return gw_addr;
}

function convertime(time) {
  var sec_num = parseInt(time, 10); // don't forget the second param
  var days    = Math.floor(sec_num / 86400);
  var hours   = Math.floor(sec_num / 3600);
  var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
  var seconds = sec_num - (hours * 3600) - (minutes * 60);
    
  if (days    < 10) {days    = "0"+days;}
  if (hours   < 10) {hours   = "0"+hours;}
  if (minutes < 10) {minutes = "0"+minutes;}
  if (seconds < 10) {seconds = "0"+seconds;}
  var time    = days+" days " +hours+':'+minutes+':'+seconds;
  return time;
}

function timeSince(date) {
  date = new Date(date * 1000);
  var seconds = Math.floor((new Date() - date) / 1000);
  var interval = seconds / 31536000;

  if (interval > 1) {
    return Math.floor(interval) + " years";
  }
  interval = seconds / 2592000;
  if (interval > 1) {
    return Math.floor(interval) + " months";
  }
  interval = seconds / 86400;
  if (interval > 1) {
    return Math.floor(interval) + " days";
  }
  interval = seconds / 3600;
  if (interval > 1) {
    return Math.floor(interval) + " hours";
  }
  interval = seconds / 60;
  if (interval > 1) {
    return Math.floor(interval) + " minutes";
  }
  return Math.floor(seconds) + " seconds";
}