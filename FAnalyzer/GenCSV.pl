#! /usr/bin/perl
use strict;
use warnings;

use JSON;
use Text::CSV;

my $file = $ARGV[0] or die "Need to get JSON file on the command line\n";

my $json_text = do {
  open(my $json_fh, "<:encoding(UTF-8)", $file) or die("Can't open \$filename\": $!\n");
  local $/;
  <$json_fh>
};

my $json = JSON->new;
my $data = $json->decode($json_text);

for ( @{$data->{data}} ) {
    print $_->{name}."\n";
}
