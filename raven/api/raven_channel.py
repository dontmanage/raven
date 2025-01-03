import dontmanage
from dontmanage import _
from dontmanage.query_builder import Order

from raven.api.raven_users import get_current_raven_user
from raven.utils import get_channel_members, track_channel_visit


@dontmanage.whitelist()
def get_all_channels(hide_archived=True):
	"""
	Fetches all channels where current user is a member - both channels and DMs
	To be used on the web app.
	"""

	if hide_archived == "false":
		hide_archived = False

	# 1. Get "channels" - public, open, private, and DMs
	channels = get_channel_list(hide_archived)

	# 3. For every channel, we need to fetch the peer's User ID (if it's a DM)
	parsed_channels = []
	for channel in channels:
		parsed_channel = {
			**channel,
			"peer_user_id": get_peer_user_id(
				channel.get("name"),
				channel.get("is_direct_message"),
				channel.get("is_self_message"),
			),
		}

		parsed_channels.append(parsed_channel)

	channel_list = [channel for channel in parsed_channels if not channel.get("is_direct_message")]
	dm_list = [channel for channel in parsed_channels if channel.get("is_direct_message")]

	return {"channels": channel_list, "dm_channels": dm_list}


def get_channel_list(hide_archived=False):
	"""
	get List of all channels where current user is a member (all includes public, private, open, and DM channels)
	"""
	channel = dontmanage.qb.DocType("Raven Channel")
	channel_member = dontmanage.qb.DocType("Raven Channel Member")

	workspace_member = dontmanage.qb.DocType("Raven Workspace Member")

	query = (
		dontmanage.qb.from_(channel)
		.select(
			channel.name,
			channel.channel_name,
			channel.type,
			channel.channel_description,
			channel.is_archived,
			channel.is_direct_message,
			channel.is_self_message,
			channel.creation,
			channel.owner,
			channel.last_message_timestamp,
			channel.last_message_details,
			channel.workspace,
		)
		.distinct()
		.left_join(channel_member)
		.on(channel.name == channel_member.channel_id)
		.left_join(workspace_member)
		.on(channel.workspace == workspace_member.workspace)
		.where((channel.is_direct_message == 1) | (workspace_member.user == dontmanage.session.user))
		.where((channel.type != "Private") | (channel_member.user_id == dontmanage.session.user))
		.where(channel.is_thread == 0)
	)

	if hide_archived:
		query = query.where(channel.is_archived == 0)

	query = query.orderby(channel.last_message_timestamp, order=Order.desc)

	return query.run(as_dict=True)


@dontmanage.whitelist()
def get_last_message_details(channel_id: str):

	if dontmanage.has_permission(doctype="Raven Channel", doc=channel_id, ptype="read"):
		last_message_timestamp = dontmanage.get_cached_value(
			"Raven Channel", channel_id, "last_message_timestamp"
		)
		last_message_details = dontmanage.get_cached_value(
			"Raven Channel", channel_id, "last_message_details"
		)

		return {
			"last_message_timestamp": last_message_timestamp,
			"last_message_details": last_message_details,
		}


@dontmanage.whitelist()
def get_channels(hide_archived=False):
	channels = get_channel_list(hide_archived)
	for channel in channels:
		peer_user_id = get_peer_user_id(
			channel.get("name"), channel.get("is_direct_message"), channel.get("is_self_message")
		)
		channel["peer_user_id"] = peer_user_id
		if peer_user_id:
			user_full_name = dontmanage.get_cached_value("User", peer_user_id, "full_name")
			channel["full_name"] = user_full_name
	return channels


def get_peer_user(channel_id: str, is_direct_message: int, is_self_message: bool = False) -> dict:
	"""
	For a given channel, fetches the peer's member object
	"""
	if is_direct_message == 0:
		return None
	if is_self_message:
		return {
			"user_id": dontmanage.session.user,
		}

	members = get_channel_members(channel_id)

	for member in members:
		if member != dontmanage.session.user:
			return members[member]

	return None


def get_peer_user_id(
	channel_id: str, is_direct_message: int, is_self_message: bool = False
) -> str:
	"""
	For a given channel, fetches the user id of the peer
	"""
	peer_user = get_peer_user(channel_id, is_direct_message, is_self_message)
	if peer_user:
		return peer_user.get("user_id")
	return None


@dontmanage.whitelist(methods=["POST"])
def create_direct_message_channel(user_id):
	"""
	Creates a direct message channel between current user and the user with user_id
	The user_id can be the peer or the user themself
	1. Check if a channel already exists between the two users
	2. If not, create a new channel
	3. Check if the user_id is the current user and set is_self_message accordingly
	"""
	# TODO: this logic might break if the user_id changes
	channel_name = dontmanage.db.get_value(
		"Raven Channel",
		filters={
			"is_direct_message": 1,
			"channel_name": [
				"in",
				[dontmanage.session.user + " _ " + user_id, user_id + " _ " + dontmanage.session.user],
			],
		},
		fieldname="name",
	)
	if channel_name:
		return channel_name
	# create direct message channel with user and current user
	else:
		channel = dontmanage.get_doc(
			{
				"doctype": "Raven Channel",
				"channel_name": dontmanage.session.user + " _ " + user_id,
				"is_direct_message": 1,
				"is_self_message": dontmanage.session.user == user_id,
			}
		)
		channel.insert()
		return channel.name


@dontmanage.whitelist(methods=["POST"])
def toggle_pinned_channel(channel_id):
	"""
	Toggles the pinned status of the channel
	"""
	raven_user = get_current_raven_user()
	pinned_channels = raven_user.pinned_channels or []

	is_pinned = False
	for pin in pinned_channels:
		if pin.channel_id == channel_id:
			raven_user.remove(pin)
			is_pinned = True
			break

	if not is_pinned:
		raven_user.append("pinned_channels", {"channel_id": channel_id})

	raven_user.save()

	return raven_user


@dontmanage.whitelist()
def leave_channel(channel_id):
	"""
	Leave a channel
	"""
	members = dontmanage.get_all(
		"Raven Channel Member",
		filters={"channel_id": channel_id, "user_id": dontmanage.session.user},
	)

	for member in members:
		dontmanage.delete_doc("Raven Channel Member", member.name)

	return "Ok"


@dontmanage.whitelist()
def mark_all_messages_as_read(channel_ids: list):
	"""
	Mark all messages in these channels as read
	"""
	user = dontmanage.session.user
	for channel_id in channel_ids:
		track_channel_visit(channel_id, user=user)

	return "Ok"