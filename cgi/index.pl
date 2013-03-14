#!/usr/bin/env perl
use strict;
use warnings;
use 5.014;
use utf8;

use IPC::Run qw(run);
use Mojolicious::Lite;

our $VERSION = '0.00';

my $re_amount = qr{ ^ \d* [,.]? \d{0,2} $ }x;
my $re_number = qr{ ^ \d* $ }x;

get '/' => sub {
	my ($self) = @_;

	$self->render( 'index', version => $VERSION, );
	return;
};

post '/print' => sub {
	my ($self) = @_;

	my %arg = map { $_ => undef } qw(
		account amount bank person mail1 mail2 mail3);
	my %opt = map { $_ => undef } qw(
		receiptdorf receiptmail);

	for my $key (keys %arg) {
		$arg{$key} = $self->param($key);
	}
	for my $key (keys %opt) {
		$opt{$key} = $self->param($key);
	}

	my @errors;

	if ($arg{amount}) {
		$arg{amount} =~ tr{,}{.};
		$arg{amount} = int($arg{amouunt} * 100);
	}

	for my $key (keys %arg) {
		if (defined $arg{$key}) {
			$arg{$key} =~ s{Ä}{Ae}g;
			$arg{$key} =~ s{Ö}{Oe}g;
			$arg{$key} =~ s{Ü}{Ue}g;
			$arg{$key} =~ s{ä}{ae}g;
			$arg{$key} =~ s{ö}{oe}g;
			$arg{$key} =~ s{ü}{ue}g;
			$arg{$key} =~ s{ß}{sz}g;
			$arg{$key} =~ tr{0-9a-zA-Z .,_-}{}cd;
			if (length($arg{$key}) == 0) {
				$arg{$key} = undef;
			}
		}
	}

	for my $key (qw(amount)) {
		if (defined $arg{$key} and $arg{$key} !~ $re_amount) {
			push(@errors, "$key must be an amount" );
		}
	}
	for my $key (qw(account bank)) {
		if (defined $arg{$key} and $arg{$key} !~ $re_number) {
			push(@errors, "$key must be a number" );
		}
	}

	if (@errors) {
		$self->render(
			'index',
			errors  => \@errors,
			version => $VERSION,
		);
	}
	else {
		my $out;
		my @cmd = ('./printtemplate');
		for my $key (keys %arg) {
			if (defined $arg{$key}) {
				push(@cmd, "--${key}=$arg{$key}");
			}
		}
		for my $key (keys %opt) {
			if (defined $opt{$key}) {
				push(@cmd, "--${key}");
			}
		}
		run(\@cmd, '<', \undef, '>&', \$out);
		$self->render( 'donated', output => $out, version => $VERSION, );
	}

	return;
};

app->config(
	hypnotoad => {
		accept_interval => 0.2,
		listen          => ['http://127.0.0.1:8082'],
		pid_file        => '/tmp/donationprint.pid',
		workers         => 1,
	},
);

app->defaults( layout => 'default' );

app->start;
