import { generateId } from './idGenerator';

export const getRandomInt = (a, b) =>
  Math.floor(Math.random() * (b - a + 1)) + a;

export const generateNodes = (customerCount, chargingCount, setNodes) => {
  const newNodes = [{
    id: "depot-0",
    type: "depot",
    position: { x: 500, y: 50 },
    data: { label: "Depot", vehicles: getRandomInt(2,4)}
  }];

  for (let i = 0; i < customerCount; i++) {
    newNodes.push({
      id: `customer-${i + 1}`,
      type: "customer",
      position: { x: Math.random() * 800, y: Math.random() * 600 },
      data: { label: `Customer ${i + 1}`, pickup: getRandomInt(20, 30), delivery: getRandomInt(20, 30) },
    });
  }

  for (let i = 0; i < chargingCount; i++) {
    newNodes.push({
      id: `station-${i + 1}`,
      type: "station",
      position: { x: Math.random() * 800, y: Math.random() * 600 },
      data: { label: `Station ${i + 1}`, ports: getRandomInt(2,3)},
    });
  }

  setNodes(newNodes);
  return newNodes;
};
