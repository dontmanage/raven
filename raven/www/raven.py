import json
import re

import dontmanage
import dontmanage.sessions
from dontmanage import _
from dontmanage.utils.telemetry import capture

no_cache = 1

SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>")
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>")


def get_context(context):
	csrf_token = dontmanage.sessions.get_csrf_token()
	# Manually commit the CSRF token here
	dontmanage.db.commit()  # nosemgrep

	if dontmanage.session.user == "Guest":
		boot = dontmanage.website.utils.get_boot_data()
	else:
		try:
			boot = dontmanage.sessions.get()
		except Exception as e:
			raise dontmanage.SessionBootFailed from e

	boot["push_relay_server_url"] = dontmanage.conf.get("push_relay_server_url")

	# add server_script_enabled in boot
	if "server_script_enabled" in dontmanage.conf:
		enabled = dontmanage.conf.server_script_enabled
	else:
		enabled = True
	boot["server_script_enabled"] = enabled

	boot_json = dontmanage.as_json(boot, indent=None, separators=(",", ":"))
	boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)

	boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)
	boot_json = json.dumps(boot_json)

	context.update(
		{"build_version": dontmanage.utils.get_build_version(), "boot": boot_json, "csrf_token": csrf_token}
	)

	app_name = dontmanage.get_website_settings("app_name") or dontmanage.get_system_settings("app_name")

	if app_name and app_name != "DontManage":
		context["app_name"] = app_name + " | " + "Raven"

	else:
		context["app_name"] = "Raven"

	if dontmanage.session.user != "Guest":
		capture("active_site", "raven")

		context[
			"preload_links"
		] = """
			<link rel="preload" href="/api/method/dontmanage.auth.get_logged_user" as="fetch" crossorigin="use-credentials">
			<link rel="preload" href="/api/method/raven.api.workspaces.get_list" as="fetch" crossorigin="use-credentials">
			<link rel="preload" href="/api/method/raven.api.raven_users.get_list" as="fetch" crossorigin="use-credentials">
			<link rel="preload" href="/api/method/raven.api.raven_channel.get_all_channels?hide_archived=false" as="fetch" crossorigin="use-credentials">
			"""
	else:
		context["preload_links"] = ""

	return context


@dontmanage.whitelist(methods=["POST"], allow_guest=True)
def get_context_for_dev():
	if not dontmanage.conf.developer_mode:
		dontmanage.throw(_("This method is only meant for developer mode"))
	return json.loads(get_boot())


def get_boot():
	try:
		boot = dontmanage.sessions.get()
	except Exception as e:
		raise dontmanage.SessionBootFailed from e

	boot["push_relay_server_url"] = dontmanage.conf.get("push_relay_server_url")
	boot_json = dontmanage.as_json(boot, indent=None, separators=(",", ":"))
	boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)

	boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)
	boot_json = json.dumps(boot_json)

	return boot_json