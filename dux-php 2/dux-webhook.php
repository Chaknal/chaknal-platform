<?php
require __DIR__ . '/vendor/autoload.php';
session_start();

use League\Csv\Writer;

// Only allow POST requests
if (strtoupper($_SERVER['REQUEST_METHOD']) != 'POST') {
    throw new Exception('Only POST requests are allowed');
}
  
  // Make sure Content-Type is application/json 
  $content_type = isset($_SERVER['CONTENT_TYPE']) ? $_SERVER['CONTENT_TYPE'] : '';
if (stripos($content_type, 'application/json') === false) {
    throw new Exception('Content-Type must be application/json');
}

// Read the input stream
$body = file_get_contents("php://input");

// Decode the JSON object
$webevent = json_decode($body, true);

// Throw an exception if not a visit event
if ($webevent['type'] != 'visit') {
    throw new Exception('Only Dux-Soup Visit events are currently supported');
}

print_r($webevent);

$header = ['id', 'Profile', 'First Name', 'Last Name', 'Title', 'Company', 'Degree', 'Email', 'CompanyWebsite', 'Industry', 'Location'];
$csv = "";
$filename = "profilevisits.csv"; 

if (file_exists($filename)) {
    // append existing csv file
    $csv = Writer::createFromPath($filename, 'a');
} else {
    // create CSV file
    $csv = Writer::createFromPath($filename, 'w');
    //insert the header
    $csv->insertOne($header);
}

// copy pending row from session
$pendingrow = $_SESSION['pendingrow'];

// copy row from event
$rowdata=[];
foreach ($header as $value) {
    $rowdata[$value] = $webevent['data'][$value];
}

// merge create & update events
if ($webevent['event'] == 'create' && $pendingrow==null){
    // create event without pending event, store it.
    $pendingrow = $rowdata;
}else if ($webevent['event'] == 'create' && $pendingrow!=null){
    // create event with pending event, write pending and store new.
    $csv->insertOne($pendingrow);
    $pendingrow = $rowdata;
}else if ($webevent['event'] == 'update' && $pendingrow==null ){
    // update event without pending event, write it
    $csv->insertOne($rowdata);
}else if ($webevent['event'] == 'update' && $pendingrow!=null && $pendingrow['id']==$rowdata['id']){
    // update event with pending event of same profile, write it and clear pending
    $csv->insertOne($rowdata);
    $pendingrow = null;
}else if ($webevent['event'] == 'update' && $pendingrow!=null && $pendingrow['id']!=$rowdata['id']){
    // update event with pending event of other profile, write both and clear pending
    $csv->insertOne($pendingrow);
    $csv->insertOne($rowdata);
    $pendingrow = null;
}

// store new pending row value in session
$_SESSION['pendingrow'] = $pendingrow;
