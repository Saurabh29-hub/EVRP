import React from "react";
import { Handle, Position } from "reactflow";

const DepotNode = ({ data }) => {
  return (
    <div
      style={{
        padding: 10,
        border: "2px solid #2e8b57",
        borderRadius: 8,
        backgroundColor: "#eafaf1",
        textAlign: "center",
        fontSize: 12,
        minWidth: 120,
        position: "relative",
      }}
    >
      {/* INCOMING EDGE */}
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: "#2e8b57" }}
      />

      <div><strong>{data.label}</strong></div>
      <div>🚚 Vehicles: {data.vehicles}</div>

      {/* OUTGOING EDGE */}
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: "#2e8b57" }}
      />
    </div>
  );
};

export default DepotNode;
