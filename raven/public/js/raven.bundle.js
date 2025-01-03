$(document).on('app_ready', function () {
    if (dontmanage.boot.show_raven_chat_on_desk && dontmanage.user.has_role("Raven User")) {

        // If on mobile, do not show the chat
        if (dontmanage.is_mobile()) {
            return;
        }
        let main_section = $(document).find('.main-section');

        // Add bottom padding to the main section
        main_section.css('padding-bottom', '60px');

        let chat_element = $(document.createElement('div'));
        chat_element.addClass('raven-chat');

        main_section.append(chat_element);

        dontmanage.require("raven_chat.bundle.jsx").then(() => {
            dontmanage.raven_chat = new dontmanage.ui.RavenChat({
                wrapper: chat_element,
            });
        });
    }

});
import './templates/send_message.html';
import './timeline_button';
