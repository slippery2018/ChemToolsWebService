/**
 * @author tianwei
 */

$(function(){
  $("[rel=tooltip]").tooltip();
  $('#myCarousel').carousel();
});


$(function () {
  $('#MyWizard').on('changed', function(e, data) {
		console.log('changed');
	});
	$('#MyWizard').on('finished', function(e, data) {
		console.log('finished');
	});
	$('#btnWizardPrev').on('click', function() {
		$('#MyWizard').wizard('previous');
	});
	$('#btnWizardNext').on('click', function() {
		$('#MyWizard').wizard('next','foo');
	});
	$('#btnWizardStep').on('click', function() {
		var item = $('#MyWizard').wizard('selectedItem');
	});
});


$(function(){ 
  $('ul li a.filter').click(
    function(){
      $("ul li a.filter").parent().removeClass('active');
      $(this).parent().attr('class','active');
      
      var success_queue = 'ul.tasklist > li.success';
      var failed_queue = 'ul.tasklist > li.failed';
      var inprogress_queue = 'ul.tasklist > li.calculating';
      switch($(this).attr('rel'))
      {
        case 'all':
          $(success_queue).show();
          $(failed_queue).show();
          $(inprogress_queue).show();
          break;
        case 'success':
          $(success_queue).show();
          $(failed_queue).hide();
          $(inprogress_queue).hide();
          break;
        case 'failed':
          $(success_queue).hide();
          $(failed_queue).show();
          $(inprogress_queue).hide();
          break;
        case 'inprogress':
          $(success_queue).hide();
          $(failed_queue).hide();
          $(inprogress_queue).show();
          break;
        default:
          break;
      }
  });
});

$(function () {
    $('.tree li:has(ul)').addClass('parent_li').find(' > span');
    $('.tree li.parent_li > span').on('click', function (e) {
        var children = $(this).parent('li.parent_li').find(' > ul > li');
        if (children.is(":visible")) {
            children.hide();
            $(this).find(' > i').addClass('glyphicon-plus-sign').removeClass('glyphicon-minus-sign');
        } else {
            children.show();
            $(this).find(' > i').addClass('glyphicon-minus-sign').removeClass('glyphicon-plus-sign');
        }
        e.stopPropagation();
    });
});


$(function () {
    $('.model-args').hide(); 

    $('.checkbox').click(function(){
      var model_args = $('#' + $(this).attr('model') + '_args'); 
      if($(this).find('input[type=checkbox]').is(':checked')){
        model_args.hide();
      }else{
        model_args.show();
      }
    });
});
