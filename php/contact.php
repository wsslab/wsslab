<?php
/** ****************************************** **
 *	@CONTACT FORM 	V1.1
 *	@AUTHOR			Dorin Grigoras
 *	@DATE			Tuesday, October 21, 2014
 ** ****************************************** **/
	session_start();
	@ini_set('display_errors', 0);
	@ini_set('track_errors', 0);
	@date_default_timezone_set('Europe/Bucharest'); // Used only to avoid annoying warnings.

	if($_REQUEST['action'] = 'email_send') {

		// BEGIN
		require('config.inc.php');

		$array['contact_name'] 		= isset($_REQUEST['contact_name']) 		? strip_tags(trim($_REQUEST['contact_name'])) 							: '';
		$array['contact_email']		= isset($_REQUEST['contact_email']) 	? ckmail($_REQUEST['contact_email']) 									: '';
		$array['contact_phone']		= isset($_REQUEST['contact_phone']) 	? strip_tags(trim($_REQUEST['contact_phone']))							: '-';
		$array['contact_subject'] 	= isset($_REQUEST['contact_subject']) 	? strip_tags(trim($_REQUEST['contact_subject'])) 						: $config['subject'];
		$array['contact_message'] 	= isset($_REQUEST['contact_message']) 	? (trim(strip_tags($_REQUEST['contact_message'], '<b><a><strong>')))	: '';
		$array['contact_captcha']	= isset($_REQUEST['contact_captcha']) 	? strip_tags(trim($_REQUEST['contact_captcha']))						: '-';

		// Check required fields
		if($array['contact_name'] == '' || $array['contact_email'] == '' || $array['contact_message'] == '')
			die('_required_');

		// Check email
		if($array['contact_email'] === false)
			die('_invalid_email_');

		if($array['contact_captcha'] != $_SESSION['captcha'])
			die('_invalid_captcha_');

		// Visitor IP:
		$ip = ip();

		// DATE
		$date = date('l, d F Y , H:i:s');

		$mail_body = "
			<b>Date:</b> 	{$date} 							<br> 
			<b>Name:</b> 	{$array['contact_name']}			<br>
			<b>Email:</b> 	{$array['contact_email']}			<br>
			<b>Phone:</b> 	{$array['contact_phone']}			<br>
			<b>Subject:</b> {$array['contact_subject']}			<br>
			<b>Message:</b> {$array['contact_message']}			<br>
			---------------------------------------------------	<br>
			IP: {$ip}
		";

		// SMTP ENABLED [isset = for old versions]
		if(!isset($config['use_smtp']) || isset($config['use_smtp']) && $config['use_smtp'] === true) {

			require('phpmailer/5.1/class.phpmailer.php');

			$m = new PHPMailer();
			$m->IsSMTP();
			$m->SMTPDebug  	= false;					// enables SMTP debug information (for testing) [default: 2]
			$m->SMTPAuth   	= true;						// enable SMTP authentication
			$m->Host       	= $config['smtp_host']; 	// sets the SMTP server
			$m->Port       	= $config['smtp_port'];		// set the SMTP port for the GMAIL server
			$m->Username   	= $config['smtp_user'];		// SMTP account username
			$m->Password   	= $config['smtp_pass'];		// SMTP account password
			$m->SingleTo   	= true;
			$m->CharSet    	= "UTF-8";
			$m->Subject 	= $array['contact_subject'];
			$m->AltBody 	= 'To view the message, please use an HTML compatible email viewer!';

			$m->AddAddress($config['send_to'], 'Contact Form');
			$m->AddReplyTo($array['contact_email'], $array['contact_name']);
			$m->SetFrom($config['smtp_user'], 'Contact Form');
			$m->MsgHTML($mail_body);

			if($config['smtp_ssl'] === true)
				$m->SMTPSecure = 'ssl';					// sets the prefix to the server

			// @SEND MAIL
			if($m->Send()) {
				die('_sent_ok_'); 
			} else {
				die($m->ErrorInfo); 
			}

			unset($array, $m);

		} 
		
		// mail()
		else {
		
			// mail( string $to , string $subject , string $message [, string $additional_headers [, string $additional_parameters ]] )
			mail( 
				$config['send_to'] , 
				$array['contact_subject'],
				$mail_body
			);

		}
	}

/** ********************************** 
 @CHECK EMAIL
/** ******************************* **/
	function ckmail($email) {
		$email = trim(strtolower($email));
		if(preg_match('/^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$/',trim($email))){
			return $email;
		} else { return false; }
	}

 /** ********************************** 
 @VISITOR IP
/** ******************************* **/
	function ip() {
		if     (getenv('HTTP_CLIENT_IP'))       { $ip = getenv('HTTP_CLIENT_IP');       } 
		elseif (getenv('HTTP_X_FORWARDED_FOR')) { $ip = getenv('HTTP_X_FORWARDED_FOR'); } 
		elseif (getenv('HTTP_X_FORWARDED'))     { $ip = getenv('HTTP_X_FORWARDED');     } 
		elseif (getenv('HTTP_FORWARDED_FOR'))   { $ip = getenv('HTTP_FORWARDED_FOR');   } 
		elseif (getenv('HTTP_FORWARDED'))       { $ip = getenv('HTTP_FORWARDED');       } 
										   else { $ip = $_SERVER['REMOTE_ADDR'];        } 
		return $ip;
	}
?>