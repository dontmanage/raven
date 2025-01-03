import dontmanage


def set_user_active():
	# Set the user's session ID in the cache
	dontmanage.cache().set_value(
		f"user_session_{dontmanage.session.user}", dontmanage.session.user, expires_in_sec=900
	)


def set_user_inactive():
	# Remove the user's session ID from the cache
	dontmanage.cache().delete_key(f"user_session_{dontmanage.session.user}")


@dontmanage.whitelist()
def get_active_users():
	# Get all the cache keys that match the pattern 'user_session_*'
	user_session_keys = dontmanage.cache().get_keys("user_session_*")
	# Decode the keys and split them to get the key name
	decoded_keys = [key.decode("utf-8").split("|")[1] for key in user_session_keys]
	# Get the user IDs from the cache
	user_ids = [dontmanage.cache().get_value(key) for key in decoded_keys]

	return user_ids


@dontmanage.whitelist()
def refresh_user_active_state(deactivate=False):
	if isinstance(deactivate, str):
		deactivate = True if deactivate.lower() == "true" else False
	if deactivate:
		set_user_inactive()
	else:
		set_user_active()

	# // nosemgrep This has to be published to all the users
	dontmanage.publish_realtime(
		"raven:user_active_state_updated",
		{"user": dontmanage.session.user, "active": not deactivate},
	)  # nosemgrep

	return "ok"
