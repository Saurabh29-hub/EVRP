export const generateId = (prefix) =>
    `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  