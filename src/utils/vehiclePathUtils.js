export const drawVehiclePaths = (paths, setEdges, colorList = []) => {

  const generatedEdges = [];
  paths.forEach((vehicle, index) => {
    const { vehicleId, path } = vehicle;
    const color = colorList[index % colorList.length] || "#00bcd4";

    for (let i = 0; i < path.length - 1; i++) {
      generatedEdges.push({
        id: `vehicle-${vehicleId}-edge-${i}`,
        source: path[i],
        target: path[i + 1],
        animated: true,
        label: vehicleId,
        style: {
          stroke: color,
          strokeWidth: 2,
        },
      });
    }
  });

  // Add to existing edges
  setEdges((prevEdges) => [...prevEdges, ...generatedEdges]);
};
  