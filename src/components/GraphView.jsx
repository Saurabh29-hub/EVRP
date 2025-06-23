import React from "react";
import ReactFlow, { MiniMap, Controls, Background, addEdge } from "reactflow";
import "reactflow/dist/style.css";
import CustomerNode from "../components/CustomerNode";
import StationNode from "../components/StationNode";
import DepotNode from "../components/DepotNode";

export const nodeTypes = {
  customer: CustomerNode,
  station: StationNode,
  depot: DepotNode
};

const GraphView = ({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  onConnect,
  // onNodeClick,
  onNodeDoubleClick,
}) => {
  return (
    <div style={{ height: "600px", border: "1px solid #999", borderRadius: 8 }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        // onNodeClick={onNodeClick}
        onNodeDoubleClick={onNodeDoubleClick}
        fitView
        nodeTypes={nodeTypes}
      >
        
        <MiniMap />
        <Controls />
        <Background />
      </ReactFlow>
      
    </div>
  );
};

export default GraphView;
