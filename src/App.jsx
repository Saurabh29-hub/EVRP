import React, { useCallback, useState } from "react";
import { useNodesState, useEdgesState, addEdge } from "reactflow";
import "reactflow/dist/style.css";

import ControlsPanel from "./components/ControlsPanel";
import EdgePrompt from "./components/EdgePrompt";
import GraphView from "./components/GraphView";

import { generateNodes } from "./utils/nodeUtils";
import { updateEdge, genRandomEdges } from "./utils/edgeUtils";
import { exportToJson, exportGraph } from "./utils/dataExport";

const App = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const [customerCount, setCustomerCount] = useState(3);
  const [chargingCount, setChargingCount] = useState(2);

  const [showEdgePrompt, setShowEdgePrompt] = useState(false);
  const [edgeData, setEdgeData] = useState({ source: "", target: "", distance: "" });

  const [selectedNode, setSelectedNode] = useState(null);

  const [editValues, setEditValues] = useState({}); // data being edite 
  
  const exportGraphWithLabel = (label) => {
    exportGraph(nodes, edges, setEdges, label); // pass label
  };

  const handleNodeDoubleClick = (event, node) => {
    setSelectedNode(node);
    setEditValues({ ...node.data }); // preload editable values
  };

  const handleGenerateNodes = () => {
    generateNodes(customerCount, chargingCount, setNodes);
    setEdges([]);
  };

  const handleGenerateEdges = () => {
    genRandomEdges(nodes, (source, target, distance) =>
      updateEdge(setEdges, { source, target, distance }, () => {}, () => {})
    );
  };

  const handleExportToJson = () => exportToJson(nodes, edges);
  const handleExportGraph = () => exportGraph(nodes, edges, setEdges);

  const handleConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const handleNodeClick = (event, node) => {
    if (node.type === "customer") {
      setSelectedNode(node);
    }
  };

  const updatePickupDelivery = (nodeId, newData) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId ? { ...node, data: { ...newData } } : node
      )
    );
  };

  const handleUpdateEdge = () => {
    const { source, target, distance } = edgeData;
    if (!source || !target || !distance) {
      alert("Please fill all edge fields.");
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
    setEdgeData({ source: "", target: "", distance: "" });
  };
   
  // console.log("nodes:", nodes);
  // console.log("allNodeIds:", nodes.map((n) => n.id));

  return (
    <div style={{ padding: "20px" }}>
      <h2>EVRP Visualizer</h2>

      <ControlsPanel
        customerCount={customerCount}
        chargingCount={chargingCount}
        setCustomerCount={setCustomerCount}
        setChargingCount={setChargingCount}
        generateNodes={handleGenerateNodes}
        generateEdges={handleGenerateEdges}
        exportToJson={handleExportToJson}
        exportGraphWithLabel={exportGraphWithLabel}
        // onAddNodeClick={handleAddNode}
        onAddEdgeClick={() => setShowEdgePrompt(true)}
      />

      <GraphView
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={handleConnect}
        // onNodeClick={handleNodeClick}
        onNodeDoubleClick={handleNodeDoubleClick}
      />

    {/* <div style={{ marginTop: "10px" }}>
        <button onClick={() => setShowEdgePrompt(true)}>
            ➕ Add Edge Manually
        </button>
    </div> */}

      {showEdgePrompt && (
        <EdgePrompt
            edgeData={edgeData}
            setEdgeData={setEdgeData}
            updateEdge={handleUpdateEdge}
            closePrompt={() => setShowEdgePrompt(false)}
            nodes={nodes}
        />
      )}

      {/* {selectedNode && (
        <NodeInputs
          selectedNode={selectedNode}
          onClose={() => setSelectedNode(null)}
          updatePickupDelivery={updatePickupDelivery}
        />
      )} */}

      {selectedNode && (
        <div style={{
          position: "absolute",
          top: 100,
          left: 100,
          background: "#fff",
          padding: 20,
          border: "1px solid #ccc",
          borderRadius: 6,
          zIndex: 1000
        }}>
        <h4>Edit {selectedNode.data.label}</h4>

        {selectedNode.type === "customer" && (
          <>
            <label>Pickup:</label>
            <input
              type="number"
              value={editValues.pickup || 0}
              onChange={(e) =>
                setEditValues({ ...editValues, pickup: Number(e.target.value) })
              }
            />
            <br />
            <label>Delivery:</label>
            <input
              type="number"
              value={editValues.delivery || 0}
              onChange={(e) =>
                setEditValues({ ...editValues, delivery: Number(e.target.value) })
              }
            />
          </>
        )}

        {selectedNode.type === "depot" && (
          <>
            <label>Vehicles:</label>
            <input
              type="number"
              value={editValues.vehicles || 0}
              onChange={(e) =>
                setEditValues({ ...editValues, vehicles: Number(e.target.value) })
              }
            />
          </>
        )}

        {selectedNode.type === "station" && (
          <>
            <label>Ports:</label>
            <input
              type="number"
              value={editValues.ports || 0}
              onChange={(e) =>
                setEditValues({ ...editValues, ports: Number(e.target.value) })
              }
            />
          </>
        )}

        <br />
        <button
          onClick={() => {
            setNodes((nodes) =>
              nodes.map((node) =>
                node.id === selectedNode.id
                  ? { ...node, data: { ...node.data, ...editValues } }
                  : node
              )
            );
            setSelectedNode(null);
            setEditValues({});
          }}
        >
          Save
        </button>
        <button onClick={() => setSelectedNode(null)}>Cancel</button>
      </div>
      )}

    </div>
  );
};

export default App;
