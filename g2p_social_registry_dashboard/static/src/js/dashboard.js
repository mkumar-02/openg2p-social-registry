/** @odoo-module **/
import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const actionRegistry = registry.category("actions");

class SRDashboard extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this._fetch_data();
    }

    _fetch_data() {
        // Add loading spinners to tiles
        $("#my_individuals").html('<div class="loader"></div>');
        $("#my_groups").html('<div class="spinner-border" role="status"></div>');
        $("#gender_pie_chart_container").html('<div class="spinner-border" role="status"></div>');
        $("#age_bar_chart_container").html('<div class="spinner-border" role="status"></div>');

        this.orm.call("res.partner", "get_dashboard_data", [], {}).then((result) => {
            // Update tiles with fetched data
            $("#my_individuals").html("<span>" + result.total_individuals + "</span>");
            $("#my_groups").html("<span>" + result.total_groups + "</span>");
            $("#gender_pie_chart_container").html(
                '<canvas id="gender_pie_chart" width="150" height="150"></canvas>'
            );
            this.renderGenderPieChart(result.gender_distribution);

            // Update age distribution chart
            $("#age_bar_chart_container").html(
                '<canvas id="age_bar_chart" width="400" height="200"></canvas>'
            );
            this.renderAgeBarChart(result.age_distribution);
        });
    }

    renderGenderPieChart(data) {
        const ctx = document.getElementById("gender_pie_chart").getContext("2d");
        new Chart(ctx, {
            type: "pie",
            data: {
                labels: ["Male", "Female"],
                datasets: [
                    {
                        data: [data.male, data.female],
                        backgroundColor: ["#4e73df", "#1cc88a"],
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "top",
                    },
                },
            },
        });
    }

    renderAgeBarChart(data) {
        const ctx = document.getElementById("age_bar_chart").getContext("2d");
        const labels = Object.keys(data);
        const values = Object.values(data);

        new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Age Distribution",
                        data: values,
                        backgroundColor: "#4e73df",
                        borderColor: "#4e73df",
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
                plugins: {
                    legend: {
                        position: "top",
                    },
                },
            },
        });
    }
}

SRDashboard.template = "g2p_social_registry_dashboard.dashboard_template";
actionRegistry.add("sr_dashboard_tag", SRDashboard);
