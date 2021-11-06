(function () {
    function createApplication() {
        let app = Vue.createApp({setup () {return {}}});
        app.use(Quasar);

        app.component("airsec-app", {
            template: `
                <div>
                    <beacons></beacons>
                </div>
            `
        });

        app.component("beacons", {
            template: `
                <div>
                    <div class="q-pa-md">
                        <q-table
                        title="Unauthorized"
                        :rows="unauthorizedBeacons"
                        :columns="columns"
                        row-key="bssid"
                        :selected-rows-label="getSelectedString"
                        selection="multiple"
                        v-model:selected="selected"
                        :loading="loading">
                            <template v-slot:top>
                                <q-btn color="primary" :disable="loading" label="Authorize" @click="authorizeSelection" />
                            </template>
                        </q-table>
                    </div>

                    <div class="q-pa-md">
                        <q-table
                        title="Authorized Beacons"
                        :rows="authorizedBeacons"
                        :columns="columns"
                        row-key="bssid"
                        :selected-rows-label="getSelectedString"
                        selection="multiple"
                        v-model:selected="selected"
                        :loading="loading">
                        </q-table>
                    </div>
                </div>
            `,
            getSelectedString: function () {
                console.log("Called")
            },
            data: function () {
                return {
                    beacons: [],
                    columns: [
                        {name: "last-seen", align: "center", label: "Last Seen", field: "time", sortable: true},
                        {name: "bssid", align: "center", label: "BSSID", field: "bssid", sortable: true},
                        {name: "ssid", align: "center", label: "SSID", field: "ssid", sortable: true},
                        {name: "rssi", align: "center", label: "RSSI", field: "rssi", sortable: true},
                    ],
                    authorizedBeacons: [],
                    unauthorizedBeacons: [],
                    selected: [],
                    loading: false,
                    polling: null
                }
            },
            methods: {
                authorizeSelection: async function () {
                    let req_data = [];
                    for (let i of this.selected) {
                        req_data.push({bssid: i.bssid});
                    }

                    let resp = await window.fetch("/api/v1/allowed-beacons", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({beacons: req_data})
                    });
                    await this.loadData();
                },
                loadData: async function () {
                    let resp = await window.fetch("/api/v1/traffic");
                    let allBeacons = await resp.json();

                    resp = await window.fetch("/api/v1/allowed-beacons");
                    let data = await resp.json()
                    let validBSSIDs = data.beacons.map((b) => b.bssid);

                    let result = {authorized: [], unauthorized: []};
                    allBeacons.beacons.reduce(function(prev, current, idx) {
                        if (validBSSIDs.includes(current.bssid)) {
                            prev.authorized.push(current)
                        }
                        else {
                            prev.unauthorized.push(current);
                        }

                        return result;
                    }, result);

                    this.authorizedBeacons = result.authorized;
                    this.unauthorizedBeacons = result.unauthorized;
                },
                setupPolling: function () {
                    if (this.polling == null) {
                        this.polling = setInterval(this.loadData.bind(this), 5000);
                    }
                },
                cancelPolling: function () {
                    if (this.polling != null) {
                        clearInterval(this.polling);
                        this.polling = null;
                    }
                }
            },
            mounted: async function() {
                this.loading = true;
                await this.loadData();
                setTimeout(() => this.loading = false, 250);
                this.setupPolling();
            },
            unmounted: function () { this.cancelPolling(); }

        });

        app.mount("#app");
    }

    document.addEventListener("DOMContentLoaded", createApplication);
}());