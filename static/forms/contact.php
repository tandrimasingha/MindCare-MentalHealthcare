<?php
//get data from form  
$name = $_POST['name'];
$email= $_POST['email'];
$subject= $_POST['subject'];
$message= $_POST['message'];

$to = "jayesh.shaw9@gmail.com";
// $subject = "Mail From website";
$txt ="Name = ". $name . "\r\n  Email = " . $email . "\r\n Message =" . $message;
$headers = "From: isiiec.contactUs@gmail.com" . "\r\n" .
"CC: jayesh.shaw10@gmail.com";
if($email!=NULL){
    mail($to,$subject,$txt,$headers);
}
//redirect
header("Location: thankyou.html");
?>