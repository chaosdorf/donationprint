#!/usr/bin/env perl
use strict;
use warnings;
use 5.014;
use utf8;

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

	my $amount           = $self->param('amount');
	my $account          = $self->param('account');
	my $bank             = $self->param('bank');
	my $person           = $self->param('person');
	my $want_receiptdorf = $self->param('receiptdorf') // 0;
	my $want_receiptmail = $self->param('receiptmail') // 0;
	my $mail1            = $self->param('mail1');
	my $mail2            = $self->param('mail2');
	my $mail3            = $self->param('mail3');

	my @errors;

	# elements are changed in-place
	for my $value ( $amount, $account, $bank, $person, $mail1, $mail2, $mail3 )
	{
		$value =~ tr{Ä}{Ae};
		$value =~ tr{Ö}{Oe};
		$value =~ tr{Ü}{Ue};
		$value =~ tr{ä}{ae};
		$value =~ tr{ö}{oe};
		$value =~ tr{ü}{ue};
		$value =~ tr{ß}{sz};
		$value =~ tr{0-9a-zA-Z .,_-}{}cd;
	}

	if ( $amount !~ $re_amount ) {
		push( @errors, 'amount must be a number' );
	}
	if ( $account !~ $re_number ) {
		push( @errors, 'account must be a number' );
	}
	if ( $bank !~ $re_number ) {
		push( @errors, 'bank must be a number' );
	}

	if (@errors) {
		$self->render(
			'index',
			errors  => \@errors,
			version => $VERSION,
		);
	}
	else {
		$self->render( 'donated', version => $VERSION, );
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
