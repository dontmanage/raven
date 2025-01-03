# Copyright (c) 2024, The Commit Company and contributors
# For license information, please see license.txt

# import dontmanage
from dontmanage.model.document import Document


class RavenPinnedChannels(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from dontmanage.types import DF

		channel_id: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	pass
