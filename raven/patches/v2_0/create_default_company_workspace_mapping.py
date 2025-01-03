import dontmanage


def execute():
	# Add rows to Raven Settings for the default workspace mapping for all companies
	raven_settings = dontmanage.get_doc("Raven Settings")

	if not raven_settings.auto_create_department_channel:
		return

	# Get all companies if they exist - check if DontManageErp is installed
	if "dontmanageerp" in dontmanage.get_installed_apps():
		companies = dontmanage.get_all("Company", pluck="name")

	for company in companies:
		raven_settings.append(
			"company_workspace_mapping", {"company": company, "raven_workspace": "Raven"}
		)

	raven_settings.save()
