/** @odoo-module */

import { patch } from '@web/core/utils/patch';

import { WebClient } from '@web/webclient/webclient';
import { AppsBar } from '@g2p_muk_web_appsbar/webclient/appsbar/appsbar';

patch(WebClient, {
    components: {
        ...WebClient.components,
        AppsBar,
    },
});
