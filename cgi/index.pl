#!/usr/bin/env perl
use strict;
use warnings;
use 5.014;

use Mojolicious::Lite;

our $VERSION = '0.00';

get '/' => sub {
	my ($self) = @_;

	$self->render(
		'index',
		version => $VERSION,
	);
	return;
};

app->config(
	hypnotoad => {
		accept_interval => 0.2,
		listen => ['http://127.0.0.1:8082'],
		pid_file => '/tmp/donationprint.pid',
		workers => 2,
	},
);

app->start;
