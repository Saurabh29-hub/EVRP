import { saveAs } from "file-saver";
import {drawVehiclePaths }  from "./vehiclePathUtils";

export const exportToJson = (nodes, edges) => {
  const data = { nodes, edges };
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: "application/json" });
  saveAs(blob, "graph_data.json");
};

export const exportGraph = async (nodes, edges, setEdges, label = "") => {

  const pathColors = ["#e91e63", "#3f51b5", "#4caf50", "#ff9800"];
  // const vehiclePaths = [
  //   {
  //     vehicleId: "EV-1",
  //     path: ["depot-0", "customer-1", "station-2", "customer-2", "depot-0"]
  //   },
  //   {
  //     vehicleId: "EV-2",
  //     path: ["depot-0", "customer-3", "station-1", "customer-1", "depot-0"]
  //   }
  // ];

  const nodeData = nodes.map((node) => ({
    id: node.id,
    type: node.type,
    x: node.position.x,
    y: node.position.y,
    label: node.data.label,
    ...(node.type === "customer" && {
      pickup: node.data.pickup,
      delivery: node.data.delivery,
    }),
  }));

  const edgeData = edges.map((edge) => ({
    source: edge.source,
    target: edge.target,
    distance: edge.data?.distance || 0,
  }));

  // Find the depot node
  const depotNode = nodes.find((node) => node.type === "depot");

  // Get number of vehicles from depot data
  const numVehicles = depotNode?.data?.vehicles || 1;

  // Generate vehicles list
  const vehicles = Array.from({ length: numVehicles }, (_, i) => ({
    id: `EV-${i + 1}`,
    capacity: 100,
    battery_capacity: 200,
    initial_battery: 200,
  }));

  const exportData = {
    label: label,
    nodes: nodeData,
    edges: edgeData,
    vehicles: vehicles,
    charging_stations: [{ id: "station-1", charging_rate: 50, max_ports: 2 }],
    constraints: {
      min_battery_threshold: 0.15,
      time_limit: 8,
      energy_consumption_rate: 0.1,
    },
  };

  try {
    const response = await fetch("http://127.0.0.1:5000/receive_json", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(exportData),
    });

    const result = await response.json();
    const vehiclePaths = result.path;
    console.log("All node IDs:", nodes.map((n) => n.id));
    console.log("Path node IDs:", vehiclePaths.flatMap(v => v.path));
    setEdges((prev) => prev.filter(edge => !edge.id.startsWith("vehicle-")));
    drawVehiclePaths(vehiclePaths, setEdges, pathColors)
    console.log("Server Response:", result);
    alert("Data sent successfully!");

  } catch (error) {
    console.error("Error exporting data:", error);
  }
};
