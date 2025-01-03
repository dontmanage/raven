import dontmanage
from dontmanage import _


@dontmanage.whitelist()
def are_push_notifications_enabled() -> bool:
	try:
		return dontmanage.db.get_single_value("Push Notification Settings", "enable_push_notification_relay")
	except dontmanage.DoesNotExistError:
		# push notifications are not supported in the current framework version
		return False


@dontmanage.whitelist(methods=["POST"])
def toggle_push_notification_for_channel(member: str, allow_notifications: 0 | 1) -> None:
	if are_push_notifications_enabled():
		member_doc = dontmanage.get_doc("Raven Channel Member", member)
		if member_doc:
			member_doc.allow_notifications = allow_notifications
			member_doc.save()

			return member_doc
	else:
		dontmanage.throw(_("Push notifications are not supported in the current framework version"))
