$(document).ready(function(){
$(".open_profile").click(function(){
    $(".pr_m_side_menu_wrap").css({display:"flex"});
    setTimeout(function() {
      $(".pr_m_side_menu_background").css({right:"0"});
     }, 0);
  });

  $('.pr_m_side_menu_wrap').on('click', function(e) {
    if (e.target !== this)
      return;
    $(".pr_m_side_menu_background").css({right:"-300px"});
    setTimeout(function() {
        $(".pr_m_side_menu_wrap").css({display:"none"});
    }, 300);
  });
  $(".pr_m_side_menu_close").click(function(){
    $(".pr_m_side_menu_background").css({right:"-300px"});
    setTimeout(function() {
        $(".pr_m_side_menu_wrap").css({display:"none"});
    }, 300);
  });
});