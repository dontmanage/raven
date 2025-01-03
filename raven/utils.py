import dontmanage


def track_channel_visit(channel_id, user=None, commit=False, publish_event_for_user=False):
	"""
	Track the last visit of the user to the channel.
	If the user is not a member of the channel, create a new member record
	"""

	if not user:
		user = dontmanage.session.user

	# Get the channel member record
	channel_member = get_channel_member(channel_id, user)

	if channel_member:
		# Update the last visit
		dontmanage.db.set_value(
			"Raven Channel Member", channel_member["name"], "last_visit", dontmanage.utils.now()
		)

	# Else if the user is not a member of the channel and the channel is open, create a new member record
	elif dontmanage.get_cached_value("Raven Channel", channel_id, "type") == "Open":
		dontmanage.get_doc(
			{
				"doctype": "Raven Channel Member",
				"channel_id": channel_id,
				"user_id": dontmanage.session.user,
				"last_visit": dontmanage.utils.now(),
			}
		).insert()

	# Need to commit the changes to the database if the request is a GET request
	if commit:
		dontmanage.db.commit()  # nosempgrep

	if publish_event_for_user:
		dontmanage.publish_realtime(
			"raven:unread_channel_count_updated",
			{"channel_id": channel_id, "sent_by": dontmanage.session.user},
			user=user,
		)


# Workspace Members
def get_workspace_members(workspace_id: str):
	"""
	Gets all members of a workspace from the cache
	"""
	cache_key = f"raven:workspace_members:{workspace_id}"

	data = dontmanage.cache.get_value(cache_key)
	if data:
		return data

	members = dontmanage.db.get_all(
		"Raven Workspace Member",
		filters={"workspace": workspace_id},
		fields=["name", "user", "is_admin"],
	)

	data = {member.user: member for member in members}
	dontmanage.cache.set_value(cache_key, data)
	return data


def delete_workspace_members_cache(workspace_id: str):
	cache_key = f"raven:workspace_members:{workspace_id}"
	dontmanage.cache.delete_value(cache_key)


def get_workspace_member(workspace_id: str, user: str = None) -> dict:
	"""
	Get the workspace member ID
	"""
	if not user:
		user = dontmanage.session.user

	return get_workspace_members(workspace_id).get(user, None)


def is_workspace_member(workspace_id: str, user: str = None) -> bool:
	"""
	Check if a user is a member of a workspace
	"""
	if not user:
		user = dontmanage.session.user

	all_members = get_workspace_members(workspace_id)

	return user in all_members


def get_channel_members(channel_id: str):
	"""
	Gets all members of a channel from the cache as a map - also includes the type of the user
	"""
	cache_key = f"raven:channel_members:{channel_id}"

	data = dontmanage.cache.get_value(cache_key)
	if data:
		return data

	raven_channel_member = dontmanage.qb.DocType("Raven Channel Member")
	raven_user = dontmanage.qb.DocType("Raven User")

	query = (
		dontmanage.qb.from_(raven_channel_member)
		.join(raven_user)
		.on(raven_channel_member.user_id == raven_user.name)
		.select(
			raven_channel_member.name,
			raven_channel_member.user_id,
			raven_channel_member.is_admin,
			raven_channel_member.allow_notifications,
			raven_user.type,
		)
		.where(raven_channel_member.channel_id == channel_id)
	)

	members = query.run(as_dict=True)

	data = {member.user_id: member for member in members}
	dontmanage.cache.set_value(cache_key, data)
	return data


def delete_channel_members_cache(channel_id: str):
	cache_key = f"raven:channel_members:{channel_id}"
	dontmanage.cache.delete_value(cache_key)


def get_channel_member(channel_id: str, user: str = None) -> dict:
	"""
	Get the channel member ID
	"""

	if not user:
		user = dontmanage.session.user

	all_members = get_channel_members(channel_id)

	return all_members.get(user, None)


def is_channel_member(channel_id: str, user: str = None) -> bool:
	"""
	Check if a user is a member of a channel
	"""
	if not user:
		user = dontmanage.session.user

	return user in get_channel_members(channel_id)


def get_raven_user(user_id: str) -> str:
	"""
	Get the Raven User ID of a user
	"""
	# TODO: Run this via cache
	return dontmanage.db.get_value("Raven User", {"user": user_id}, "name")