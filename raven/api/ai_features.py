import dontmanage

from raven.ai.handler import get_variables_for_instructions


@dontmanage.whitelist()
def get_instruction_preview(instruction):
	"""
	Function to get the rendered instructions for the bot
	"""
	instructions = dontmanage.render_template(instruction, get_variables_for_instructions())
	return instructions


@dontmanage.whitelist()
def get_saved_prompts(bot: str = None):
	"""
	API to get the saved prompt for a user/bot/global
	"""
	or_filters = [["is_global", "=", 1], ["owner", "=", dontmanage.session.user]]

	prompts = dontmanage.get_list(
		"Raven Bot AI Prompt", or_filters=or_filters, fields=["name", "prompt", "is_global", "raven_bot"]
	)

	# Order by ones with the given bot
	prompts = sorted(prompts, key=lambda x: x.get("raven_bot") == bot, reverse=True)

	return prompts
