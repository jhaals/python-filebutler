<?
$DATABASE = '/path/to/database/';
$FILES = '/path/to/files/';
$DEBUG = False;
$id = $_GET['u'];

/*
TODO:
	Secure input
*/


function downloadFile( $fullPath ){ 
  /* This function is stolen from http://www.php.net/manual/en/function.header.php#102175 */

  // Must be fresh start 
  if( headers_sent() ) 
    die(); 

  // Required for some browsers 
  if(ini_get('zlib.output_compression')) 
    ini_set('zlib.output_compression', 'Off'); 

  // File Exists? 
  if( file_exists($fullPath) ){ 
    
    // Parse Info / Get Extension 
    $fsize = filesize($fullPath); 
    $path_parts = pathinfo($fullPath); 
    $ext = strtolower($path_parts["extension"]); 
    
    // Determine Content Type 
    switch ($ext) { 
      case "pdf": $ctype="application/pdf"; break; 
      case "exe": $ctype="application/octet-stream"; break; 
      case "zip": $ctype="application/zip"; break; 
      case "doc": $ctype="application/msword"; break; 
      case "xls": $ctype="application/vnd.ms-excel"; break; 
      case "ppt": $ctype="application/vnd.ms-powerpoint"; break; 
      case "gif": $ctype="image/gif"; break; 
      case "png": $ctype="image/png"; break; 
      case "jpeg": 
      case "jpg": $ctype="image/jpg"; break; 
      default: $ctype="application/force-download"; 
    } 

    header("Pragma: public"); // required 
    header("Expires: 0"); 
    header("Cache-Control: must-revalidate, post-check=0, pre-check=0"); 
    header("Cache-Control: private",false); // required for certain browsers 
    header("Content-Type: $ctype"); 
    header("Content-Disposition: attachment; filename=\"".basename($fullPath)."\";" ); 
    header("Content-Transfer-Encoding: binary"); 
    header("Content-Length: ".$fsize); 
    ob_clean(); 
    flush(); 
    readfile( $fullPath ); 

  } else 
    die(); 
}

if(file_exists($DATABASE.$id)) {
	/*
		Get filename, password, expire date and one_time_download from database file
	*/
	$file = fopen($DATABASE.$id,'r');
	$contents = fread($file, filesize($DATABASE.$id));
	list($filename, $password, $expire, $one_time_download) = split(":", $contents);

	if($password) {
		if($_POST) {
			if(md5($_POST['password']) != $password) {
				die('Invalid password');
			}
		} else {
			?><html>
				<head>
					<title>Password protected file</title>
				</head>
				<body>
					<form action="" method="post">
					Password: <input type="password" name="password">
					<input type="submit" value="download">
					</form>
				</body>
			</html>
	<?
		die();
		}
	}

	// Check if requested file exists
	if(file_exists($FILES.$filename)) {
	
		// Any expire date? 0 = none
		if($expire != 0) {
			
			// Check expire date.
			if ($expire > date("YmdHi")) {
     			// valid
     			downloadFile($FILES.$filename);
     		} else {
     			if($DEBUG) {
     				$debugmsg .= 'Expired...<br/>';
     			}
     			// Invalid
     			// Set one_time_download to 1. Files will be deleted.
     			$one_time_download = 1;
     		}
		} else {
            // Valid URL and existing file
            $debugmsg .= 'Serving file...<br/>';
		    downloadFile($FILES.$filename);	
		}
		fclose($file);
		
        // Delete file if one_time_download = 1
		if($one_time_download == 1) {
			unlink($DATABASE.$id);
       		unlink($FILES.$filename);
       		if($DEBUG) {
       			$debugmsg .= 'One time download set to 1, deleted files<br/>';
       		}
		}
	} else {
		if($DEBUG) {
			$debugmsg .= 'Requested file does not exist<br/>';
		} 
	}
} else {
	if ($DEBUG) {
		$debugmsg .= 'Could not find id in database<br/>';
	}
}
if($DEBUG) {
	print $debugmsg;
} 
?>
