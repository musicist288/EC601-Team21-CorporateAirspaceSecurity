(function () {
    function createApplication() {
        let app = Vue.createApp({setup () {return {}}});
        app.use(Quasar);

        app.component("airsec-app", {
            data: function () {
                return {
                    isOpen: false,
                    bssid: null
                }
            },
            template: `
                <div>
                    <beacons @show-rssi="onShowRSSI"></beacons>
                    <rssi-chart @close="onCloseRSSI"
                                v-bind:bssid="bssid"
                                v-if="isOpen">
                    </rssi>
                </div>
            `,
            methods: {
                onShowRSSI: function (bssid) {
                    if (bssid) {
                        this.bssid = bssid;
                        this.isOpen = true;
                    }
                },
                onCloseRSSI: function () {
                    this.isOpen = false;
                    this.bssid = null;
                }
            }
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
                        @row-click="unauthorizedClicked"
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
                        @row-click="authorizedClicked"
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
                        {name: "channel", align: "center", label: "Channel", field: "channel", sortable: true},
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
                unauthorizedClicked: function(evt, row, index) {
                    this.$emit("show-rssi", row.bssid);
                },
                authorizedClicked: function(evt, row, index) {
                    this.$emit("show-rssi", row.bssid);
                },
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
            beforeUnmount: function () {
                this.$emit("close");
            },
            unmounted: function () {
                this.cancelPolling();
            }

        });

        app.component("rssi-chart", {
            props: ["bssid"],
            data: function () {
                return { open: true };
            },
            template: `<div>
            <q-dialog @show="dialogShown" @hide="dialogHide" v-model="open">
                <q-card>
                    <q-card-section style="height:500px; width:800px">
                        <canvas class="chart"></canvas>
                    </q-card-section>
                </q-card>
            </q-dialog>
            </div>`,
            methods: {
                fetchData: async function () {
                    let resp = await window.fetch(`/api/v1/rssi?bssid=${this.bssid}`)
                    let body = await resp.json()
                    this.chart.data.datasets[0].data = body.data;
                    this.chart.update();
                },
                setupPolling: function () {
                    this.interval = window.setInterval(this.fetchData.bind(this), 1000);
                },
                clearPolling: function() {
                    if (this.interval) {
                        window.clearInterval(this.interval);
                    }
                },
                dialogShown: function () {
                    const config = {
                        type: 'line',
                        data: {
                            datasets: [{
                                label: this.bssid,
                                data: [],
                                fill: false,
                                borderColor: 'rgb(75, 192, 192)',
                                tension: 0.1
                            }]
                        },
                        options: {
                            parsing: {
                                xAxisKey: 'time',
                                yAxisKey: 'rssi'
                            },
                            scales: {
                                x: {
                                    type: 'timeseries',
                                }
                            }
                        }
                    };

                    let el = document.querySelector("canvas.chart");
                    this.chart = new Chart(el, config);
                    this.setupPolling();
                },
                dialogHide: function () {
                    this.$emit("close");
                }
            },
            mounted: function () {
            },
            umounted: function () {
                this.clearInterval();
            }
        });

        app.mount("#app");
    }

    document.addEventListener("DOMContentLoaded", createApplication);
}());
