import React from "react";
import { Handle, Position } from "reactflow";

const StationNode = ({ data }) => {
  return (
    <div
      style={{
        padding: 10,
        border: "2px solid #1e90ff",
        borderRadius: 8,
        backgroundColor: "#e6f0ff",
        textAlign: "center",
        fontSize: 12,
        minWidth: 120,
        position: "relative",
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: "#1e90ff" }}
      />

      <div><strong>{data.label}</strong></div>
      <div>🛠 Ports: {data.ports}</div>

      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: "#1e90ff" }}
      />
    </div>
  );
};

export default StationNode;
