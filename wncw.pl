#!/usr/bin/perl
  use utf8;
  use Time::Local;
  use Term::ANSIColor;

  my $date = shift or print "which day?\n" and exit;
  $date =~ /(\d\d)(\d\d)/ or print "date format is mmdd\n" and exit;
  my ($dd,$mm,$yy,$wd) = (localtime(timelocal(0,0,0,$2,$1-1,2019)-24*60*60))[3..6]; # $mm is 0-based. minus 1 day  due to timezone of wncw.
  my $time = ($wd == 4)? '17:00' : '18:00';
  #thu 17:00
  #sat 18:00
  #sun 18:00
  my $url = sprintf "https://api.composer.nprstations.org/v1/widget/5187f56de1c8c6a808e91b8d/playlist?datestamp=%02d-%02d-%02d&order=1&time=$time",1900+$yy,$mm+1,$dd;
  $url .= "&prog_id=5187f5b1e1c8c6a808e91bc7" if $wd == 4;

  my $prog = shift;
  if ($prog eq 'ksmu'){
      $url = sprintf "https://api.composer.nprstations.org/v1/widget/536cd814e1c87b4608aa1186/playlist?datestamp=%02d-%02d-%02d&order=1&time=$time&prog_id=536cd819e1c87b4608aa119f",1900+$yy,$mm+1,$dd;
  }

  use JSON;
  use LWP::UserAgent;

  my $ua = LWP::UserAgent->new;
  my $req = HTTP::Request->new(GET => $url);
  my $res = $ua->request($req);
  if ($res->is_success) {
      $json = $res->content;
  }else{
      print $res->status_line, "\n";
      exit;
  }

  binmode(STDOUT, ':encoding(utf8)');

  my $hv_json = decode_json $json;
  my $set = $hv_json->{playlist};
  for my $e (@$set){
   print "\n**** $e->{'name'} ($e->{'date'}) ****\n\n";
   my $pls = $e->{playlist};
   for my $s (@$pls){
       $s->{'_start_time'} =~ s/\d+-\d+-\d+\s//;
       printf("%s | %s | %s | %s\n", $s->{'_start_time'}, $s->{'trackName'}, colored($s->{'artistName'},'GREEN'), $s->{'collectionName'});
   }
  }
