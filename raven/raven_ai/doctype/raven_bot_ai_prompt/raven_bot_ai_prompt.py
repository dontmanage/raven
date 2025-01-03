# Copyright (c) 2024, The Commit Company (Algocode Technologies Pvt. Ltd.) and contributors
# For license information, please see license.txt

# import dontmanage
from dontmanage.model.document import Document


class RavenBotAIPrompt(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from dontmanage.types import DF

		is_global: DF.Check
		naming_series: DF.Literal["PR-.#####."]
		prompt: DF.SmallText
		raven_bot: DF.Link | None
	# end: auto-generated types

	pass
