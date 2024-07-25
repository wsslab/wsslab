<?php
/**
 * @version		v1.0
 * @date		Tuesday, October 21, 2014
 * @author		Grigoras Dorin
 *
				USAGE:
				<img alt="" rel="nofollow,noindex" width="50" height="18" src="php/captcha.php" />
				$_SESSION['captcha']  - use it in your script.

				Supported link:
					php/captcha.php?w=100&amp;h=50&amp;s=30&amp;bgcolor=ffffff&amp;txtcolor=000000
**/
	session_start();
	@ini_set('display_errors', 0);
	@ini_set('track_errors', 0);

	header('Cache-Control: no-cache');
	header('Pragma: no-cache');

/** ********************************** 
 @RANDOM GENERATORS [LN, N, L]
/** ******************************* **/
    function random($length=6,$type=null) { // null = letters+numbers, L = letters, N = numbers

		switch($type) {
			case 'N' :	$chars = '0123456789'; 								break;
			case 'L' :	$chars = 'abcdefghijklmnopqrstuvwxyz'; 				break;
			default  :	$chars = 'abcdefghijklmnopqrstuvwxyz0123456789'; 	break;
		}

		$numChars = strlen($chars); $string = '';
        for ($i = 0; $i < $length; $i++) { $string .= substr($chars, rand(1, $numChars) - 1, 1); }
		unset($chars);
		return $string; 
	}


/** ********************************** 
 @_GET shortcut and protect
/** ******************************* **/
	function _getVar($var) {
		if(isset($_GET[$var])) {
			return trim($_GET[$var]);
		} else { return null; }
	}


/** ********************************** 
 @CAPTCHA
/** ******************************* **/
	// Put the code in session to use in script
	if(_getVar('c') != '') 
		$c = (int) _getVar('c'); 
	else 
		$c = 6;
	$mycode = random($c,'N');
	
	$_SESSION['captcha'] = $mycode;

	// Image Size from a specified dimensions
	$w =  (int) _getVar('w'); if($w == '') $w = 60; // width
	$h =  (int) _getVar('h'); if($h == '') $h = 18; // height
	$s =  (int) _getVar('s'); if($s == '') $s = 5; // font size [5 max.]
	$bgcolor  = _getVar('bgcolor');  if($bgcolor == '')  $bgcolor   = 'ffffff'; // background color [ffffff default]
	$txtcolor = _getVar('txtcolor'); if($txtcolor == '') $txtcolor  = '000000'; // text color [000000 default]

	// convert color to R  G  B 
	// [from ffffff to  ff ff ff]
	$bgcol 	 = sscanf($bgcolor,  '%2x%2x%2x');
	$txtcol	 = sscanf($txtcolor, '%2x%2x%2x');

	// Create image
	$code  = $_SESSION['captcha'];
	$image = imagecreate($w, $h); 											// image size [50x18 default]
	$bgcol = imagecolorallocate($image, $bgcol[0], $bgcol[1],  $bgcol[2]); 	// background color
	$txcol = imagecolorallocate($image, $txtcol[0], $txtcol[1], $txtcol[2]); // text color
	$strn2 = imagestring($image, $s, 0, 0, $code, $txcol);					// text size [4 default]
	header('Content-Type: image/png');
	imagepng($image);
	imagedestroy($image);

?>