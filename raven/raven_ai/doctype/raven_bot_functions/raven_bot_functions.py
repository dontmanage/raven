# Copyright (c) 2024, The Commit Company (Algocode Technologies Pvt. Ltd.) and contributors
# For license information, please see license.txt

# import dontmanage
from dontmanage.model.document import Document


class RavenBotFunctions(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from dontmanage.types import DF

		description: DF.SmallText | None
		function: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		type: DF.Data | None
	# end: auto-generated types

	pass
