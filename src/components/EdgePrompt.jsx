import React from "react";

const EdgePrompt = ({
  edgeData,
  setEdgeData,
  updateEdge,
  closePrompt,
  nodes = [],
}) => {
  return (
    <div style={{
      position: "absolute",
      top: 100,
      left: 20,
      background: "#fff",
      padding: 10,
      border: "1px solid black",
      zIndex: 10,
    }}>
      <h4>Add Edge</h4>

      <label>Source:</label>
      <select
        value={edgeData.source}
        onChange={(e) => setEdgeData({ ...edgeData, source: e.target.value })}
      >
        <option value="">-- Select --</option>
        {nodes.map((node) => (
          <option key={node.id} value={node.id}>
            {node.data?.label || node.id}
          </option>
        ))}
      </select>
      <br />

      <label>Target:</label>
      <select
        value={edgeData.target}
        onChange={(e) => setEdgeData({ ...edgeData, target: e.target.value })}
      >
        <option value="">-- Select --</option>
        {nodes.map((node) => (
          <option key={node.id} value={node.id}>
            {node.data?.label || node.id}
          </option>
        ))}
      </select>
      <br />

      <label>Distance:</label>
      <input
        type="number"
        value={edgeData.distance}
        onChange={(e) => setEdgeData({ ...edgeData, distance: e.target.value })}
      />
      <br />

      <button onClick={updateEdge}>Add</button>
      <button onClick={closePrompt}>Cancel</button>
    </div>
  );
};

export default EdgePrompt;
