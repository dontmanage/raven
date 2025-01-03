import dontmanage
import dontmanage.utils
from dontmanage import _
from dontmanage.twofactor import two_factor_is_enabled
from dontmanage.utils.html_utils import get_icon_html
from dontmanage.utils.oauth import get_oauth2_authorize_url, get_oauth_keys
from dontmanage.utils.password import get_decrypted_password

no_cache = True


@dontmanage.whitelist(allow_guest=True)
def get_context():

	redirect_to = dontmanage.local.request.args.get("redirect-to")
	context = {"provider_logins": []}
	providers = dontmanage.get_all(
		"Social Login Key",
		filters={"enable_social_login": 1},
		fields=["name", "client_id", "base_url", "provider_name", "icon", "redirect_url"],
		order_by="name",
	)

	for provider in providers:
		client_secret = get_decrypted_password("Social Login Key", provider.name, "client_secret")
		if not client_secret:
			continue

		icon = {"html": "", "src": "", "alt": ""}
		if provider.icon:
			if provider.provider_name == "Custom":
				icon["html"] = get_icon_html(provider.icon, small=True)
			else:
				icon["src"] = provider.icon
				icon["alt"] = provider.provider_name

		if provider.client_id and provider.base_url and get_oauth_keys(provider.name):

			context["provider_logins"].append(
				{
					"name": provider.name,
					"provider_name": provider.provider_name,
					"auth_url": get_oauth2_authorize_url(provider.name, redirect_to),
					"redirect_to": provider.redirect_url,
					"icon": icon,
				}
			)
			context["social_login"] = True

	login_label = [_("Email")]
	if dontmanage.utils.cint(dontmanage.get_system_settings("allow_login_using_mobile_number")):
		login_label.append(_("Mobile"))

	if dontmanage.utils.cint(dontmanage.get_system_settings("allow_login_using_user_name")):
		login_label.append(_("Username"))

	context["login_label"] = f" {_('/')} ".join(login_label)

	context["login_with_email_link"] = dontmanage.get_system_settings("login_with_email_link")
	context["two_factor_is_enabled"] = two_factor_is_enabled()
	context["disable_signup"] = dontmanage.get_website_settings("disable_signup")

	return context
