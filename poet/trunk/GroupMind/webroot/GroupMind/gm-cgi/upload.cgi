#!/usr/bin/perl
use strict; # To specify a strict use of variables and functions
use CGI; # To handle much of the upload work.

#maybe not the right directory
my $StoreFileDirectory = '/upload';

#hard-coded for now, but should be made dynamic to prevent conflict
my $StoreFileName = 'importedQuestions.xml';

#this will probably have to point back to the EditQuestions page
my $ThankYouPage = '';

# Load the contents of the form into the $FORM variable.
my $FORM = new CGI;

sub StoreUploadedFile
{
	# Grab the filehandle of the uploaded file.
	my $filehandle = $FORM->upload('filename');
	# Return false if no file uploaded.
	return '' unless $filehandle;
	# Grab the file name of the uploaded file.
	my $filename = $FORM->param('filename');
	# Strip any path information from the file name.
	$filename =~ s!^.*[/\\]!!;
	# Determine file storage name and directory location.
	$StoreFileName = $filename unless $StoreFileName =~ /\w/;
	$StoreFileDirectory .= '/' if $StoreFileDirectory =~ /\w/ and $StoreFileDirectory !~ m![\\/]$!;
	$StoreFileDirectory = "$ENV{DOCUMENT_ROOT}$StoreFileDirectory" if $StoreFileDirectory =~ m!^[\\/]!;
	# Store the file.
	my $buffer;
	open UPLOADED,">$StoreFileDirectory$StoreFileName";
	binmode UPLOADED; # for Win/DOS operating systems
	while(read $filehandle,$buffer,1024) { print UPLOADED $buffer; }
	close UPLOADED;
	# Return true.
	return 1;
} # sub StoreUploadedFile


sub PresentUploadForm
{
	# Notice the enctype attribute of the form.
	print "Content-type: text/html\n\n";
	print <<FORM;
<html><body>

<form 
   name="UploadForm" 
   enctype="multipart/form-data" 
   action="http://$ENV{SERVER_NAME}$ENV{REQUEST_URI}" 
   method="POST">
<input type="file" name="filename" size="55">
<br>
<input type="submit">
</form>

</body></html>
FORM
} # sub PresentUploadForm

my $stored = StoreUploadedFile;
exit PresentUploadForm unless $stored and $ThankYouPage;
print "Location: $ThankYouPage\n\n";
# end of script

