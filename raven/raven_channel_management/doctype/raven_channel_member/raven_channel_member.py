# Copyright (c) 2023, The Commit Company and contributors
# For license information, please see license.txt

import dontmanage
from dontmanage import _
from dontmanage.model.document import Document

from raven.notification import subscribe_user_to_topic, unsubscribe_user_to_topic
from raven.utils import delete_channel_members_cache


class RavenChannelMember(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from dontmanage.types import DF

		allow_notifications: DF.Check
		channel_id: DF.Link
		is_admin: DF.Check
		is_synced: DF.Check
		last_visit: DF.Datetime
		linked_doctype: DF.Link | None
		linked_document: DF.DynamicLink | None
		user_id: DF.Link
	# end: auto-generated types

	def before_validate(self):
		self.last_visit = dontmanage.utils.now()

	def validate(self):
		if (
			self.has_value_changed("is_admin")
			and not self.flags.in_insert
			and not self.flags.ignore_permissions
		):
			# Check if the user is an existing admin of the channel
			if not dontmanage.db.exists(
				"Raven Channel Member",
				{"channel_id": self.channel_id, "user_id": dontmanage.session.user, "is_admin": 1},
			):
				dontmanage.throw(
					_("You cannot make yourself an admin of a channel. Please ask another admin to do this."),
					dontmanage.PermissionError,
				)

	def before_insert(self):
		# 1. A user cannot be a member of a channel more than once
		if dontmanage.db.exists(
			"Raven Channel Member", {"channel_id": self.channel_id, "user_id": self.user_id}
		):
			dontmanage.throw(_("You are already a member of this channel"), dontmanage.DuplicateEntryError)
		# if there are no members in the channel, then the member becomes admin
		if dontmanage.db.count("Raven Channel Member", {"channel_id": self.channel_id}) == 0:
			self.is_admin = 1

		self.allow_notifications = 1

	def after_delete(self):

		member_name = dontmanage.get_cached_value("Raven User", self.user_id, "full_name")

		current_user_name = dontmanage.get_cached_value("Raven User", dontmanage.session.user, "full_name")

		# If this was the last member of a private channel, archive the channel
		if (
			dontmanage.db.count("Raven Channel Member", {"channel_id": self.channel_id}) == 0
			and dontmanage.db.get_value("Raven Channel", self.channel_id, "type") == "Private"
		):
			dontmanage.db.set_value("Raven Channel", self.channel_id, "is_archived", 1)

		# If this member was the only admin, then make the next oldest member an admin
		if (
			self.get_admin_count() == 0
			and dontmanage.db.count("Raven Channel Member", {"channel_id": self.channel_id}) > 0
		):
			first_member = dontmanage.db.get_value(
				"Raven Channel Member",
				{"channel_id": self.channel_id},
				["name", "user_id"],
				as_dict=1,
				order_by="creation asc",
			)
			dontmanage.db.set_value("Raven Channel Member", first_member.name, "is_admin", 1)

			first_member_name = dontmanage.get_cached_value("Raven User", first_member.user_id, "full_name")

			# Add a system message to the channel mentioning the new admin
			dontmanage.get_doc(
				{
					"doctype": "Raven Message",
					"channel_id": self.channel_id,
					"message_type": "System",
					"text": f"{member_name} was removed by {current_user_name} and {first_member_name} is the new admin of this channel.",
				}
			).insert(ignore_permissions=True)
		else:
			# If the member who left is the current user, then add a system message to the channel mentioning that the user left
			if member_name == current_user_name:
				# Add a system message to the channel mentioning the member who left
				dontmanage.get_doc(
					{
						"doctype": "Raven Message",
						"channel_id": self.channel_id,
						"message_type": "System",
						"text": f"{member_name} left.",
					}
				).insert(ignore_permissions=True)
			else:
				# Add a system message to the channel mentioning the member who left
				dontmanage.get_doc(
					{
						"doctype": "Raven Message",
						"channel_id": self.channel_id,
						"message_type": "System",
						"text": f"{current_user_name} removed {member_name}.",
					}
				).insert(ignore_permissions=True)

	def on_trash(self):
		unsubscribe_user_to_topic(self.channel_id, self.user_id)
		self.invalidate_channel_members_cache()

	def check_if_user_is_member(self):
		is_member = True
		channel = dontmanage.db.get_value("Raven Channel", self.channel_id, ["type", "owner"], as_dict=True)
		if channel.type == "Private":
			# A user can only add members to a private channel if they are themselves member of the channel or if they are the owner of a new channel
			if (
				channel.owner == dontmanage.session.user
				and dontmanage.db.count("Raven Channel Member", {"channel_id": self.channel_id}) == 0
			):
				# User is the owner of a channel and there are no members in the channel
				pass
			elif dontmanage.db.exists(
				"Raven Channel Member",
				{"channel_id": self.channel_id, "user_id": dontmanage.session.user},
			):
				# User is a member of the channel
				pass
			elif dontmanage.session.user == "Administrator":
				# User is Administrator
				pass
			else:
				is_member = False
		return is_member

	def after_insert(self):
		"""
		Subscribe the user to the topic if the channel is not a DM
		"""
		is_direct_message = dontmanage.get_cached_value(
			"Raven Channel", self.channel_id, "is_direct_message"
		)

		if not is_direct_message and self.allow_notifications:
			subscribe_user_to_topic(self.channel_id, self.user_id)

		if not is_direct_message:

			is_thread = self.is_thread()

			# Send a system message to the channel mentioning the member who joined
			if not is_thread:
				member_name = dontmanage.get_cached_value("Raven User", self.user_id, "full_name")
				if self.user_id == dontmanage.session.user:
					dontmanage.get_doc(
						{
							"doctype": "Raven Message",
							"channel_id": self.channel_id,
							"message_type": "System",
							"text": f"{member_name} joined.",
						}
					).insert(ignore_permissions=True)
				else:
					current_user_name = dontmanage.get_cached_value("Raven User", dontmanage.session.user, "full_name")
					dontmanage.get_doc(
						{
							"doctype": "Raven Message",
							"channel_id": self.channel_id,
							"message_type": "System",
							"text": f"{current_user_name} added {member_name}.",
						}
					).insert(ignore_permissions=True)

		self.invalidate_channel_members_cache()

	def on_update(self):
		"""
		Check if the notification preference is changed and update the subscription
		"""
		old_doc = self.get_doc_before_save()
		if old_doc:
			if old_doc.allow_notifications != self.allow_notifications:
				is_direct_message = dontmanage.get_cached_value(
					"Raven Channel", self.channel_id, "is_direct_message"
				)

				if not is_direct_message:
					if self.allow_notifications:
						subscribe_user_to_topic(self.channel_id, self.user_id)
					else:
						unsubscribe_user_to_topic(self.channel_id, self.user_id)

		if self.has_value_changed("is_admin") and not self.flags.in_insert and not self.is_thread():
			# Send a system message to the channel mentioning the member who became admin
			member_name = dontmanage.get_cached_value("Raven User", self.user_id, "full_name")
			text = (
				f"{member_name} is now an admin." if self.is_admin else f"{member_name} is no longer an admin."
			)
			dontmanage.get_doc(
				{
					"doctype": "Raven Message",
					"channel_id": self.channel_id,
					"message_type": "System",
					"text": text,
				}
			).insert(ignore_permissions=True)

		self.invalidate_channel_members_cache()

	def get_admin_count(self):
		return dontmanage.db.count("Raven Channel Member", {"channel_id": self.channel_id, "is_admin": 1})

	def is_thread(self):
		return dontmanage.get_cached_value("Raven Channel", self.channel_id, "is_thread")

	def invalidate_channel_members_cache(self):
		if not self.flags.ignore_cache_invalidation:
			delete_channel_members_cache(self.channel_id)


def on_doctype_update():
	"""
	Add indexes to Raven Channel Member table
	"""
	# Index the selector (channel or message type) first for faster queries (less rows to sort in the next step)
	dontmanage.db.add_index("Raven Channel Member", ["channel_id", "user_id"])