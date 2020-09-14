#! /usr/bin/perl
use strict;
use warnings;

use Text::CSV;

my %common = (
    "C" => "Center",
    "PF" => "Power Forward",
    "PG" => "Point Guard",
    "SF" => "Small Forward",
    "SG" => "Shooting Guard"
);

my %teamMap = (
    "ATL" => "Atlanta Hawks",
    "BKN" => "Brooklyn Nets",
    "BOS" => "Boston Celtics",
    "CHA" => "Charlotte Hornets",
    "CHI" => "Chicago Bulls",
    "CLE" => "Cleveland Cavaliers",
    "DAL" => "Dallas Mavericks",
    "DEN" => "Denver Nuggets",
    "DET" => "Detroit Pistons",
    "GSW" => "Golden State Warriors",
    "HOU" => "Houston Rockets",
    "IND" => "Indiana Pacers",
    "LAC" => "Los Angeles Clippers",
    "LAL" => "Los Angeles Lakers",
    "MEM" => "Memphis Grizzlies",
    "MIA" => "Miami Heat",
    "MIL" => "Milwaukee Bucks",
    "MIN" => "Minnesota Timberwolves",
    "NOP" => "New Orleans Pelicans",
    "NYK" => "New York Knicks",
    "OKC" => "Oklahoma City Thunder",
    "ORL" => "Orlando Magic",
    "PHI" => "Philadelphia 76ers",
    "PHX" => "Phoenix Suns",
    "POR" => "Portland Trail Blazers",
    "SAC" => "Sacramento Kings",
    "SAS" => "San Antonio Spurs",
    "TOR" => "Toronto Raptors",
    "UTA" => "Utah Jazz",
    "WAS" => "Washington Wizards"
);

my $file = $ARGV[0] or die "Need to get CSV file on the command line\n";

my $csv = Text::CSV->new ({ binary => 1, auto_diag => 1, sep_char => ',' });

open(my $data, '<:encoding(utf8)', $file) or die "Could not open '$file' $!\n";
my $rowNum = 0;
while (my $row = $csv->getline($data)) {
    my @fields = @$row;

    if ($rowNum != 0) {
	if (exists $common{$fields[2]}) {
	    $fields[2] = $common{$fields[2]};
	}
	else {
	    $fields[2] = "";
	}

	if (exists $teamMap{$fields[4]}) {
	    $fields[4] = $teamMap{$fields[4]};
	}
    }
    
    $csv->say(*STDOUT, \@fields);
    $rowNum++;
}
if (not $csv->eof) {
    $csv->error_diag();
}
close $data;
