import { useState } from 'react';

const DEFAULT_DSL_CODE = `# size: 100 x 100

// Bedroom
Room {
    id: "bedroom";
    label: "Bedroom";
    size: [30, 25];
    position: [0, 0];
}

Room {
    id: "living";
    label: "Living-Room";
    size: [40, 30];
    position: [0, 25];
}

Room {
    id: "bathroom";
    label: "Bathroom";
    size: [20, 15];
    position: [30, 0];
}

Room {
    id: "kitchen";
    label: "Kitchen";
    size: [30, 10];
    position: [30, 15];
}

Window {
    id: "window_east";
    position: [0, 10];
    width: 1;
    height: 4;
}

// Bed
Bed {
    id: "bed";
    position: [10, 1];
    width: 10;
    height: 15;
}

// Door
Door {
    id: "bedroom_door";
    position: [7, 25];
    width: 0.4;
    height: 0.15;
    direction: "up";
}

// Bedside Table
Table {
    id: "bedside_table";
    position: [2.5, 1];
    width: 5;
    height: 5;
}

Chair {
    id: "sofa";
    position: [3.5, 7];
    width: 3;
    height: 1.5;
}`;

export const useDslState = () => {
  const [dslCode, setDslCode] = useState<string>(DEFAULT_DSL_CODE);

  const generateRandomDslCode = () => {
    const roomTypes = ['Bedroom', 'Living-Room', 'Bathroom', 'Kitchen', 'Dining-Room'];
    const furnitureTypes = ['Bed', 'Table', 'Chair', 'Stairs', 'Elevator'];
    const directions = ['up', 'down', 'left', 'right'];
    
    const gridCols = 2 + Math.floor(Math.random() * 2);
    const gridRows = 2 + Math.floor(Math.random() * 2);
    const roomWidth = 30;
    const roomHeight = 25;
    let newCode = '# size: 100 x 100\n\n';
    let roomCount = 0;
    for (let row = 0; row < gridRows; row++) {
      for (let col = 0; col < gridCols; col++) {
        if (roomCount >= 5) break;
        const roomType = roomTypes[roomCount % roomTypes.length];
        const posX = col * (roomWidth + 2);
        const posY = row * (roomHeight + 2);
        newCode += `Room {\n`;
        newCode += `    id: "${roomType.toLowerCase().replace(/ /g, '-')}_${roomCount}";\n`;
        newCode += `    label: "${roomType}";\n`;
        newCode += `    size: [${roomWidth}, ${roomHeight}];\n`;
        newCode += `    position: [${posX}, ${posY}];\n`;
        newCode += `}\n\n`;
        roomCount++;
      }
    }
    newCode += `Window {\n    id: "window_0";\n    position: [2, 2];\n    width: 2;\n    height: 3;\n}\n\n`;
    newCode += `Door {\n    id: "door_0";\n    position: [${roomWidth - 2}, 0];\n    width: 0.4;\n    height: 0.15;\n    direction: "down";\n}\n\n`;
    for (let i = 0; i < Math.min(roomCount, 3); i++) {
      const furnitureType = furnitureTypes[Math.floor(Math.random() * furnitureTypes.length)];
      const posX = (i % gridCols) * (roomWidth + 2) + 5;
      const posY = Math.floor(i / gridCols) * (roomHeight + 2) + 5;
      const width = 4 + Math.floor(Math.random() * 4);
      const height = 2 + Math.floor(Math.random() * 4);
      newCode += `${furnitureType} {\n`;
      newCode += `    id: "${furnitureType.toLowerCase()}_${i}";\n`;
      newCode += `    position: [${posX}, ${posY}];\n`;
      newCode += `    width: ${width};\n`;
      newCode += `    height: ${height};\n`;
      newCode += `}\n\n`;
    }
    setDslCode(newCode);
  };

  return {
    dslCode,
    setDslCode,
    generateRandomDslCode
  };
}; 