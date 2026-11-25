
const API = "";

let chart;

// Crear gráfica
function createChart() {
    const ctx = document.getElementById("humidityChart");

    chart = new Chart(ctx, {
        type: "line",

        data: {
            labels: [],
            datasets: [{
                label: "Humedad del suelo (%)",
                data: [],
                borderColor: "#198754",
                backgroundColor: "rgba(25,135,84,0.12)",
                fill: true,
                tension: 0.35
            }]
        },

        options: {
            responsive: true,
            scales: {
                y: {
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

// Consultar estado
async function updateStatus() {
    try {
        const response = await fetch(`${API}/api/status`);

        if (!response.ok) throw new Error("API no disponible");

        const data = await response.json();

        document.getElementById("connectionStatus").textContent =
            "API conectada";

        document.getElementById("connectionDot").style.background =
            "#198754";

        document.getElementById("humidity").textContent =
            data.last_humidity !== null
                ? `${data.last_humidity}%`
                : "--%";

        document.getElementById("deviceStatus").textContent =
            data.device_online ? "En línea" : "Sin datos recientes";

    } catch (error) {
        document.getElementById("connectionStatus").textContent =
            "API desconectada";

        document.getElementById("connectionDot").style.background =
            "#dc3545";
    }
}

// Consultar historial
async function updateHistory() {
    try {
        const response = await fetch(`${API}/api/readings`);

        if (!response.ok) throw new Error("Error al consultar");

        const readings = await response.json();

        const table = document.getElementById("historyTable");

        table.innerHTML = "";

        chart.data.labels = [];
        chart.data.datasets[0].data = [];

        readings.reverse().forEach(reading => {
            const date = new Date(reading.created_at);

            const row = document.createElement("tr");

            [
                reading.id,
                `${reading.humidity}%`,
                reading.soil_raw ?? "--",
                date.toLocaleString()
            ].forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            table.appendChild(row);

            chart.data.labels.push(
                date.toLocaleTimeString()
            );

            chart.data.datasets[0].data.push(
                reading.humidity
            );
        });

        chart.update();

    } catch (error) {
        console.error("Error en historial:", error);
    }
}


// Inicializar
document.addEventListener("DOMContentLoaded", () => {

    initializeTheme();
    createChart();

    updateStatus();
    updateHistory();

    initializePumpControls();
    updatePumpStatus();

    setInterval(updateStatus, 5000);
    setInterval(updateHistory, 10000);
    setInterval(updatePumpStatus, 3000);

});

function initializeTheme() {
    const themeButton = document.getElementById("themeToggle");

    if (!themeButton) return;

    const savedTheme = localStorage.getItem("smartIrrigationTheme");

    if (savedTheme === "dark") {
        document.body.classList.add("dark-mode");
    }

    function updateButton() {
        const isDark = document.body.classList.contains("dark-mode");

        themeButton.textContent = isDark
            ? "☀️ Modo claro"
            : "🌙 Modo oscuro";
    }

    updateButton();

    themeButton.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");

        const isDark = document.body.classList.contains("dark-mode");

        localStorage.setItem(
            "smartIrrigationTheme",
            isDark ? "dark" : "light"
        );

        updateButton();
    });
}
if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(console.error);
}
// Consultar el estado de la bomba
async function updatePumpStatus() {
    try {
        const response = await fetch(`${API}/api/pump`);

        if (!response.ok) {
            throw new Error("No se pudo consultar la bomba");
        }

        const data = await response.json();

        document.getElementById("pumpStatus").textContent =
            data.pump_on ? "Encendida" : "Apagada";

    } catch (error) {
        console.error("Error al consultar la bomba:", error);
    }
}


// Encender o apagar la bomba
async function setPumpState(state) {

    const message = document.getElementById("controlMessage");
    const onButton = document.getElementById("onButton");
    const offButton = document.getElementById("offButton");

    try {
        onButton.disabled = true;
        offButton.disabled = true;

        message.textContent = "Enviando comando...";

        const response = await fetch(`${API}/api/pump`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ state: state })
        });

        if (!response.ok) {
            throw new Error("Error al enviar el comando");
        }

        const data = await response.json();

        document.getElementById("pumpStatus").textContent =
            data.pump_on ? "Encendida" : "Apagada";

        message.textContent = data.message;

    } catch (error) {
        console.error(error);
        message.textContent = "No se pudo controlar la bomba.";

    } finally {
        onButton.disabled = false;
        offButton.disabled = false;
    }
}


// Configurar los botones
function initializePumpControls() {

    document.getElementById("onButton").addEventListener("click", () => {
        setPumpState("on");
    });

    document.getElementById("offButton").addEventListener("click", () => {
        setPumpState("off");
    });

}