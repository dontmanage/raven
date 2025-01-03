import dontmanage
from dontmanage import _

from raven.utils import get_channel_members


@dontmanage.whitelist()
def create_event(
	channel: str, subject: str, duration: str, google_calendar: str = None, description: str = None
):
	"""
	Create a new event with Google Meet enabled.
	Once created, send a message to the channel with the event details.
	"""
	# Create a new event
	if isinstance(duration, str):
		duration = int(duration)

	if not google_calendar:
		google_calendar = dontmanage.get_value(
			"Google Calendar", {"enable": 1, "user": dontmanage.session.user}, "name"
		)

	if not google_calendar:
		dontmanage.throw(_("Google Calendar not found for the current user"))

	event = dontmanage.get_doc(
		{
			"doctype": "Event",
			"subject": subject,
			"starts_on": dontmanage.utils.now_datetime(),
			"ends_on": dontmanage.utils.add_to_date(dontmanage.utils.now_datetime(), minutes=duration),
			"description": description,
			"send_reminder": 0,
		}
	)

	event.save()

	add_participants(event, channel)

	event = update_meeting_details(event, google_calendar)

	# Send a message to the channel
	doc = dontmanage.get_doc(
		{
			"doctype": "Raven Message",
			"channel_id": channel,
			"text": '<p>To join the meeting, click on the link below: <a href="{0}">{0}</a></p>'.format(
				event.google_meet_link
			),
			"message_type": "Text",
			"hide_link_preview": 1,
			"link_doctype": "Event",
			"link_document": event.name,
		}
	)
	doc.insert()

	return event


def add_participants(event, channel):
	"""
	Add participants to the event and send a message to the channel with the event details.
	"""
	participants = [dontmanage.session.user]
	channel_type = dontmanage.get_cached_value("Raven Channel", channel, "type")

	if channel_type == "Open":
		# Only add the current user
		pass

	else:

		members_map = get_channel_members(channel)

		members = list(members_map.keys())

		for member in members:
			if member not in participants:
				participants.append(member)

	for participant in participants:
		contact_name = dontmanage.db.exists("Contact", {"user": participant})
		if contact_name:
			dontmanage.get_doc(
				{
					"doctype": "Event Participants",
					"reference_doctype": "Contact",
					"reference_docname": contact_name,
					"email": participant,
					"parent": event.name,
					"parenttype": "Event",
					"parentfield": "event_participants",
				}
			).save()


def update_meeting_details(event, calendar):
	event.reload()
	event.update(
		{
			"sync_with_google_calendar": 1,
			"add_video_conferencing": 1,
			"google_calendar": calendar,
		}
	)
	event.save()
	event.reload()

	return event
