#!/usr/bin/perl
# this is a simple script to evaluate vertical selection
# for FedWeb'14
# Ke Zhou (zhouke.nlp@gmail.com), 28/05/2014
# Thomas Demeester (tdmeeste@intec.ugent.be), 14/10/2014

# usage: evalVS_v3 vrunfile vrelfile resultpath
# submissions format: 7001 FW14-v002 univX-VS1 (topicid verticalid run-tag)
# vrel format: 7001 FW14-v002 1 (topicid verticalid relevance (1 or 0))
#
# produces detailed results per topic


if (@ARGV != 2) {
    die "Usage:  evalVS_v3 <run_file>  \n
      run_file format: 7001 FW14-v002 univX-VS1 (topicid verticalid run-tag)\n
      vrel_file format: 7001 FW14-v002 1 (topicid verticalid relevance (1))\n\n";
}

$runFile = shift;
$vrelFile = shift;


# process vrel
open VREL, "<$vrelFile" or die "Fail to open $vrelFile: $!\n\n";
{
    local $/ = undef;
    @data = split(/\s+/, <VREL>);
}
close VREL or die "Fail to close $vrelFile: $!\n\n";

while (($topicid, $vertid, $rel) = splice(@data, 0, 3)) {
    $vrel{$topicid}->{$vertid} = $rel;
    $numRel{$topicid} += $rel;
}

# test vrel file
#foreach $t(sort keys %vrel) {
#    foreach $v(sort keys %{$vrel{$t}}) {
#        $rel = $vrel{$t}->{$v};
#        print "$t\t$v\t$rel\n";
#    }
#}


open RUNS, "<$runFile" or die "Fail to 1 open $runFile: $!\n\n";
{
    local $/ = undef;
    @data = split(/\s+/, <RUNS>);
}
close RUNS or die "Fail to close $runFile: $!\n\n";

while (($topicid, $vertid, $runid) = splice(@data, 0, 3)) {
    $runs{$runid}->{$topicid}->{$vertid} = 1;
}

## test run file
#foreach $r(sort keys %runs) {
#    foreach $t(sort keys %{$runs{$r}}) {
#        foreach $v(sort keys %{$runs{$r}->{$t}}) {
#            print "$r\t$t\t$v\n";
#        }
#    }
#}

## check run file; skip: submitted files already tested
#print "Running the TREC check script:\n";
#if (system("python /local/xmlir/fedweb/eval/src/check_vs_fedweb2014.py $runFile")) {
#    exit 255;
#}
#else {
#    print "   Ok.\n";
#}


# now evaluate each run based on vrel
foreach $runid (sort keys %runs) {

    $numTopics = 0;
    $sumPrec = 0;
    $sumRec = 0;
    $sumF = 0;
    $numRunTopics = 0;
    %results = ();

    foreach $topicid (sort keys %vrel) {
        next if (!$numRel{$topicid}); # if there is no vertical relevant for a topic, jumps to the next topic
        $numTopics++;

        $numRet = 0;
        $numRetRel = 0;

        foreach $vertid (sort keys %{$runs{$runid}->{$topicid}}) {
            $numRet++;
            # assuming verticals appearing in the vrel file are relevant (1)
            if ($vrel{$topicid}->{$vertid} == 1) {
                $numRetRel++;
            }
        }
        $rec = $numRetRel / $numRel{$topicid};
        if ($numRet == 0) {$prec = 0.0;}
        else {
            $prec = $numRetRel / $numRet;
            $numRunTopics++;
        }
        if ($prec + $rec == 0) {$fmeasure = 0;}
        else {$fmeasure = 2 * ($prec * $rec) / ($prec + $rec);}

        $sumPrec += $prec;
        $sumRec += $rec;
        $sumF += $fmeasure;

        #store individual results
        $res = join(',', ($prec, $rec, $fmeasure));
        $results{$topicid} = $res;
    }

    $meanPrec = $sumPrec / $numTopics;
    $meanRec = $sumRec / $numTopics;
    $meanF = $sumF / $numTopics;

    $numEvalTopics = scalar(keys %vrel);

    print "RUN ($runid)\n";
    printf "num of topics in vrel_file: %5d\n", $numEvalTopics;
    printf "num of topics in run_file:  %5d\n", $numRunTopics;
    printf "mean precision:             %.4f\n", $meanPrec;
    printf "mean recall:                %.4f\n", $meanRec;
    printf "mean f-measure:             %.4f\n", $meanF;

    for (sort keys %results) {
        print "$_,", $results{$_}, "\n"
    }
    print "$_ $results{$_}\n" for (keys %results);

}

