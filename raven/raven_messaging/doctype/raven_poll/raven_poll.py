# Copyright (c) 2024, The Commit Company and contributors
# For license information, please see license.txt

import dontmanage
from dontmanage.model.document import Document


class RavenPoll(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from dontmanage.types import DF

		from raven.raven_messaging.doctype.raven_poll_option.raven_poll_option import RavenPollOption

		is_anonymous: DF.Check
		is_disabled: DF.Check
		is_multi_choice: DF.Check
		options: DF.Table[RavenPollOption]
		question: DF.SmallText
		total_votes: DF.Int
	# end: auto-generated types

	def before_validate(self):
		# Total_votes is the sum of all votes in the poll per user
		poll_votes = dontmanage.get_all(
			"Raven Poll Vote", filters={"poll_id": self.name}, fields=["user_id"], group_by="user_id"
		)

		# count the number of unique users who voted
		self.total_votes = len(poll_votes) if poll_votes else 0

	def on_trash(self):
		# Delete all poll votes
		dontmanage.db.delete("Raven Poll Vote", {"poll_id": self.name})

	pass
