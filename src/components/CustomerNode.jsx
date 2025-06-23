import React from "react";
import { Handle, Position } from "reactflow";

const CustomerNode = ({ data }) => {
  return (
    <div
      style={{
        padding: 10,
        border: "2px solid #555",
        borderRadius: 8,
        backgroundColor: "#f4f4f4",
        textAlign: "center",
        fontSize: 12,
        minWidth: 120,
        position: "relative", // Required for handle positioning
      }}
    >
      {/* INCOMING CONNECTION */}
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: "#555" }}
      />

      <div><strong>{data.label}</strong></div>
      {data.pickup !== undefined && <div>📦 Pickup: {data.pickup}</div>}
      {data.delivery !== undefined && <div>📬 Delivery: {data.delivery}</div>}

      {/* OUTGOING CONNECTION */}
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: "#555" }}
      />
    </div>
  );
};

export default CustomerNode;
