(function () {

    const chartColor = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000'];

    function createApplication() {
        let app = Vue.createApp({setup () {return {}}});
        app.use(Quasar);

        app.component("airsec-app", {
            data: function () {
                return {
                    isOpen: false,
                    bssids: null
                }
            },
            template: `
                <div>
                    <beacons @show-rssi="onShowRSSI"></beacons>
                    <rssi-chart @close="onCloseRSSI"
                                v-bind:bssids="bssids"
                                v-if="isOpen">
                    </rssi>
                </div>
            `,
            methods: {
                onShowRSSI: function (bssids) {
                    if (Array.isArray(bssids) && bssids.length > 0) {
                        this.bssids = bssids;
                        this.isOpen = true;
                    }
                },
                onCloseRSSI: function () {
                    this.isOpen = false;
                    this.bssids = null;
                }
            }
        });

        app.component("beacons", {
            template: `
                <div>
                    <div class="q-pa-md">
                        <q-table
                        title="Evil Twins"
                        :rows="evilTwins"
                        :columns="columns"
                        row-key="bssid"
                        :selected-rows-label="getSelectedString"
                        selection="multiple"
                        v-model:selected="selected"
                        :loading="loading">
                            <template v-slot:top>
                                <div class="row col-12 justify-between">
                                    <div class="q-table__title">Evil Twins</div>
                                    <q-btn color="primary" 
                                            :disable="this.selected == 0" 
                                            label="View RSSI" 
                                            @click="showRSSIChart" />
                                </div>
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
                            <template v-slot:top>
                                <div class="row col-12 justify-between">
                                    <div class="q-table__title">Authorized Beacons</div>
                                    <q-btn color="primary" 
                                           :disable="this.selected == 0" 
                                            label="View RSSI" @click="showRSSIChart" />
                                </div>
                            </template>
                        </q-table>
                    </div>

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
                                <div class="row col-12 justify-between">
                                    <div class="q-table__title">Unauthorized Beacons</div>
                                    <div>
                                        <q-btn color="primary"
                                            style="margin-right: 0.5em"
                                            :disable="this.selected == 0"
                                            label="View RSSI"
                                            @click="showRSSIChart" />
                                        <q-btn color="primary"
                                            :disable="loading"
                                            label="Authorize"
                                            @click="authorizeSelection" />
                                    </div>
                                </div>
                            </template>
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
                        {
                            name: "last-seen",
                            align: "center",
                            label: "Last Seen",
                            field: "time",
                            sortable: true,
                            format: function(val) {
                                return moment(val).format("DD MMM Y HH:mm:ss");
                            }
                        },
                        {name: "bssid", align: "center", label: "BSSID", field: "bssid", sortable: true},
                        {name: "ssid", align: "center", label: "SSID", field: "ssid", sortable: true},
                        {name: "channel", align: "center", label: "Channel", field: "channel", sortable: true},
                        {name: "rssi", align: "center", label: "RSSI", field: "rssi", sortable: true},
                    ],
                    authorizedBeacons: [],
                    unauthorizedBeacons: [],
                    evilTwins: [],
                    selected: [],
                    loading: false,
                    polling: null
                }
            },
            methods: {
                showRSSIChart: function () {
                    let bssids = this.selected.map(s => s.bssid);
                    this.$emit("show-rssi", bssids)
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

                    resp = await window.fetch("/api/v1/evil-twins");
                    data = await resp.json();
                    let evilTwins = data.beacons;

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
                    this.evilTwins = evilTwins;
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
                this.cancelPolling();
                this.$emit("close");
            }
        });

        app.component("rssi-chart", {
            props: ["bssids"],
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
                    let query = this.bssids.map(b => "bssid=" + b).join('&');
                    let resp = await window.fetch(`/api/v1/rssi?${query}`);
                    let body = await resp.json();

                    this.chart.data.datasets.forEach(function (b) {
                        if (body.hasOwnProperty(b.label)) {
                            b.data = body[b.label];
                        }
                    });

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
                            datasets: this.bssids.map((b, i) => {
                                return {
                                    label: b,
                                    data: [],
                                    fill: false,
                                    tension: 0.1,
                                    borderColor: chartColor[i % chartColor.length]
                                };
                            })
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
            beforeUnmount: function () {
                this.clearPolling();
            }
        });

        app.mount("#app");
    }

    document.addEventListener("DOMContentLoaded", createApplication);
}());
