<?php
$size=filesize('exportedMeeting.xml');
header('Content-type: text/xml');
header('Content-Length: $size'); 
header('Content-disposition: attachment; filename=exportedMeeting.xml');
$fp=fopen('exportedMeeting.xml', 'r');
fpassthru($fp);
fclose($fp);
?>