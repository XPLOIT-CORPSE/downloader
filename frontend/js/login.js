function createRandomShape() {
    const shape = document.createElement("div");
    shape.classList.add("shape");
  
    const size = Math.floor(Math.random() * 100) + 50; // Random size between 50 and 150 pixels
    shape.style.width = size + "px";
    shape.style.height = size + "px";
  
    const top = Math.floor(Math.random() * window.innerHeight);
    const left = Math.floor(Math.random() * window.innerWidth);
    shape.style.top = top + "px";
    shape.style.left = left + "px";
  
    // Random background color
    const color = "#" + Math.floor(Math.random()*16777215).toString(16);
    shape.style.backgroundColor = color;
  
    document.getElementById("content").appendChild(shape);
  }
  
  // Create a grid of shapes
  const numShapes = 50;
  for (let i = 0; i < numShapes; i++) {
    //createRandomShape();
  }
  