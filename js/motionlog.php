<?
$postdata = file_get_contents("php://input");

if (!$f = fopen("/mnt/volume01/sinclair/public_html/emerge/motion.log","a"))
{
  echo "Server error writing file.";
  exit;
}

$u = $_SERVER['HTTP_USER_AGENT'];
$h = $_SERVER['REMOTE_ADDR'];

fwrite($f, '!'.time().'!'.$u.'!'.$h."\n");
fwrite($f, $postdata);
fclose($f);

$lines = count(explode("\n", $postdata));

echo "Wrote " . $lines . " lines of data.";
?>
