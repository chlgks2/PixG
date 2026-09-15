


let scrHig = $('section').height();

$(window).on('scroll',function(){

    let scr = $(window).scrollTop();
      
    if(scr >= 0 && scr < scrHig){
      $('nav').stop().animate({'left':'-100%'})
    }   
    if(scr > scrHig){
      $('nav').stop().animate({'left':0})
    }


    function liClass(e){
      $('nav li').eq(e).addClass('on').siblings().removeClass('on')
  }

  if(scr >= 0 && scr < scrHig){
      liClass(0)
  }

  if(scr >= scrHig && scr < scrHig*2){
      liClass(1)
  }

  if(scr >= scrHig*2 && scr < scrHig*3){
      liClass(2)
  }

  if(scr >= scrHig*3 && scr < scrHig*4){
      liClass(3)
  } 

  if(scr >= scrHig*4){
      liClass(4)
  }

});


$('nav li').click(function(){

  let i = $(this).index()

  $('html, body').stop().animate({'scrollTop' : scrHig * i+60})

});

$('.gen').click(function(){
  $('html, body').stop().animate({'scrollTop' : scrHig * 3 +60})

})

$('#wrap section').on('mousewheel',function(e,d){

  if(d>0){
    let prv = $(this).prev().offset().top;
  $('html, body').stop().animate({'scrollTop':prv});

  }else if(d<0){
    let nxt = $(this).next().offset().top;
  $('html, body').stop().animate({'scrollTop':nxt});  

  }
  
});


    $('article').click(function(e){
      e.preventDefault(); //a태그로 인해 새로고침 되는 것을 막음

      $('.imgView').fadeIn();

      let img = $(this).find('.assetBox').html();
      $('.imgShow').html(img);

      let h4 = $(this).find('h4').html();
      $('.imgView').find('h4').html(h4);

      let p = $(this).find('p').html();
      $('.imgView').find('p').html(p)

  });

  $('i, .closeWrap').click(function(){
      $('.imgView').fadeOut()
  });


var cursorBig = document.querySelector('.big');
var cursorSmall = document.querySelector('.small');
var a = document.querySelectorAll('button');
var b = document.querySelectorAll('article');
var c = document.querySelectorAll('i');
var d = document.querySelectorAll('a');

document.addEventListener('mousemove', function(e){
  var x = e.clientX;
  var y = e.clientY;
  cursorBig.style.transform = `translate3d(calc(${x}px - 50%), calc(${y-60}px - 50%), 0)`
});

document.addEventListener('mousemove', function(e){
  var x = e.clientX;
  var y = e.clientY;
  cursorSmall.style.left = x + 'px';
  cursorSmall.style.top = y + 'px';
});


document.addEventListener('mousedown', function(){
  cursorBig.classList.add('click');
  cursorSmall.classList.add('hover__small')
});


document.addEventListener('mouseup', function(){
  cursorBig.classList.remove('click')
  cursorSmall.classList.remove('hover__small')
});


a.forEach(item => {
  item.addEventListener('mouseover', () => {
    cursorBig.classList.add('hover__big');
    cursorSmall.classList.add('hover__small');
  });
  item.addEventListener('mouseleave', () => {
    cursorBig.classList.remove('hover__big');
    cursorSmall.classList.remove('hover__small');
  });
})

b.forEach(item => {
  item.addEventListener('mouseover', () => {
    cursorBig.classList.add('hover__big');
    cursorSmall.classList.add('hover__small');
  });
  item.addEventListener('mouseleave', () => {
    cursorBig.classList.remove('hover__big');
    cursorSmall.classList.remove('hover__small');
  });
})

c.forEach(item => {
  item.addEventListener('mouseover', () => {
    cursorBig.classList.add('hover__big');
    cursorSmall.classList.add('hover__small');
  });
  item.addEventListener('mouseleave', () => {
    cursorBig.classList.remove('hover__big');
    cursorSmall.classList.remove('hover__small');
  });
})


d.forEach(item => {
  item.addEventListener('mouseover', () => {
    cursorBig.classList.add('hover__big');
    cursorSmall.classList.add('hover__small');
  });
  item.addEventListener('mouseleave', () => {
    cursorBig.classList.remove('hover__big');
    cursorSmall.classList.remove('hover__small');
  });
})