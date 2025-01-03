# Copyright (c) 2024, The Commit Company and contributors
# For license information, please see license.txt

import dontmanage
from dontmanage import _
from dontmanage.model.document import Document


class RavenPollVote(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from dontmanage.types import DF

		option: DF.Data
		poll_id: DF.Link
		user_id: DF.Link
	# end: auto-generated types

	def before_insert(self):
		# check if the poll is still open
		poll = dontmanage.get_cached_doc("Raven Poll", self.poll_id)
		if poll.is_disabled:
			dontmanage.throw(_("This poll is closed."))

		# check if the option is valid
		if not dontmanage.db.exists(
			"Raven Poll Option",
			{
				"parent": self.poll_id,
				"name": self.option,
			},
		):
			dontmanage.throw(_("Invalid option selected."))

		# check if the user has already voted for this option in this poll
		if dontmanage.db.exists(
			"Raven Poll Vote",
			{
				"poll_id": self.poll_id,
				"user_id": self.user_id,
				"option": self.option,
			},
		):
			dontmanage.throw(_("You have already voted for this option."))

	def validate(self):
		# Check if the user_id is the same as the logged in user
		if self.user_id != dontmanage.session.user:
			dontmanage.throw(_("You can only vote for yourself."))

	def after_insert(self):
		update_poll_votes(self.poll_id)

	def after_delete(self):
		update_poll_votes(self.poll_id)


def update_poll_votes(poll_id):
	poll = dontmanage.get_cached_doc("Raven Poll", poll_id)
	# get votes for each option
	poll_votes = dontmanage.get_all(
		"Raven Poll Vote",
		filters={"poll_id": poll_id},
		fields=["option", "count(name) as votes"],
		group_by="option",
	)

	# update the votes for each option in the poll
	for option in poll.options:
		option.votes = 0
		for vote in poll_votes:
			if option.name == vote.option:
				option.votes = vote.votes
				break

	poll.save(ignore_permissions=True)
