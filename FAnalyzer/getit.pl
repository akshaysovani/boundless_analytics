#!/usr/bin/perl

while ($n = read STDIN, $_, 1024) {
    while ($_ =~ /\"slice\"\:\s*\[\[([^,]+),\s*([^\]]+)\]\]/mg) {
	$keys{$1}++;
	$values{$2}++;
    }
}
print "Keys:\n";
while (($key, $val) = each(%keys)) {
    print "\t", $key, " = ", $val, "\n";
}
print "\nVals:\n";
while (($key, $val) = each(%values)) {
    print "\t", $key, " = ", $val, "\n";
}
