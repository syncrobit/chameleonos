$(document).ready(function(){
  var miner_height;
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
      $('.sb-serial').html("cham-" + data.serial_number);
      $('.fw-version').html(data.fw_version);
      $('.eth-mac').html(data.eth_mac);
      $('.wlan-mac').html(data.wlan_mac);
      $('.miner-address').html((data.address == null) ? 'N/A' : data.address);
      $('.temperature').html(data.temperature + " &deg;C");
      $('.uptime').html(convertime(data.uptime));
      $('.current-time').html(moment.unix(data.time).utc().format('YYYY-MM-DD H:m:s') + " UTC");

      //Stats
      $('.cpu-usage').html(data.cpu_usage + "%");
      $('.storage-usage').html(formatBytes(data.storage_used) + "/" + formatBytes(data.storage_total));
      $('.memory_usge').html(formatBytes(data.mem_used) + "/" + formatBytes(data.mem_total))
      $('.mem-per-used').html(((data.mem_used/data.mem_total) * 100).toFixed(2) + "%");
      $('.storage-per-used').html(((data.storage_used/data.storage_total) * 100).toFixed(2) + "%");
      
    }).done(function(){
      $.get( "/summary", function( data ) {
        $('.explorer-view').attr("href", "https://explorer.helium.com/hotspots/" + data.address);
        $('.miner-name').html((data.hotspot_name == null) ? 'N/A' : data.hotspot_name);
        $('.miner-region').html((data.region == null) ? 'N/A' : data.region);
        $('.concentrator-model').html((data.concentrator_model == null) ? 'N/A' :data.concentrator_model);
        $('.listen-addr').html((data.miner_listen_addr == null) ? 'N/A' : data.miner_listen_addr);
        $('.miner_height').html((data.miner_height == null) ? '0' : formatNumber(data.miner_height));
        $('.relayed').html((data.miner_listen_addr == null) ? 'N/A' : (/\/p2p/i.test(data.miner_listen_addr)) ? 'Yes' : 'No')
        miner_height = (data.miner_height === null) ? 0: data.miner_height;
      }).done(function(){
        $.get( "/stats", function( data ) {
          $('.chain-height').html(formatNumber(data.blockchain_height));
          $('.oracle-price').html(data.oracle_price + " USD");
          $('.monthly-earnings').html(data.rewards_30d + " HNT");
          $('.daily-earnings').html(data.rewards_1d + " HNT")
          $('.weekly-earnings').html(data.rewards_7d + " HNT");
          $('.is-sync').html((miner_height < (data.blockchain_height.replace(/,/g, '') - 250)) ? 'Out of Sync' : 'Synced');
          $('.difference').html(calculateDifference(data.rewards_7d, data.last_week) + '%');
        })
      });

    });

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
          $('#activity').html('<table class="table">' +
                              '<thead class="thead-dark">' +
                              '<tr>' +
                              '<th scope="col">Block</th>' +
                              '<th scope="col">Time</th>' +
                              '<th scope="col">Type</th>' +
                              '<th scope="col">Amount</th>' +
                              '</tr>' +
                              '</thead>' +
                              '<tbody>');
          $.each(data, function(index, element) {
            $('#activity').append('<tr>' +
                                  '<th scope="row">' + formatNumber(element.block) + '</th>' +
                                  '<td>' + moment.unix(element.time).utc().format('YYYY-MM-DD H:m:s') + ' UTC</td>' +
                                  '<td>' + element.type + '</td>' +
                                  '<td>' + formatNumber(element.amount) + ' HNT</td>' +
                                  '</tr>');               
            });
          
          $('#activity').append('</tbody>' +
                                '</table>');
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
