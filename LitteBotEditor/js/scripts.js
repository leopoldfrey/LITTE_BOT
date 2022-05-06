var sentencesData;
var $sentences = $("#sentences");
var modalSentence = $('#modalSentence');
var modalAdmin = $('#modalAdmin');
var newSentence = $('#newSentence');
var newAnswer = $('#newAnswer');
var stateBut = $("#socketState");
var oldQ = "";
var sentences = new Array();
var mod = false;
var cat = "common";
var currRow;
var editing = false;

function sel(o) {
  currRow.removeClass("selected");
  currRow = o;
  currRow.addClass("selected");
  $("html, body").animate({ scrollTop: currRow.position.top });
}

function change(o) {
  if(o.html().includes("span"))
    o.html("");
  else
    o.html("<span class='icon-check'>");
}

function set(o) {
  o.html("<span class='icon-check'>");
}

function clear(o) {
  o.html("");
}

function load()
{
  urlFill = ""
  switch(cat)
  {
    default:
    case "common":
      urlFill = "/getCommon";
      history.pushState({}, null, "index.html?cat=common");
      break;
    case "seduction":
      urlFill = "/getSeduction";
      history.pushState({}, null, "index.html?cat=seduction");
      break;
    case "provocation":
      urlFill = "/getProvocation";
      history.pushState({}, null, "index.html?cat=provocation");
      break;
    case "fuite":
      urlFill = "/getFuite";
      history.pushState({}, null, "index.html?cat=fuite");
      break;
    case "epilogue":
      urlFill = "/getEpilogue";
      history.pushState({}, null, "index.html?cat=epilogue");
      break;
  }
  $.ajax({
      url: urlFill,
      type: "GET",
      success: function(response) {
          fillSentences(response);
          $("html, body").animate({ scrollTop: 0 });
      },
      error: function(jqXHR, textStatus, errorMessage) {
          console.log(errorMessage); // Optional
      }
  });
}

function fillSentences(data) {
  $sentences.empty();
  sentencesData = data;
  len = Object.keys(sentencesData).length;
  // console.log("Length", len);

  switch(cat){
    default:
    case "common":
      $("#info").html("Commun ("+len+")");
      $("#commun").addClass("selbut");
      $("#seduction").removeClass("selbut");
      $("#provocation").removeClass("selbut");
      $("#fuite").removeClass("selbut");
      $("#epilogue").removeClass("selbut");
      break;
    case "seduction":
      $("#info").html("Séduction ("+len+")");
      $("#commun").removeClass("selbut");
      $("#seduction").addClass("selbut");
      $("#provocation").removeClass("selbut");
      $("#fuite").removeClass("selbut");
      $("#epilogue").removeClass("selbut");
      break;
    case "provocation":
      $("#info").html("Provocation ("+len+")");
      $("#commun").removeClass("selbut");
      $("#seduction").removeClass("selbut");
      $("#provocation").addClass("selbut");
      $("#fuite").removeClass("selbut");
      $("#epilogue").removeClass("selbut");
      break;
    case "fuite":
      $("#info").html("Fuite ("+len+")");
      $("#commun").removeClass("selbut");
      $("#seduction").removeClass("selbut");
      $("#provocation").removeClass("selbut");
      $("#fuite").addClass("selbut");
      $("#epilogue").removeClass("selbut");
      break;
    case "epilogue":
      $("#info").html("Epilogue ("+len+")");
      $("#commun").removeClass("selbut");
      $("#seduction").removeClass("selbut");
      $("#provocation").removeClass("selbut");
      $("#fuite").removeClass("selbut");
      $("#epilogue").addClass("selbut");
      break;
  }

  Object.keys(sentencesData).forEach((idx) => {

    q = sentencesData[idx]['q'];
    a = sentencesData[idx]['a'];
    questions = ""
    if(typeof q == "object")
    {
      questions = "<ul>";
      q.forEach((s, j) => {
        questions += "<li>" + s + "</li>";
      });
      questions += "</ul>";
    } else {
      questions = q;
    }

    answers = ""
    if(typeof a == "object")
    {
      answers = "<ul>";
      a.forEach((s, j) => {
        answers += "<li>" + s + "</li>";
      });
      answers += "</ul>";
    } else {
      answers = a;
    }

    // console.log(idx, questions, answers);

    $sentences.append(
      "<tr class='sentenceRow'><th class='sentenceNum' scope='row'>" + idx + "</th>" +
      "<td class='sentenceElem sentenceEdit' id='sentence"+idx+"'>" + questions + "</td>"+
      "<td class='sentenceElem sentenceEdit2' id='answer"+idx+"'>" + answers + "</td>"+
      "</tr>");
  });

  $('.sentenceEdit').dblclick(function() {
    edit();
  });

  $('.sentenceEdit2').dblclick(function() {
    edit();
  });

  currRow = $('.sentenceRow').first();
  currRow.addClass("selected");
  $('.sentenceRow').click(function() {
    // console.log("CLICK");
    sel($(this));
  });
}

function next() {
  c = currRow.next();
  if (c.length > 0) {
    sel(c);
  }
}

function prev() {
  c = currRow.prev();
  if (c.length > 0) {
    sel(c);
  }
}

$(window).keydown(function (e) {
    if(editing)
      return;
    // console.log(e.which);
    shifted = e.shiftKey;
    var c = "";
    if (e.which == 13) { // Enter
      edit();
    } else if (e.which == 38) { // Up Arrow
      prev();
    } else if (e.which == 40 || e.which == 32) { // Down Arrow
      next();
    } else if (e.which == 83 && e.shiftKey) {
      //save();
    } else if (e.which == 65) { // a
      modalAdmin.modal('show');
    }
});

$(window).on('load', function() {
  url = new URL(window.location.href);
  cat = url.searchParams.get('cat');
  if(!cat)
    cat = "common";
  // console.log("cat", cat);
  load();
});

$("#commun").click(function(){
  // console.log("Edit common");
  cat = "common";
  history.pushState({}, null, "index.html?cat=common");
  $.ajax({
      url: "/getCommon",
      type: "GET",
      success: function(response) {
          fillSentences(response);
          $("html, body").animate({ scrollTop: 0 });
      },
      error: function(jqXHR, textStatus, errorMessage) {
          console.log(errorMessage); // Optional
      }
  });
});

$("#seduction").click(function(){
  // console.log("Edit seduction");
  cat = "seduction";
  history.pushState({}, null, "index.html?cat=seduction");
  $.ajax({
      url: "/getSeduction",
      type: "GET",
      success: function(response) {
          fillSentences(response);
          $("html, body").animate({ scrollTop: 0 });
      },
      error: function(jqXHR, textStatus, errorMessage) {
          console.log(errorMessage); // Optional
      }
  });
});

$("#provocation").click(function(){
  // console.log("Edit provocation");
  cat = "provocation";
  history.pushState({}, null, "index.html?cat=provocation");
  $.ajax({
      url: "/getProvocation",
      type: "GET",
      success: function(response) {
          fillSentences(response);
          $("html, body").animate({ scrollTop: 0 });
      },
      error: function(jqXHR, textStatus, errorMessage) {
          console.log(errorMessage); // Optional
      }
  });
});

$("#fuite").click(function(){
  // console.log("Edit fuite");
  cat = "fuite";
  history.pushState({}, null, "index.html?cat=fuite");
  $.ajax({
      url: "/getFuite",
      type: "GET",
      success: function(response) {
          fillSentences(response);
          $("html, body").animate({ scrollTop: 0 });
      },
      error: function(jqXHR, textStatus, errorMessage) {
          console.log(errorMessage); // Optional
      }
  });
});

$("#epilogue").click(function(){
  // console.log("Edit epilogue");
  cat = "epilogue";
  history.pushState({}, null, "index.html?cat=epilogue");
  $.ajax({
      url: "/getEpilogue",
      type: "GET",
      success: function(response) {
          fillSentences(response);
          $("html, body").animate({ scrollTop: 0 });
      },
      error: function(jqXHR, textStatus, errorMessage) {
          console.log(errorMessage); // Optional
      }
  });
});

$("#plus").click(function(){
  // console.log("PLUS !", cat);
  currRow.removeClass("selected");

  idx = parseInt($('.sentenceNum').last().html()) + 1;
  $sentences.append(
    "<tr class='sentenceRow'><th class='sentenceNum' scope='row'>" + idx + "</th>" +
    "<td class='sentenceElem sentenceEdit' id='sentence"+idx+"'></td>"+
    "<td class='sentenceElem sentenceEdit2' id='answer"+idx+"'></td>"+
    "</tr>");
  currRow = $('.sentenceRow').last();
  currRow.addClass("selected");
  currRow.get(0).scrollIntoView();
  currRow.click(function() {
    sel($(this));
  });
  $('#sentence'+idx).dblclick(function() {
    edit();
  });
  $('#answer'+idx).dblclick(function() {
    edit();
  });

  setTimeout(function(){
    edit();
  }, 300);
});

$("#del").click(function(){
  idx = currRow.children(".sentenceNum").html();
  if(confirm("Supprimer la ligne "+idx) == true)
  {
    // console.log("Delete", idx, q);
    $.ajax({
        url: "/del",
        type: "POST",
        data: JSON.stringify({
          "idx": escape(idx)
        }),
        success: function(response) {
            console.log(response['msg']);
            load();
        },
        error: function(jqXHR, textStatus, errorMessage) {
            console.log(errorMessage); // Optional
        }
    });
  }
});

// MODAL SENTENCE INPUT

function edit()
{
  editing = true;
  var q = currRow.children(".sentenceEdit").html();
  oldQ = q;
  q = q.replaceAll("\n","").replaceAll("<ul>","").replaceAll("<li>","- ").replaceAll("</ul>","").replaceAll("</li>","\n");
  var a = currRow.children(".sentenceEdit2").html();
  a = a.replaceAll("\n","").replaceAll("<ul>","").replaceAll("<li>","- ").replaceAll("</ul>","").replaceAll("</li>","\n");
  newSentence.val(q);
  newAnswer.val(a);
  setTimeout(function(){newSentence.focus();}, 500);
  modalSentence.modal('show');
}

function validSentence(ev) {
  ev.preventDefault();
  var q = "<ul>"+newSentence.val().replaceAll("- ", "</li><li>")+"</ul>";
  currRow.children(".sentenceEdit").html(q);
  var a = "<ul>"+newAnswer.val().replaceAll("- ", "</li><li>")+"</ul>";
  currRow.children(".sentenceEdit2").html(a);
  // console.log("VALID", currRow);
  modalSentence.modal('hide');
  save();
}

function save() {
  // console.log("SAVE")
  rowNum = currRow.children("th").first().html();
  q = currRow.children(".sentenceEdit").html().replaceAll('\n','').replaceAll("<ul>","").replaceAll("</ul>","").replaceAll("<li>","");
  questions = q.replaceAll("</li>","_SEPARATOR_");
  a = currRow.children(".sentenceEdit2").html().replaceAll("\n","").replaceAll("<ul>","").replaceAll("</ul>","").replaceAll("<li>","");
  answers = a.replaceAll("</li>","_SEPARATOR_");
  // console.log("NUM", rowNum, questions, answers);
  $.ajax({
      url: "/mod",
      type: "POST",
      data: JSON.stringify({
        "idx": rowNum,
        "q": escape(questions),
        "a": escape(answers)
      }),
      success: function(response) {
          console.log(response['msg']);
      },
      error: function(jqXHR, textStatus, errorMessage) {
          console.log(errorMessage); // Optional
      }
  });
}

function cancel(ev) {
  //
}

modalSentence.on("hide.bs.modal", function(){
  // console.log("HIDE", $('.sentenceRow').last().is(currRow), "("+newSentence.val()+")");
  if($('.sentenceRow').last().is(currRow) && newSentence.val() == "")
  {
    idx = currRow.children(".sentenceNum").html();
    currRow.remove()
    console.log("REMOVE LAST", idx);
  }
  editing = false;
});

$("#Close").click(function(ev)
{
  // console.log("CLOSE");
  cancel(ev);
});

$('#Cancel').click(function(ev)
{
  // console.log("CANCEL");
  cancel(ev);
});

modalSentence.submit(function(ev)
{
  // console.log("SUBMIT");
  validSentence(ev);
});


$('#Ok').click(function(ev)
{
  // console.log("OK");
  validSentence(ev);
});

function saveConfig() {
  modalAdmin.modal('hide');
  socket.send(JSON.stringify({
      'command':            'saveConfig',
      'max_intro':          $("#max_intro").val(),
      'max_seduction':      $("#max_seduction").val(),
      'max_provocation':    $("#max_provocation").val(),
      'max_fuite':          $("#max_fuite").val(),
      'max_intro_s':        $("#max_intro_s").val(),
      'max_seduction_s':    $("#max_seduction_s").val(),
      'max_provocation_s':  $("#max_provocation_s").val(),
      'max_fuite_s':        $("#max_fuite_s").val(),
      'pitch_intro':        $("#pitch_intro").val(),
      'pitch_seduction':    $("#pitch_seduction").val(),
      'pitch_provocation':  $("#pitch_provocation").val(),
      'pitch_fuite':        $("#pitch_fuite").val(),
      'pitch_epilogue':     $("#pitch_epilogue").val(),
      'speed_intro':        $("#speed_intro").val(),
      'speed_seduction':    $("#speed_seduction").val(),
      'speed_provocation':  $("#speed_provocation").val(),
      'speed_fuite':        $("#speed_fuite").val(),
      'speed_epilogue':     $("#speed_epilogue").val(),
      'max_silence':        $("#max_silence").val(),
      'max_inter_relance':  $("#max_inter_relance").val()
      // 'max_interactions': $("#max_interactions").val(),
      // 'max_section':      $("#max_section").val()
    }));
}

function reloadBrain() {
  modalAdmin.modal('hide');
  socket.send(JSON.stringify({'command':'reload'}));
}

$("#phone").change(function () {
    console.log($("#phone").prop('checked'));
    socket.send(JSON.stringify({'command':'phone', 'phone':$("#phone").prop('checked') ? 1 : 0}));
 });

// WEBSOCKET

var socket;

function connectToWS()
{
  socket = new WebSocket("ws://localhost:9001");

  socket.onopen = function(e) {
    stateBut.html("Open :)");
    stateBut.css("background", "lightgreen");
    console.log("[open] Connection established");
    socket.send(JSON.stringify({'command':'connect'}));
    socket.send(JSON.stringify({'command':'getConfig'}));
  };

  socket.onmessage = function(event) {
    // console.log(`[message] Data received from server: ${event.data}`);
    data = JSON.parse(event.data);
    if(data.command == "on") {
      console.log("PHONE ON", data.value);
      $("#phone").prop("checked", data.value);
    } else if(data.command == "message") {
      console.log("[ws]", data);
    } else if(data.command == "params") {
      // $("#max_interactions").val(data.max_interactions);
      // $("#max_section").val(data.max_section);
      $("#max_intro").val(data.max_intro);
      $("#max_seduction").val(data.max_seduction);
      $("#max_provocation").val(data.max_provocation);
      $("#max_fuite").val(data.max_fuite);
      $("#max_intro_s").val(data.max_intro_s);
      $("#max_seduction_s").val(data.max_seduction_s);
      $("#max_provocation_s").val(data.max_provocation_s);
      $("#max_fuite_s").val(data.max_fuite_s);
      $("#max_silence").val(data.max_silence);
      $("#max_inter_relance").val(data.max_inter_relance);
      $("#pitch_intro").val(data.pitch_intro);
      $("#pitch_seduction").val(data.pitch_seduction);
      $("#pitch_provocation").val(data.pitch_provocation);
      $("#pitch_fuite").val(data.pitch_fuite);
      $("#pitch_epilogue").val(data.pitch_epilogue);
      $("#speed_intro").val(data.speed_intro);
      $("#speed_seduction").val(data.speed_seduction);
      $("#speed_provocation").val(data.speed_provocation);
      $("#speed_fuite").val(data.speed_fuite);
      $("#speed_epilogue").val(data.speed_epilogue);
    } else if(data.command == "timers") {
    } else if(data.command == "silent") {
    } else if(data.command == "step") {
    } else {
      console.log("[ws]", data);
    }
  };

  socket.onclose = function(event) {
    stateBut.html("Closed :(");
    stateBut.css("background", "#ff9797");
    // console.log('[close] Connection closed');
    setTimeout(function(){
        checkSocket(socket.readyState);
    }, 3000);
  };

  socket.onerror = function(error) {
    stateBut.html("Error :(");
    stateBut.css("background", "#ff9797");
    // console.log(`[error] ${error.message}`);
    setTimeout(function(){
        checkSocket(socket.readyState);
    }, 3000);
  };
}

function checkSocket(state) {
    switch(state) {
        case socket.CONNECTING:
            stateBut.html("Connecting...");
            stateBut.css("background", "orange");
            console.log("- WebSocket Connecting...");
            break;
        case socket.OPEN:
            stateBut.html("Open :)");
            stateBut.css("background", "lightgreen");
            console.log("- WebSocket Open :)");
            break;
        case socket.CLOSING:
            stateBut.html("Closing...");
            stateBut.css("background", "orange");
            console.log("- WebSocket Closing...");
            break;
        case socket.CLOSED:
            stateBut.html("Closed :(");
            stateBut.css("background", "#ff9797");
            console.log("* WebSocket Closed :(");
            connectToWS();
            break;
    }
}

connectToWS();
