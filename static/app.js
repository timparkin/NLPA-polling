var xhr = new XMLHttpRequest();
var handleFolder = function(index, id) {
  axios.post('/change_folder', {index: index, id: id})

  .then((data) => {
    console.log('folder_changed')

  })
}

var folders = document.querySelectorAll('.folder')

folders.forEach((folder, index) => {
  folder.addEventListener('click', (event) => {
    handleFolder(index, folder.id)
  }, true)
})









ts = document.querySelector('.toggleshow')
if (ts) {

  ts.addEventListener('click', (event) => {
    axios.post('/toggleshow', {})
        .then((data) => {
          console.log('toggleshow')
        })
  }, true)

}

var pollMembers = document.querySelectorAll('.poll-member')

pollMembers.forEach((pollMember, index) => {

    var buttons = pollMember.querySelectorAll('.button')

    buttons.forEach((button, bindex) => {

      button.addEventListener('click', (event) => {
        handlePoll(pollMember.getAttribute('pindex'), pollMember.id,  bindex)

        pollMember_buttons = pollMember.querySelectorAll('.button')
        all_buttons = document.querySelectorAll('.button')

        all_buttons.forEach( (all_button, all_button_index ) => {
                if (all_button.classList.contains('button'+(bindex+1))) {
                  all_button.classList.remove('selected')
                }

            })


        pollMember_buttons.forEach( (pollMember_button, pollMember_button_index ) => {
                pollMember_button.classList.remove('selected')
            })

        button.classList.add('selected')
      }, true)



    })
  pollMember.querySelector('.percentageBarParent').addEventListener('dblclick', () => {

    if (pollMember.classList.contains('hidden')) {

      handleHide(pollMember.getAttribute('pindex'), pollMember.id, 'show')
    } else {

      handleHide(pollMember.getAttribute('pindex'), pollMember.id, 'hide')
    }
  })



})

  // Sends a POST request to the server using axios
var handlePoll = function(member, id, bid) {
  axios.post('/vote', {member: member, id: id, bid: bid})
  .then((data) => {
    console.log('data sent',member,id,bid)
  })
}

var handleHide = function(pindex, member, hide) {



  axios.post('/hide', {member: pindex, id: 'X', hide: hide})
  .then((data) => {
    console.log('hide data sent',pindex,member, hide)
  })
}





    // Configure Pusher instance
    var pusher = new Pusher('2c5f10b047da040d1be1', {
        cluster: 'eu',
        encrypted: true
      });
      
      // Subscribe to poll trigger
      var channel = pusher.subscribe('poll');

channel.bind('hide', function(data) {

  console.log('hiding', data)
    pollMember = $('.poll-member[pindex="'+data['member']+'"]')
    if (pollMember.hasClass('hidden')) {
      pollMember.removeClass('hidden')
    } else {
      pollMember.addClass('hidden')
    }
})

// VOTE STYLING Listen to vote event
channel.bind('vote', function(data) {

  votes = {}
  hide = {}

  for (i = 0; i < (data.length); i++) {
    datum = data[i]['p']
    name = data[i]['n']

    if (!votes[datum]) {
        votes[datum] = []
    }
    if (!hide[datum]) {
        hide[datum] = []
    }


    if (name != 'X') {
      votes[datum].push(data[i]['v'])
    } else {
      hide[datum].push(data[i]['v'])
    }
  }

  all_total = 0
  for (const [key, value] of Object.entries(votes)) {


    total = 0
    for (v in value) {
        total = total + value[v]
    }
    votes[key] = total

    all_total = all_total + total
  }
  np = 0
  p_list = document.querySelectorAll('.poll-member')

  $('.folder').removeClass('selected')
  f = $('body').attr('folder')
  $('.f'+f).addClass('selected')

  for (var i = 0; i < p_list.length; i++) {

    p = p_list[i]
    pindex = p.getAttribute('pindex')
    if ( votes[pindex] === undefined) {
      votes[pindex] = 0
    }



    if (hide[pindex] == '4') {
      p.classList.add('hidden');
    } else {
      p.classList.remove('hidden')
    }
    p.querySelector('.percentageBar').style.width = calculatePercentage(all_total, votes[pindex])
    p.querySelector('.percentageBar').style.background = "#388e3c"

    p.querySelector('.percentage .percent').textContent =  calculatePercentage(all_total, votes[pindex])
    if (votes[pindex] != 0) {
      p.querySelector('.percentage .score').textContent = votes[pindex]
    } else {
      p.querySelector('.percentage .score').textContent = ''
    }
    p.querySelector('.percentage .score').setAttribute('score',votes[pindex])


  }

});






      // Listen to toggleshow event
      channel.bind('toggleshow', function(data) {

        if (document.getElementById("j")) {
          if (data == 'True') {
            if (document.getElementById("j").classList.contains('hide')) {
              document.getElementById("j").classList.remove('hide');
            }
            document.getElementById("j").classList.add('show');
          } else {
            if (document.getElementById("j").classList.contains('show')) {
              document.getElementById("j").classList.remove('show');
            }
            document.getElementById("j").classList.add('hide');
          }
        }

        if (document.getElementById("o")) {
          if (data == 'True') {
            if (document.getElementById("o").classList.contains('hide')) {
              document.getElementById("o").classList.remove('hide');
            }
            document.getElementById("o").classList.add('show');
          } else {
            if (document.getElementById("o").classList.contains('show')) {
              document.getElementById("o").classList.remove('show');
            }
            document.getElementById("o").classList.add('hide');
          }
        }

      });


      let calculatePercentage = function(total, amount){
        if (amount == 0) {
          return ''
        } else {
          return Math.round((amount / total) * 100) + "%"
        }
      }


      channel.bind('refresh', function(data) {;
        setTimeout(function() {  location.reload(); }, 100);

      });

function reset_scores() {
    axios.post('/reset_scores', {})
  .then((data) => {
    console.log('reset scores')
  })
}


$(document).ready(function(){

$(".wrapper").popupLightbox();

  xhr.open("POST", '/load', false);
  xhr.send({})
  xhr.open("POST", '/getshow', false);
  xhr.send({})

});



window.onload = function() {
  xhr.open("POST", '/load', false);
  xhr.send({})
  xhr.open("POST", '/getshow', false);
  xhr.send({})
};








