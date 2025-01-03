import dontmanage


def execute():
	"""
	Migrate Raven User to have the "type" field set for older Raven Users
	"""

	users = dontmanage.get_all("Raven User", filters={"type": ["in", ["", None]]}, pluck="name", limit=5)

	for user in users:
		dontmanage.db.set_value("Raven User", user, "type", "User")

	dontmanage.db.commit()
