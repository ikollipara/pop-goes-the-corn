/**------------------------------------------------------------
 * app.js
 * Ian Kollipara
 *
 * App Entrypoint
 *------------------------------------------------------------**/

document.addEventListener("DOMContentLoaded", () => {
  const el = document.querySelector("[data-game-ws]");
  if (el === null) return;

  const data = JSON.parse(document.querySelector("#ws_data").textContent);
  console.log(data);

  const url = new URL(`ws://${document.location.host}${data.ws}/`);
  const ws = new WebSocket(url);

  ws.onopen = (ev) => {
    ws.send(JSON.stringify({ name: "Hello" }));
  };

  ws.onmessage = (ev) => {
    console.log(ev);
  };
});

document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("starfield");
  const ctx = canvas.getContext("2d");

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const stars = [];
  const numStars = 100;

  for (let i = 0; i < numStars; i++) {
    stars.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      radius: Math.random() * 1.5,
      alpha: Math.random(),
    });
  }

  function drawStars() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    stars.forEach((star) => {
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 255, ${star.alpha})`;
      ctx.fill();
    });
  }

  function animateStars() {
    stars.forEach((star) => {
      star.y += 0.5;
      if (star.y > canvas.height) {
        star.y = 0;
        star.x = Math.random() * canvas.width;
      }
    });
    drawStars();
    requestAnimationFrame(animateStars);
  }

  animateStars();

  window.addEventListener("resize", () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    drawStars();
  });
});
