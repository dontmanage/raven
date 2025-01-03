# Copyright (c) 2023, The Commit Company and contributors
# For license information, please see license.txt

import dontmanage
from dontmanage import _
from dontmanage.model.document import Document

from raven.utils import delete_channel_members_cache, is_channel_member


class RavenChannel(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from dontmanage.types import DF

		channel_description: DF.SmallText | None
		channel_name: DF.Data
		is_ai_thread: DF.Check
		is_archived: DF.Check
		is_direct_message: DF.Check
		is_dm_thread: DF.Check
		is_self_message: DF.Check
		is_synced: DF.Check
		is_thread: DF.Check
		last_message_details: DF.JSON | None
		last_message_timestamp: DF.Datetime | None
		linked_doctype: DF.Link | None
		linked_document: DF.DynamicLink | None
		openai_thread_id: DF.Data | None
		thread_bot: DF.Link | None
		type: DF.Literal["Private", "Public", "Open"]
		workspace: DF.Link | None
	# end: auto-generated types

	def on_trash(self):
		# delete all members when channel is deleted
		dontmanage.db.delete("Raven Channel Member", {"channel_id": self.name})

		# delete all messages when channel is deleted
		dontmanage.db.delete("Raven Message", {"channel_id": self.name})

		# delete all reactions when channel is deleted
		dontmanage.db.delete("Raven Message Reaction", {"channel_id": self.name})

		# Delete the pinned channels
		dontmanage.db.delete("Raven Pinned Channels", {"channel_id": self.name})

		delete_channel_members_cache(self.name)

		# If the channel was a thread, (i.e. a message exists with the same name), remove the 'is_thread' flag from the message
		if self.is_thread and dontmanage.db.exists("Raven Message", {"name": self.name}):
			message_channel_id = dontmanage.get_cached_value("Raven Message", self.name, "channel_id")
			dontmanage.db.set_value("Raven Message", self.name, "is_thread", 0)
			# Update the message which used to be a thread
			dontmanage.publish_realtime(
				"message_edited",
				{
					"channel_id": message_channel_id,
					"sender": dontmanage.session.user,
					"message_id": self.name,
					"message_details": {
						"is_thread": 0,
					},
				},
				doctype="Raven Channel",
				docname=message_channel_id,
			)

	def after_insert(self):
		"""
		After inserting a channel, we need to check if it is a direct message channel or not.

		If it is a direct message channel, we can add both the users as members.

		If it is a self message channel, we will add only the same user as a member.

		For all other channels, we will add the current user as a member if it is not created by a bot.
		If it is created by a bot, we will add the bot as a member.
		"""
		# add current user as channel member
		if not dontmanage.flags.in_install and not self.flags.do_not_add_member:

			if self.is_direct_message == 1:
				# Add both users as members
				raven_users = self.channel_name.split(" _ ")
				unique_raven_users = list(set(raven_users))
				self.add_members(unique_raven_users)
			else:
				# Can ignore permissions here because the user who creates the channel should be an admin of the channel
				dontmanage.get_doc(
					{
						"doctype": "Raven Channel Member",
						"channel_id": self.name,
						"user_id": dontmanage.session.user,
						"is_admin": 1,
					}
				).insert(ignore_permissions=True)

	def validate(self):
		# If the user trying to modify the channel is not the owner or channel member, then don't allow
		old_doc = self.get_doc_before_save()

		if self.is_direct_message == 1:
			if old_doc:
				if old_doc.get("channel_name") != self.channel_name:
					dontmanage.throw(
						_("You cannot change the name of a direct message channel"),
						dontmanage.ValidationError,
					)

		if not self.is_dm_thread and not self.is_direct_message:
			# If it's not a direct message channel, it needs a workspace
			if not self.workspace:
				dontmanage.throw(_("You need to specify a workspace for this channel"), dontmanage.ValidationError)

		if old_doc and old_doc.get("is_archived") != self.is_archived:
			if dontmanage.db.exists(
				"Raven Channel Member",
				{"channel_id": self.name, "user_id": dontmanage.session.user, "is_admin": 1},
			):
				pass
			elif dontmanage.session.user == "Administrator":
				pass
			else:
				dontmanage.throw(
					_("You don't have permission to archive/unarchive this channel"),
					dontmanage.PermissionError,
				)
		if not self.flags.is_created_by_bot:
			if self.type == "Private" or self.type == "Public":
				if (
					self.owner == dontmanage.session.user
					and dontmanage.db.count("Raven Channel Member", {"channel_id": self.name}) <= 1
				):
					pass
				elif dontmanage.db.exists(
					"Raven Channel Member", {"channel_id": self.name, "user_id": dontmanage.session.user}
				):
					pass
				elif dontmanage.session.user == "Administrator":
					pass
				else:
					dontmanage.throw(_("You don't have permission to modify this channel"), dontmanage.PermissionError)

		# Check if this channel exists in the current workspace
		if self.workspace and self.flags.in_insert:
			if dontmanage.db.exists(
				"Raven Channel", {"channel_name": self.channel_name, "workspace": self.workspace}
			):
				dontmanage.throw(
					_("A channel with this name already exists in this workspace."), dontmanage.ValidationError
				)

	def before_validate(self):
		if self.is_self_message == 1:
			self.is_direct_message = 1

		if self.is_direct_message == 1:
			self.type = "Private"
		if self.is_direct_message == 0:
			self.channel_name = self.channel_name.strip().lower().replace(" ", "-")

		if not self.is_direct_message and not self.workspace and not self.is_dm_thread:
			workspaces = dontmanage.get_all("Raven Workspace")
			if len(workspaces) == 1:
				self.workspace = workspaces[0].name

	def add_members(self, members, is_admin=0):
		# members is a list of Raven User IDs
		for member in members:
			doc = dontmanage.db.exists(
				"Raven Channel Member",
				{"channel_id": self.name, "user_id": member},
			)
			if doc:
				continue
			else:
				channel_member = dontmanage.get_doc(
					{
						"doctype": "Raven Channel Member",
						"channel_id": self.name,
						"user_id": member,
						"is_admin": is_admin,
					}
				)
				channel_member.insert(ignore_permissions=True)

	def autoname(self):
		if self.is_direct_message == 0 and self.is_thread == 0:
			# Add workspace name to the channel name
			self.name = self.workspace + "-" + self.channel_name.strip().lower().replace(" ", "-")
		elif self.is_thread:
			self.name = self.channel_name
