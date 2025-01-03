import dontmanage


@dontmanage.whitelist(allow_guest=True)
def get_client_id():
	return dontmanage.db.get_single_value("Raven Settings", "oauth_client")
