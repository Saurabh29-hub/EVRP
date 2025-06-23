import { useState, useCallback } from "react";
import Draggable from "react-draggable";
import {ReactFlow, 
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  MarkerType, 
} from "@xyflow/react";

//import React, { useState } from "react";
import { saveAs } from "file-saver";
import './App.css';

// Function to generate unique IDs
const generateId = (prefix) => `${prefix}-${Math.random().toString(36).substr(2, 9)}`;

const App = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([
    { id: "depot-0", type: "depot", position: { x: 500, y: 50 }, data: { label: "Depot" } },
  ]);

  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [customerCount, setCustomerCount] = useState(0);
  const [chargingCount, setChargingCount] = useState(0);
  const [selectedNode, setSelectedNode] = useState(0);
  const [showEdgePrompt, setShowEdgePrompt] = useState(false);
  const [edgeData, setEdgeData] = useState({ source: "", target: "", distance: "" });
  const [loading, setLoading] = useState(false);

  // Generate customer and charging station nodes
  const generateNodes = async () => {
    const newNodes = [{ id: "depot-0", type: "depot", position: { x: 500, y: 50 }, data: { label: "Depot" } }];

    for (let i = 0; i < customerCount; i++) {
      newNodes.push({
        id: generateId("customer"),
        type: "customer",
        position: { x: Math.random() * 800, y: Math.random() * 600 },
        data: { label: `Customer ${i + 1}`, pickup: 0, delivery: 0 },
      });
    }

    for (let i = 0; i < chargingCount; i++) {
      newNodes.push({
        id: generateId("station"),
        type: "station",
        position: { x: Math.random() * 800, y: Math.random() * 600 },
        data: { label: `Station ${i + 1}` },
      });
    }

    setNodes(newNodes);
    return newNodes;
  };

  // Generate Random number 
  const getRandomInt = (a, b) => {
    return Math.floor(Math.random() * (b - a + 1)) + a;
  }

  // Generate random graph
  const genRandomNodes = async () => {
    setNodes([]);
    setEdges([]);
    setSelectedNode(null);

    setCustomerCount(getRandomInt(1, 5));
    setChargingCount(getRandomInt(1, 3));
    
    // Wait for states to update, then generate new nodes
    setLoading(true);

    // Wait for customer/charging state update (React won't guarantee sync, so pass directly)
    const nodesList = await generateNodes();  // Get nodes
    await genRandomEdges(nodesList);          // Use those nodes for edge generation
    edges.map((edge) => {
      console.log(edge);
    })
    setLoading(false);
  };

  const genRandomEdges = async (nodesList) => {
    for (let i = 0; i < nodesList.length; i++) {
      for (let j = i+1; j < nodesList.length; j++) {
        if (getRandomInt(1, 3) > 1) {
          const node1 = nodesList[i];
          const node2 = nodesList[j];
          const distance = getRandomInt(20, 30);
          await updateEdge(node1.id, node2.id, distance);
        }
      }
    }
  };

  // Open prompt to add an edge
  const openEdgePrompt = () => {
    setShowEdgePrompt(true);
  };

  // Handle edge update
  const updateEdge = async (sourceId = null, targetId = null, distanceVal = null) => {
    const source = sourceId || edgeData?.source;
    const target = targetId || edgeData?.target;
    const distance = distanceVal || edgeData?.distance || 0;
    console.log("source: " + source);
    console.log("Dest: " + target);
    console.log("Distance: " + distance);

    if (!source || !target || !distance) {
      alert("Please select source, destination, and enter a valid distance.");
      return;
    }

    setEdges((eds) => [
      ...eds,
      {
        id: `edge-${source?.id || source}-${target?.id || target}`,
        source: source,
        target: target,
        label: `${distance}`,
        // markerEnd: {
        //   type: MarkerType.ArrowClosed,
        //   width: 20,
        //   height: 20,
        //   color: '#FF0072',
        // },
        // style: {
        //   strokeWidth: 2,
        //   stroke: '#FF0072',
        // },
        data: { distance: Number(distance) },
      },
    ]);

    setShowEdgePrompt(false);
    setEdgeData({ source: "", target: "", distance: "" });
  };

  // Handle node click for pickup/delivery inputs
  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const updateNodeData = (field, value) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === selectedNode?.id
          ? {
              ...node,
              data: { ...node.data, [field]: Number(value) || 0 },
            }
          : node
      )
    );
  
    // Ensure selectedNode is updated properly
    setSelectedNode((prev) => ({
      ...prev,
      data: { ...prev.data, [field]: Number(value) || 0 },
    }));
  };
  
  

  // Update label when clicking "Update"
  const updateCustomerLabel = () => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === selectedNode?.id
          ? {
              ...node,
              data: {
                ...node.data,
                label: ` ${selectedNode.data.label || "N/A"} (${node.data.pickup || 0}, ${node.data.delivery || 0})`,
              },
            }
          : node
      )
    );
  
    // Reset selected node after update
    setSelectedNode(null);
  };
  

  const exportToJson = () => {
    const data = { nodes, edges };
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });

    // Trigger file download
    saveAs(blob, "graph_data.json");
  };

  // Export data to JSON format
  const exportGraph = async () => {
    const nodeData = nodes.map((node) => ({
      id: node.id,
      type: node.type,
      x: node.position.x,
      y: node.position.y,
      label: node.data.label,
      ...(node.type === "customer" && { pickup: node.data.pickup, delivery: node.data.delivery }),
    }));

    const edgeData = edges.map((edge) => ({
      source: edge.source,
      target: edge.target,
      distance: edge.data?.distance || 0,
    }));

    const exportData = {
      nodes: nodeData,
      edges: edgeData,
      vehicles: [
        { id: "EV-1", capacity: 100, battery_capacity: 200, initial_battery: 200 },
      ],
      charging_stations: [
        { id: "station-1", charging_rate: 50, max_ports: 2 },
      ],
      constraints: {
        min_battery_threshold: 0.15,
        time_limit: 8,
        energy_consumption_rate: 0.1,
      },
    };

    console.log("Exported Data:", JSON.stringify(exportData, null, 2));

    // Send data to backend
    try {
      const response = await fetch("http://127.0.0.1:5000/receive_json", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
          },
          body: JSON.stringify(exportData),
      });

      const result = await response.json();
      console.log("Response from server:", result);
      alert("Data sent successfully!");

      // After sending to backend, download JSON file
      // exportToJson(exportData);
    } catch (error) {
      console.error("Error sending data:", error);
    }
  };


  
  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <div className="controls">
        <input
          type="number"
          placeholder="Customers"
          min="0"
          onChange={(e) => setCustomerCount(Number(e.target.value))}
        />
        <input
          type="number"
          placeholder="Charging Stations"
          min="0"
          onChange={(e) => setChargingCount(Number(e.target.value))}
        />
        
        <button onClick={generateNodes}>Generate Nodes</button>
        <button onClick={openEdgePrompt}>Add Edge</button>
        <button onClick={() => { exportGraph();}}>Export JSON</button>
        <button onClick={() => genRandomNodes()}>Generate Graph</button>

      </div>

      {/* Loading Spinner */}
      {loading && (
        <div style={{ textAlign: "center", marginTop: 20 }}>
          <span className="spinner" />
          <p>Generating Graph...</p>
        </div>
      )}

      {/* Edge Prompt */}
      {showEdgePrompt && (
        <div className="edge-prompt">
          <h4>Add Edge</h4>
          <label>Source:</label>
          <select onChange={(e) => setEdgeData({ ...edgeData, source: e.target.value })}>
            <option value="">Select Source</option>
            {nodes.map((node) => (
              <option key={node.id} value={node.id}>
                {node.data.label}
              </option>
            ))}
          </select>

          <label>Destination:</label>
          <select onChange={(e) => setEdgeData({ ...edgeData, target: e.target.value })}>
            <option value="">Select Destination</option>
            {nodes.map((node) => (
              <option key={node.id} value={node.id}>
                {node.data.label}
              </option>
            ))}
          </select>

          <label>Distance:</label>
          <input
            type="number"
            placeholder="Enter distance"
            value={edgeData.distance}
            onChange={(e) => setEdgeData({ ...edgeData, distance: e.target.value })}
          />

          <button onClick={() => updateEdge(edgeData.source, edgeData.target, edgeData.distance)}>Update</button>
          <button onClick={() => setShowEdgePrompt(false)}>Cancel</button>
        </div>
      )}


  

      {/* Pickup & Delivery Form */}
      {selectedNode?.type === "customer" && (
        <div className="node-inputs">
          <h4>{selectedNode.data.label}</h4>
          <input
            type="number"
            placeholder="Pickup amount"
            value={selectedNode?.data?.pickup || ""}
            onChange={(e) => updateNodeData("pickup", Number(e.target.value))}
          />
          <input
            type="number"
            placeholder="Delivery amount"
            value={selectedNode?.data?.delivery || ""}
            onChange={(e) => updateNodeData("delivery", Number(e.target.value))}
          />
          <button onClick={updateCustomerLabel}>Update</button>
        </div>
      )}

      <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onNodeClick={onNodeClick} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default App;
