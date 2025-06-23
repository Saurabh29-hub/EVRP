import React from "react";

const NodeInputs = ({ selectedNode, onClose, updatePickupDelivery }) => {
  return (
    <div style={{ position: "absolute", top: 150, left: 20, background: "#eee", padding: 10, border: "1px solid gray" }}>
      <h4>Update Customer</h4>
      <label>Pickup:</label>
      <input
        type="number"
        value={selectedNode.data.pickup}
        onChange={(e) =>
          updatePickupDelivery(selectedNode.id, {
            ...selectedNode.data,
            pickup: Number(e.target.value),
          })
        }
      />
      <br />
      <label>Delivery:</label>
      <input
        type="number"
        value={selectedNode.data.delivery}
        onChange={(e) =>
          updatePickupDelivery(selectedNode.id, {
            ...selectedNode.data,
            delivery: Number(e.target.value),
          })
        }
      />
      <br />
      <button onClick={onClose}>Done</button>
    </div>
  );
};

export default NodeInputs;
