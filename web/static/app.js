const mapConfig = JSON.parse(document.getElementById("map-config").textContent);
const map = L.map("map").setView([42.36, -71.095], 13);
L.tileLayer(mapConfig.tile_url, {
  maxZoom: 19,
  attribution: mapConfig.attribution
}).addTo(map);

const markerLayer = L.layerGroup().addTo(map);

function markerIcon(direction) {
  const className = Number(direction) === 1 ? "marker inbound" : "marker outbound";
  return L.divIcon({ className: "", html: `<div class="${className}"></div>`, iconSize: [18, 18] });
}

function escapeText(value) {
  return String(value ?? "-").replace(/[&<>'"]/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
  })[character]);
}

function formatTimestamp(value) {
  if (value === null || value === undefined || value === "") return "-";
  const timestamp = new Date(value);
  return Number.isNaN(timestamp.getTime()) ? String(value) : timestamp.toLocaleString();
}

function renderVehicles(vehicles) {
  markerLayer.clearLayers();
  const table = document.getElementById("vehicle-table");
  table.innerHTML = "";
  const bounds = [];

  vehicles.forEach(vehicle => {
    const latitude = Number(vehicle.latitude);
    const longitude = Number(vehicle.longitude);
    if (Number.isFinite(latitude) && Number.isFinite(longitude)) {
      const marker = L.marker([latitude, longitude], { icon: markerIcon(vehicle.direction_id) })
        .bindPopup(`<strong>${escapeText(vehicle.vehicle_id)}</strong><br>Trip ${escapeText(vehicle.trip_id)}<br>Stop ${escapeText(vehicle.stop_sequence)}`);
      marker.addTo(markerLayer);
      bounds.push([latitude, longitude]);
    }

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeText(vehicle.vehicle_id)}</td>
      <td>${escapeText(vehicle.trip_id)}</td>
      <td>${escapeText(vehicle.direction_id)}</td>
      <td>${escapeText(vehicle.stop_sequence)}</td>
      <td>${escapeText(vehicle.occupancy_status)}</td>
      <td>${escapeText(formatTimestamp(vehicle.observed_at))}</td>`;
    table.appendChild(row);
  });

  if (bounds.length) map.fitBounds(bounds, { padding: [25, 25], maxZoom: 15 });
}

async function refresh() {
  const health = document.getElementById("health");
  try {
    const [vehicleResponse, statsResponse] = await Promise.all([
      fetch("/api/vehicles?limit=100"),
      fetch("/api/stats")
    ]);
    if (!vehicleResponse.ok || !statsResponse.ok) throw new Error("The backend is not ready");

    const vehiclePayload = await vehicleResponse.json();
    const stats = await statsResponse.json();
    renderVehicles(vehiclePayload.data || []);
    document.getElementById("vehicle-count").textContent = stats.latest_vehicle_count ?? 0;
    document.getElementById("observation-count").textContent = stats.observation_count ?? 0;
    document.getElementById("event-count").textContent = stats.cdc_event_count ?? 0;
    document.getElementById("last-updated").textContent = formatTimestamp(stats.latest_observation?.observed_at);
    health.textContent = `Pipeline connected (${stats.data_mode || "unknown"})`;
    health.classList.remove("error");
  } catch (error) {
    health.textContent = "Waiting for pipeline";
    health.classList.add("error");
    console.error(error);
  }
}

document.getElementById("refresh").addEventListener("click", refresh);
refresh();
setInterval(refresh, 10000);
