export const updateEdge = (setEdges, edgeData, setShowEdgePrompt, resetEdgeData) => {
    const { source, target, distance } = edgeData;
    if (!source || !target || !distance) {
      alert("Please provide valid edge details.");
      return;
    }
  
    setEdges((eds) => [
      ...eds,
      {
        id: `edge-${source}-${target}`,
        source,
        target,
        label: `${distance}`,
        data: { distance: Number(distance) },
      },
    ]);
  
    setShowEdgePrompt(false);
    resetEdgeData();
  };
  
  export const genRandomEdges = async (nodesList, updateEdgeFn) => {
    for (let i = 0; i < nodesList.length; i++) {
      for (let j = i + 1; j < nodesList.length; j++) {
        if (Math.random() > 0.5) {
          const distance = Math.floor(Math.random() * 10) + 20;
          await updateEdgeFn(nodesList[i].id, nodesList[j].id, distance);
        }
      }
    }
  };
  