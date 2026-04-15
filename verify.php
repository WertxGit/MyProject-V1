<?php
$secret = "6LfK1rgsAAAAAJx85TRfcmsJur_-NGz2Yy9Nwek-";
$response = $_POST["g-recaptcha-response"];

$verify = file_get_contents(
"https://www.google.com/recaptcha/api/siteverify?secret=$secret&response=$response"
);

echo $verify;
?>