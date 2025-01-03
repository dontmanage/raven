import * as React from "react";
import { App } from "./App";
import { createRoot } from "react-dom/client";


class RavenChat {
	constructor({ wrapper }) {
		this.$wrapper = $(wrapper);

		this.init();
	}

	init() {
		this.setup_app();
	}

	setup_app() {
		// create and mount the react app
		const root = createRoot(this.$wrapper.get(0));
		root.render(<App />);
		this.$raven_chat = root;
	}
}

dontmanage.provide("dontmanage.ui");
dontmanage.ui.RavenChat = RavenChat;
export default RavenChat;