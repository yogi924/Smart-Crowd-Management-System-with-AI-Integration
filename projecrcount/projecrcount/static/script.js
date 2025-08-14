mapboxgl.accessToken = "pk.eyJ1Ijoic3ViaGFtcHJlZXQiLCJhIjoiY2toY2IwejF1MDdodzJxbWRuZHAweDV6aiJ9.Ys8MP5kVTk5P9V2TDvnuDg";

let map, directions, userMarker;

// Initialize map
function setupMap(userCoords) {
  map = new mapboxgl.Map({
    container: "map",
    style: "mapbox://styles/mapbox/streets-v11",
    center: userCoords,
    zoom: 15,
  });

  directions = new MapboxDirections({
    accessToken: mapboxgl.accessToken,
    unit: "metric",
    profile: "mapbox/walking",
    interactive: false,
  });

  map.addControl(new mapboxgl.NavigationControl());
  map.addControl(directions, "top-left");

  userMarker = new mapboxgl.Marker({ color: "red" })
    .setLngLat(userCoords)
    .addTo(map);
}

// Fetch data and update both counts and route
async function refreshAll() {
  const selectedGate = document.getElementById("gate-select").value;
  const selectedCounts = Array.from(document.querySelectorAll('.gate-list input:checked'))
    .map(cb => cb.value);

  try {
    const [countRes, locRes] = await Promise.all([
      fetch("/get_counts"),
      fetch("/get_gate_locations"),
    ]);
    const counts = await countRes.json();
    const locations = await locRes.json();

    // Update crowd count display
    const countDiv = document.getElementById("count-display");
    countDiv.innerHTML = selectedCounts.length > 0
      ? selectedCounts.map(id => `Gate ${id}: ${counts[id] || 0} people`).join("<br>")
      : "<em>No gates selected for count display</em>";

    // Decide which gate to route to
    let routeGate = selectedGate;
    if (!routeGate) {
      routeGate = Object.keys(counts).reduce((a, b) =>
        counts[a] < counts[b] ? a : b
      );
    }

    const dest = [locations[routeGate].lng, locations[routeGate].lat];
    directions.setOrigin(userMarker.getLngLat().toArray());
    directions.setDestination(dest);

    // Add gate markers
    Object.entries(locations).forEach(([gateId, loc]) => {
      new mapboxgl.Marker({ color: "#3D8BFF" })
        .setLngLat([loc.lng, loc.lat])
        .setPopup(new mapboxgl.Popup().setHTML(`<strong>Gate ${gateId}</strong>`))
        .addTo(map);
    });

  } catch (err) {
    console.error("Failed to fetch data:", err);
  }
}

// Run once with geolocation
navigator.geolocation.getCurrentPosition(
  (pos) => {
    const userCoords = [pos.coords.longitude, pos.coords.latitude];
    setupMap(userCoords);
    refreshAll();

    // Refresh crowd data every 2 seconds
    setInterval(refreshAll, 2000);

    // Attach change listeners
    document.querySelectorAll(".gate-list input, #gate-select").forEach(el =>
      el.addEventListener("change", refreshAll)
    );
  },
  (err) => {
    console.error("Geolocation failed", err);
    alert("Geolocation is required.");
  },
  { enableHighAccuracy: true }
);

// Manual trigger
function updateRoute() {
  refreshAll();
}
