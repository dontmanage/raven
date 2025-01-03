# Copyright (c) 2024, The Commit Company (Algocode Technologies Pvt. Ltd.) and contributors
# For license information, please see license.txt

import dontmanage
from dontmanage.model.document import Document


class RavenWorkspace(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from dontmanage.types import DF

		can_only_join_via_invite: DF.Check
		description: DF.SmallText | None
		logo: DF.AttachImage | None
		type: DF.Literal["Public", "Private"]
		workspace_name: DF.Data
	# end: auto-generated types

	def after_insert(self):
		if not dontmanage.flags.in_patch:
			self.create_member_for_owner()

	def on_trash(self):
		# Delete all members when the workspace is deleted
		dontmanage.db.delete("Raven Workspace Member", {"workspace": self.name})
		# Delete all channels when the workspace is deleted
		channels = dontmanage.db.get_all("Raven Channel", {"workspace": self.name})
		for channel in channels:
			# use delete doc to delete the channel ,it's members and messages
			dontmanage.delete_doc("Raven Channel", channel.name)

	def create_member_for_owner(self):
		member = dontmanage.new_doc("Raven Workspace Member")
		member.workspace = self.name
		member.user = self.owner
		member.is_admin = True
		member.insert(ignore_permissions=True)
