<?php

$userid = $argc > 1 ? $argv[1] : null;
$prvkey = $argc > 2 ? $argv[2] : null;
$commandfilename = $argc > 3 ? $argv[3] : "rc-commands.txt";
$invitemessagefilename = $argc > 4 ? $argv[4] : "invitemessage.txt";
$directmessagefilename = $argc > 5 ? $argv[5] : "directmessage.txt";
$invitemessagetext = '';
$directmessagetext = '';

$exit = false;

if ($userid == null){
    print "Remote Control userid not set\n";
    $exit = true;
}
if ($prvkey == null){
    print "Remote Control Authentication key not set\n";
    $exit = true;
}
if ($exit){
    print "USAGE: php dux-rc.php <userid> <authkey> [<command inputfile>]\n";
    return;
}

print "Posting to Remote Control Queue for user $userid\n";
print "Please note that the queue will never add an already queued command twice!\n";
$commandfile = new SplFileObject($commandfilename);
$invitemessagefile = new SplFileObject($invitemessagefilename);
$directmessagefile = new SplFileObject($directmessagefilename);

while (!$invitemessagefile->eof()) {
    $invitemessagetext .= $invitemessagefile->fgets();
}
while (!$directmessagefile->eof()) {
    $directmessagetext .= $directmessagefile->fgets();
}

while (!$commandfile->eof()) {
    $rcurl  = "https://app.dux-soup.com/xapi/remote/control/$userid/queue";
    // each line can contain either just a profile , or a command tuple:
    // https://www.linkedin.com/in/janjanjanjanjan/ 
    // which will trigger a visit of the profile
    // OR
    // message https://www.linkedin.com/in/janjanjanjanjan/ 2020-09-01
    // which will send a direct message, taken from directmessage.txt, and
    // send it to the target profile after the specified date ( optional )
    // Date should be in ISO String format : https://nl.wikipedia.org/wiki/ISO_8601
    // Other possible values for command are 'connect' and 'visit'

    $cmdstr = $commandfile->fgets();
    $command = explode(' ', trim($cmdstr)   );

    if (sizeof($command)>0 && $command[0]!=""){
        $data = [
            'command' => sizeof($command)>1 ? $command[0] : 'visit',
            'targeturl' => $rcurl,
            'userid' => $userid,
            'timestamp' => time()*1000,
            'params' => [
                'profile' => sizeof($command)>1 ? $command[1] : $command[0],
            ]
        ];

        if ($data['command'] === 'connect'){
            $data['params']['messagetext'] = $invitemessagetext;
        } else if ($data['command'] === 'message'){
            $data['params']['messagetext'] = $directmessagetext;
        }
        
        if (sizeof($command) === 3){
            // timestamp found, should be in ISO String format : https://nl.wikipedia.org/wiki/ISO_8601
            $data['runafter'] = $command[2];
        }

        // Request has been built, calculate the SHA1 hash and encode 
        // the result in base64 before adding it as an HTTP header.
        $duxsig = base64_encode(hash_hmac("sha1", json_encode($data), $prvkey, true));

        $options = [
            'http' => [
                'method'  => 'POST',
                'content' => json_encode( $data ),
                'header'  =>  "Content-Type: application/json\r\n" .
                            "Accept: application/json\r\n" .
                            "X-Dux-Signature: $duxsig\r\n",
                'ignore_errors' => TRUE
            ],
        ];

        $context  = stream_context_create( $options );
        $result = file_get_contents( $rcurl, false, $context );
        $response = json_decode( $result );

        $cmdtxt = $data['command'];
        $cmdprof = $data['params']['profile'];
        if ($response->messageid){
            print "+ $cmdtxt $cmdprof succeeded with MSGID: $response->messageid\n";
        }else{
            print "- $cmdtxt $cmdprof failed with ERROR: $http_response_header[0]\n";
        }
    }
}

$commandfile = null;
$invitemessagefile = null;
$directmessagefile = null;
?>

