import React, { useState } from "react";

const ControlsPanel = ({
  customerCount,
  chargingCount,
  setCustomerCount,
  setChargingCount,
  generateNodes,
  generateEdges,
  exportToJson,
  onAddEdgeClick,
  exportGraphWithLabel,
}) => {

  const [showDropdown, setShowDropdown] = useState(false);
  const postOptions = ["CSP(using Z3)", "Heuristic(A*)", "Meta Heuristic(Genetic Algo)"];

  return (
    <div style={{ marginBottom: "10px" }}>
      <label>Customers:</label>
      <input
        type="number"
        value={customerCount}
        onChange={(e) => setCustomerCount(Number(e.target.value))}
        style={{ marginRight: "10px", width: "60px" }}
      />

      <label>Stations:</label>
      <input
        type="number"
        value={chargingCount}
        onChange={(e) => setChargingCount(Number(e.target.value))}
        style={{ marginRight: "10px", width: "60px" }}
      />

      <button onClick={generateNodes}>Generate Nodes</button>
      <button onClick={generateEdges}>Generate Edges</button>
      <button onClick={exportToJson}>Export JSON</button>
      <div style={{ position: "relative" }}>
        <button onClick={() => setShowDropdown(!showDropdown)}>
          Find Path ⬇️
        </button>
        {showDropdown && (
          <div style={{
            position: "absolute",
            top: "100%",
            left: 0,
            backgroundColor: "#fff",
            border: "1px solid #ccc",
            borderRadius: "4px",
            boxShadow: "0px 2px 5px rgba(0,0,0,0.15)",
            zIndex: 10,
          }}>
            {postOptions.map((label) => (
              <div
                key={label}
                onClick={() => {
                  setShowDropdown(false);
                  exportGraphWithLabel(label); // call with label
                }}
                style={{ padding: "8px 12px", cursor: "pointer" }}
              >
                {label}
              </div>
            ))}
          </div>
        )}
      </div>
      <button onClick={onAddEdgeClick}>Add Edge Manually</button>
      {/* <button onClick={onAddNodeClick}>➕ Add Node</button>
      <button onClick={onAddEdgeClick}>🔗 Add Edge Manually</button> */}
    </div>
  );
};

export default ControlsPanel;
