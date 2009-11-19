
from os.path import basename

from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives

from email_extras.settings import USE_GNUPG, GNUPG_HOME


if USE_GNUPG:
	from gnupg import GPG
	from email_extras.models import Address


def addresses_for_key(gpg, key):
	"""
	takes a key and extracts the email addresses for it
	"""
	fingerprint = key["fingerprint"]
	addresses = []
	for key in gpg.list_keys():
		if key["fingerprint"] == fingerprint:
			addresses.extend([address.split("<")[-1].strip(">") 
				for address in key["uids"] if address])
	return addresses
	

def send_mail(subject, body_text, addr_from, addr_to, fail_silently=False, 
	attachments=None, body_html=None):
	"""
	sends a multipart email containing text and html versions which are 
	encrypted for each recipient that has a valid gpg key installed
	"""

	# allow for a single address to be passed in
	if not hasattr(addr_to, "__iter__"):
		addr_to = [addr_to]

	# obtain a list of the recipients that have gpg keys installed
	valid_key_addresses = []
	if USE_GNUPG:
		valid_key_addresses = Address.objects.filter(address__in=addr_to
			).values_list("address", flat=True)
		# create the gpg object
		if valid_key_addresses:
			gpg = GPG(gnupghome=GNUPG_HOME)
			
	# encrypts body if recipient has a gpg key installed
	encrypt_if_key = lambda body, addr: (body if addr not in valid_key_addresses 
		else unicode(gpg.encrypt(body, addr)))
		
	# load attachments and create name/data tuples
	attachments_parts = []
	if attachments is not None:
		for attachment in attachments:
			f = open(attachment, "rb")
			attachments_parts.append((basename(attachment), f.read()))
			f.close()
	
	# send emails
	for addr in addr_to:
		msg = EmailMultiAlternatives(subject, encrypt_if_key(body_text, addr), 
			addr_from, [addr])
		if body_html is not None:
			msg.attach_alternative(encrypt_if_key(body_html, addr), "text/html")
		for parts in attachments_parts:
			msg.attach(parts[0], encrypt_if_key(parts[1], addr))
		msg.send(fail_silently=fail_silently)


def send_mail_template(subject, template, addr_from, addr_to, 
	fail_silently=False, attachments=None, context=None):
	"""
	send email rendering text and html versions for the specified template name
	using the context dictionary passed in
	"""

	if context is None:
		context = {}

	# loads a template passing in vars as context
	render = lambda type: loader.get_template("email_extras/%s.%s" % 
		(template, type)).render(Context(context))
	
	send_mail(subject, render("txt"), addr_from, addr_to, 
		fail_silently=fail_silently, attachments=attachments, 
		body_html=render("html"))
