<?
if (!$f = fopen("/mnt/volume01/sinclair/public_html/emerge/timing.log","a"))
{
  echo "Error opening file.";
  exit;
}
$t = $_GET["timing"];
$u = $_SERVER['HTTP_USER_AGENT'];
$h = $_SERVER['REMOTE_ADDR'];
$r = fwrite($f,  $t.'!'.time().'!'.$u.'!'.$h."\n");
fclose($f);
?>