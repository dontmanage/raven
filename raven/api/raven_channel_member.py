import dontmanage
from dontmanage import _

from raven.utils import delete_channel_members_cache, get_channel_member, track_channel_visit


@dontmanage.whitelist()
def remove_channel_member(user_id, channel_id):
	# Get raven channel member name where user_id and channel_id match
	member = get_channel_member(channel_id, user_id)
	# Delete raven channel member
	if member:
		dontmanage.delete_doc("Raven Channel Member", member["name"])
	else:
		dontmanage.throw(_("User is not a member of this channel"))

	return True


@dontmanage.whitelist(methods=["POST"])
def track_visit(channel_id):
	"""
	Track the last visit of the user to the channel.
	This is usually called when the user exits the channel (unmounts the component) after loading the latest messages in it.
	"""
	track_channel_visit(channel_id=channel_id, commit=True)
	return True


@dontmanage.whitelist(methods=["POST"])
def add_channel_members(channel_id: str, members: list[str]):
	"""
	Add members to a channel
	"""
	dontmanage.has_permission("Raven Channel", doc=channel_id, ptype="write", throw=True)

	# Since this is a bulk operation, we need to disable cache invalidation (will be handled manually) and ignore permissions (since we already have permission to add members)

	for member in members:
		member_doc = dontmanage.get_doc(
			{"doctype": "Raven Channel Member", "channel_id": channel_id, "user_id": member}
		)
		member_doc.flags.ignore_cache_invalidation = True
		member_doc.insert(ignore_permissions=True)

	delete_channel_members_cache(channel_id)
	return True
