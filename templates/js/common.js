
function enableField()
{
	$("#hostname_input").show();
	$("#hostname_label").show();
	
}


function disableField()
{

	$("#hostname_input").hide();
	$("#hostname_label").hide();
	
}




function sign_out()
{

	$("#loading").show();
	$.get("log_in",{logout:"True"},
	
	function(){

		window.location="";
		
	});
	

}

function home_upload()
{

		$.ajaxFileUpload
		(
			{
				url:'upload',
				secureuri:false,
				fileElementId:'homefile',
				dataType: 'json',
				success: function (data)
				{
					$('#uploadtext').text('Home contents uploaded successfully !')
				},
				error: function (data)
				{
					$('#uploadtext').html('<b>Home contents upload failed.</b>')
				}
			}
		)
		
}

function release_upload()
{

		$.ajaxFileUpload
		(
			{
				url:'upload',
				secureuri:false,
				fileElementId:'releasefile',
				dataType: 'json',
				success: function (data)
				{
					$('#releasetext').text('Release file uploaded successfully !')
				},
				error: function (data)
				{
					$('#releasetext').html('<b>Release file upload failed.</b>')
				}
			}
		)
		
}

function wallpaper_upload()
{

		$.ajaxFileUpload
		(
			{
				url:'upload',
				secureuri:false,
				fileElementId:'wallpaperfile',
				dataType: 'json',
				success: function (data)
				{
					$("#loading").show();

					$.post("page_loader", {'page':'page6'} , function(page_data){
						
					$('#wallpapertext').text('Wallpaper uploaded successfully !')

					$("#loading").hide();

					});
					
					$('#wallpaper_items').prepend('<div class="wallpaper upload"><img style="cursor:pointer;" src="'+data.msg+'" /></div>');
					$('.upload').click(function(){$(this).fadeOut(100);$(this).fadeIn(100);


					$('.wallpaper').removeClass('selected_wallpaper');
					$(this).addClass("selected_wallpaper");




					});
		
},
				error: function (data)
				{
					$('#wallpapertext').html('<b>Wallpaper upload failed.</b>')
				}
			}
		)
		
}



function is_logged_in()	
{

	$("#loading").show();
	$.get("is_logged_in", {},

	function(data){
	
		if(data!='False')
		{
	
			load_step1();
		}
		else
		{
			load_step0();
		}



	});


}

$("input[name='password']").ready(function() {  
     $("input[name='password']").keypress(function (e) {  
         if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {  
            sign_in(); 
            return false;  
         } else {  
             return true;  
         }  
     });  
});

function sign_in()
{

	$("#loading").show();


	$.get("log_in", { username: $('input[name="username"]').val(), password: $('input[name="password"]').val() },
  	function(data){

		$("#loading").hide();
	
		if(data=='True')
		{
			load_step1();
		}
		else
		{ 
			$('#error').html('Wrong Username or Password ! <br /> Please try again.'); 
		}

  	});


}


function sign_up()
{


	$.get("register", { user: $('input[name="user"]').val(), email_id: $('input[name="email_id"]').val(), password1: $('input[name="password1"]').val(), password2: $('input[name="password2"]').val() },
  	function(data){
	
		if(data=='True')
		{
			$('#error_signup').html("Account successfully created.<br />Confirmation is emailed.");
			$('#popup').fadeOut(8000,function(){$('#error_signup').text("")});
			$('#signup_form')[0].reset();
		}
		else
		{ 
			$('#error_signup').html(data);
		}

	

  	});


}

function update_size()
{

		var senddata = $('form').serialize();
		$("#loading").show();

		$.post('update_size',senddata, function(data){
					  $('#total_size').html(data);
					  $("#loading").hide();
		 });

}


function load_step0()
{

	$("#statusline").text("");
	$("#left_container").load("ajax_pool #left #page0");

		$.post("page_loader", {page:'page0'}, function(data){

			$("#right_container").html(data);
		

                        
                                        $("input[name='password']").ready(function() {

					$(this).keypress(function (e) {
                                        if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {
                                                sign_in();
                                                return false;
                                        } else {
                                                return true;
                                        }
                                        });

					});
                       



	
		});

}

function load_step1()
{



	$("#loading").show();

	$("#statusline").text("Distrotype");

	$("#left_container").load("ajax_pool #left #page1");

	if($("#step_right").length)
	{
		$("#step_right").show();
		$("#loading").hide();
	}
	else
	{	
		$.post("page_loader", {page:'page1'}, function(data){

			$("#right_container").html(data);
			$("#loading").hide();			
		});




	}

	$("#page2").hide();


}	


function load_step2()
{
	
	if ( $('#live_radio').is(':checked')==true && ($('#title_input').val() == "" || $('#hostname_input').val() =="") )
	{
		$('#step1_error').text('Information incomplete');
		return true;
	}
	
	
	else if ($('#live_radio').is(':checked')==false && $('#title_input').val() == "" )
	{
		
		$('#step1_error').text('Enter Image title');
		
		return true;
	}

	

	$("#loading").show();
		var senddata = $('form').serialize();
		senddata = senddata + '&page=page2';
		$.post("page_loader", senddata);

	if($("#page2").length)
	{
		$("#page2").show();
		$("#loading").hide();
	}

	else
	{


		$.post("page_loader", senddata , function(data){
				
				$('#right_container').append(data);
				$("#loading").hide();
		});
	}


	$("#statusline").text("Distrotype > Repository");
	$("#step_right").hide();
	$("#page3").hide();	

	

}	


function load_step3()
{
	$("#loading").show();

		var senddata = $('form').serialize();
		senddata = senddata + '&page=page3';
		$.post("page_loader", senddata);

	if($("#page3").length)
	{
		$("#page3").show();
		$("#loading").hide();
	}
	else
	{


		$.post("page_loader", senddata , function(data){
						
			$('#right_container').append(data);
			$("#loading").hide();
	
			$("#lang_selector div").hover(function(){$(this).fadeOut(100);$(this).fadeIn(500);});
			$("#lang_selector div").click(function(){

				$(".lang").removeClass("highlighted");
				$(".lang").removeClass("clicked");
				$(this).addClass("highlighted");
				$(this).addClass("clicked");
				
			});
		});
	}


	$("#statusline").text("Distrotype > Repository > Languages");
	


	$("#page4").hide() ;
	$("#page2").hide() ;


}	


function load_step4()
{
	$("#loading").show();
		var senddata = $('form').serialize();
		senddata = senddata + '&page=page4';

		$.post("page_loader", senddata);

	if($("#page4").length)
	{
		$("#page4").show();
		$("#loading").hide();
	}

	else
	{


		$.post("page_loader", senddata , function(data){
						
			$('#right_container').append(data);
			$("#loading").hide();
		});
	}


	$("#statusline").text("Distrotype > Repository > Languages > Upload");
	$("#page5").hide() ;
	$("#page3").hide() ;	
}	


function load_step5()
{
	$("#loading").show();
		var senddata = $('form').serialize();
		senddata = senddata + '&page=page5';
		$.post("page_loader", senddata);
	if($("#page5").length)
	{
		$("#page5").show();
		$("#loading").hide();
	}

	else
	{


		$.post("page_loader", senddata , function(data){
			
			$('#right_container').append(data);


	
							

				$(function() {  
     					$("#search").keypress(function (e) {  
         			if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {  
            				$('#search_button').click(); 
            				return false;  
         			} else {  
             				return true;  
         			}  
     				});  
				});

								
			$("#loading").hide();

		});

	}


	$("#statusline").text("Distrotype > Repository > Languages > Upload > Packages");
	$("#page6").hide() ;
	$("#page4").hide() ;	
}




function load_step6()
{
	update_size();
	//Update the size label and live_packages cache object

	$("#loading").show();
		var senddata = $('form').serialize();
		senddata = senddata + '&page=page6';
		$.post("page_loader", senddata);
	if($("#page6").length)
	{
		$("#page6").show();
		$("#loading").hide();
	}

	else
	{
		

		var senddata = $('form').serialize();
		senddata = senddata + '&page=page6';

		$.post("page_loader", senddata , function(data){
		
			$('#right_container').append(data);
			$('.wallpaper').click(function(){$(this).fadeOut(100);$(this).fadeIn(100);

			    $('.wallpaper').removeClass('selected_wallpaper');
			    $(this).addClass("selected_wallpaper");


			});
		

			$(function() {$("div.scrollable").scrollable({ size:3,items:'.items',prev:'.prev',next:'.next'});	
	
			});


	
			$("#loading").hide();

			});

	}


	$("#statusline").text("Distrotype > Repository > Languages > Upload > Packages > Wallpaper");

	$("#page5").hide() ;
	$("#page7").hide() ;	
}



function load_step7()
{
	$("#loading").show();
		var senddata = $('form').serialize();
		var wallpaper = $('.selected_wallpaper img').attr('src');
		senddata = senddata + '&page=page7&wallpaper='+wallpaper;
		$.post("page_loader", senddata);
	if($("#page7").length)
	{
		$("#page7").show();
		$("#loading").hide();
	}

	else
	{
		

		var senddata = $('form').serialize();
		senddata = senddata + '&page=page7';

		$.post("page_loader", senddata , function(data){


			
			$('#right_container').append(data);
	
			$("#loading").hide();

		});

	}


	$("#statusline").text("Distrotype > Repository > Languages > Upload > Packages > Wallpaper > Media");
$(function()
{
	load_step6();

});
	$("#page6").hide() ;
	$("#page8").hide() ;	
}


function load_step8()
{
	$("#loading").show();
	if($("#page8").length)
	{
		$("#page8").show();
		$("#loading").hide();
	}

	else
	{
		

		var senddata = $('form').serialize();
		senddata = senddata + '&page=page8';

		$.post("page_loader", senddata , function(data){


			
			$('#right_container').append(data);
			$("#loading").hide();

		});

	}


	$("#statusline").text("Distrotype > Repository > Languages > Upload > Packages > Wallpaper > Media > Build");

	$("#page7").hide() ;

}


function load_userlog()
{
	$("#loading").show();

		

		
		$.post("page_loader", { page:'userlog'} , function(data){


			
			$('#right_container').html(data);
			$("#loading").hide();

		});

	


	$("#statusline").text("Userlog");

	$("#page7").hide() ;

}



// Language selection functions

function addtolangSelectList()
{



	if($('.selected_list div').length==0)
	{
		$('.clicked').addClass("default_lang");
	}
	else
	{
		$('.clicked').removeClass("default_lang");
	}

		$('.clicked').appendTo('.selected_list')
	
}

function addtolangList()
{
	$('.clicked').removeClass("default_lang");
	

	$('.clicked').appendTo('.list');

	if($('.selected_list div').length==1)
	{
		$('.selected_list div').addClass("default_lang");
	}

}


$(function(){

is_logged_in(); 
$("#loading").hide();
});


//To prevent browser stalling
$(window).unbind('unload');


/*
$(function()
{
	load_step6();

});
*/


