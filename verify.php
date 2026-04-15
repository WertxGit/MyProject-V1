<?php
$secret = "6LfK1rgsAAAAAEzUuknc2C46BKh37bj5dTkDup6R";
$response = $_POST["g-recaptcha-response"];

$verify = file_get_contents(
"https://www.google.com/recaptcha/api/siteverify?secret=$secret&response=$response"
);

echo $verify;
?>
