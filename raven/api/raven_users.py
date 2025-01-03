import json

import dontmanage
from dontmanage import _
from dontmanage.utils.caching import redis_cache


@dontmanage.whitelist(methods=["GET"])
def get_current_raven_user():
	"""
	Fetches the current user's Raven User profile
	"""

	# Check if the user is a Raven User and has he "Raven User" role
	# If not, then throw an error
	if not dontmanage.has_permission("Raven User"):
		dontmanage.throw(
			_(
				"You do not have a <b>Raven User</b> role. Please contact your administrator to add your user profile as a <b>Raven User</b>."
			),
			title=_("Insufficient permissions. Please contact your administrator."),
		)

	return dontmanage.get_cached_doc("Raven User", {"user": dontmanage.session.user})


@dontmanage.whitelist(methods=["POST"])
def update_raven_user(**args):
	"""
	Updates the current user's Raven User profile
	"""

	dontmanage.get_doc("Raven User", {"user": dontmanage.session.user}).update(args).save()


@dontmanage.whitelist()
@dontmanage.read_only()
def get_list():
	"""
	Fetches list of all users who have the role: Raven User
	"""

	# Check if the user is a Raven User and has he "Raven User" role
	# If not, then throw an error
	if not dontmanage.has_permission("Raven User"):
		dontmanage.throw(
			_(
				"You do not have a <b>Raven User</b> role. Please contact your administrator to add your user profile as a <b>Raven User</b>."
			),
			title=_("Insufficient permissions. Please contact your administrator."),
		)

	# Get users is cached since this won't change frequently
	return get_users()


@redis_cache()
def get_users():
	users = dontmanage.db.get_all(
		"Raven User",
		fields=[
			"full_name",
			"user_image",
			"name",
			"first_name",
			"enabled",
			"type",
			"availability_status",
			"custom_status",
		],
		order_by="full_name",
	)
	return users


@dontmanage.whitelist()
def is_user_on_leave(user: str):
	"""
	If the user is on leave, return True
	"""
	# Check if DontManageHR is installed
	if not "hrms" in dontmanage.get_installed_apps():
		return False

	employee = dontmanage.db.exists("Employee", {"user_id": user})

	if employee:
		# Check if attendance today is marked as "On Leave"
		attendance = dontmanage.db.exists(
			"Attendance",
			{
				"employee": employee,
				"status": "On Leave",
				"attendance_date": dontmanage.utils.today(),
				"docstatus": 1,
			},
		)

		if attendance:
			return True

	return False


@dontmanage.whitelist(methods=["POST"])
def add_users_to_raven(users):

	if isinstance(users, str):
		users = json.loads(users)

	failed_users = []
	success_users = []

	for user in users:
		user_doc = dontmanage.get_doc("User", user)

		if user_doc.role_profile_name:
			failed_users.append(user_doc)

		elif hasattr(user_doc, "role_profiles") and len(user_doc.role_profiles) > 0:
			failed_users.append(user_doc)
		else:
			user_doc.append("roles", {"role": "Raven User"})
			user_doc.save()
			success_users.append(user_doc)

	return {"success_users": success_users, "failed_users": failed_users}


@dontmanage.whitelist(methods=["POST"])
def invite_user(email: str, first_name: str = None, last_name: str = None):
	"""
	Invites a user to Raven. If the user exists in DontManage, they are added to Raven.
	"""

	existing_user = dontmanage.db.exists("User", {"email": email})

	if existing_user:
		user_doc = dontmanage.get_doc("User", existing_user)
		if user_doc.role_profile_name:
			dontmanage.throw(_("User has a role profile set. Please set the role to Raven User manually."))

		elif hasattr(user_doc, "role_profiles") and len(user_doc.role_profiles) > 0:
			dontmanage.throw(_("User has a role profile set. Please set the role to Raven User manually."))

		user_doc.append("roles", {"role": "Raven User"})
		user_doc.save()
		return {"success": True, "message": "User added to Raven"}
	else:
		user_doc = dontmanage.new_doc("User")
		user_doc.email = email
		user_doc.first_name = first_name
		user_doc.last_name = last_name
		user_doc.send_welcome_email = 1
		user_doc.append("roles", {"role": "Raven User"})
		user_doc.insert()
		return {"success": True, "message": "User added to Raven"}
