import json

import dontmanage
from dontmanage import _

from raven.utils import is_channel_member


@dontmanage.whitelist(methods=["POST"])
def react(message_id: str, reaction: str):
	"""
	API to react/unreact to a message.
	Checks if the user can react to the message
	First checks if the user has already reacted to the message.
	If yes, then unreacts (deletes), else reacts (creates).
	"""

	# PERF: No need for permission checks here.
	# The permission checks are done in the controller method for the doctype

	channel_id = dontmanage.get_cached_value("Raven Message", message_id, "channel_id")
	channel_type = dontmanage.get_cached_value("Raven Channel", channel_id, "type")

	if channel_type == "Private":

		if not is_channel_member(channel_id):
			dontmanage.throw(_("You do not have permission to react to this message"), dontmanage.PermissionError)

	reaction_escaped = reaction.encode("unicode-escape").decode("utf-8").replace("\\u", "")
	user = dontmanage.session.user
	existing_reaction = dontmanage.db.exists(
		"Raven Message Reaction",
		{"message": message_id, "owner": user, "reaction_escaped": reaction_escaped},
	)

	if existing_reaction:
		# Why not use dontmanage.db.delete?
		# Because dontmanage won't run the controller method for 'after_delete' if we do so,
		# and we need to calculate the new count of reactions for our message
		dontmanage.get_doc("Raven Message Reaction", existing_reaction).delete(delete_permanently=True)

	else:
		dontmanage.get_doc(
			{
				"doctype": "Raven Message Reaction",
				"reaction": reaction,
				"message": message_id,
				"channel_id": channel_id,
				"owner": user,
			}
		).insert(ignore_permissions=True)
	return "Ok"


def calculate_message_reaction(message_id):

	reactions = dontmanage.get_all(
		"Raven Message Reaction",
		fields=["owner", "reaction"],
		filters={"message": message_id},
		order_by="reaction_escaped",
	)

	total_reactions = {}

	for reaction_item in reactions:
		if reaction_item.reaction in total_reactions:
			existing_reaction = total_reactions[reaction_item.reaction]
			new_users = existing_reaction.get("users")
			new_users.append(reaction_item.owner)
			total_reactions[reaction_item.reaction] = {
				"count": existing_reaction.get("count") + 1,
				"users": new_users,
				"reaction": reaction_item.reaction,
			}

		else:
			total_reactions[reaction_item.reaction] = {
				"count": 1,
				"users": [reaction_item.owner],
				"reaction": reaction_item.reaction,
			}
	channel_id = dontmanage.get_cached_value("Raven Message", message_id, "channel_id")
	dontmanage.db.set_value(
		"Raven Message",
		message_id,
		"message_reactions",
		json.dumps(total_reactions),
		update_modified=False,
	)
	dontmanage.publish_realtime(
		"message_reacted",
		{
			"channel_id": channel_id,
			"sender": dontmanage.session.user,
			"message_id": message_id,
			"reactions": json.dumps(total_reactions),
		},
		doctype="Raven Channel",
		docname=channel_id,  # Adding this to automatically add the room for the event via DontManage
		after_commit=False,
	)
