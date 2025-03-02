/**------------------------------------------------------------
 * app.js
 * Ian Kollipara
 *
 * App Entrypoint
 *------------------------------------------------------------**/

class GameState {
  #data;
  #websocket;
  #gameData;
  #currentPlayer;
  #player;

  constructor(data, player) {
    this.#data = data;
    this.#player = player;
    const url = new URL(`ws://${document.location.host}${this.#data.ws}/`);
    this.#websocket = new WebSocket(url);
    this.#setupHandler();
    this.#joinOnOpen();
    this.#hideStartBtnIfNotCreator();
  }

  join() {
    this.#websocket.send(JSON.stringify({ type: "join", email: this.#player }));
  }

  start() {
    this.#websocket.send(JSON.stringify({ type: "start" }));
  }

  click() {
    if (this.#gameData.active_player !== this.#player) return;
    this.#websocket.send(JSON.stringify({ type: "click" }));
  }

  startSync() {
    this.intervalFunc = setInterval(() => {
      this.#websocket.send(
        JSON.stringify({
          type: "sync",
          game: this.#gameData,
          currentPlayer: this.#gameData.active_player,
        })
      );
    }, 1000);
  }

  stopSync() {
    clearInterval(this.intervalFunc);
  }

  endTurn() {
    this.#websocket.send(
      JSON.stringify({
        type: "end_turn",
        game: this.#gameData,
        currentPlayer: this.#gameData.active_player,
      })
    );
  }

  playCard(card) {
    this.#websocket.send(
      JSON.stringify({
        type: "play_card",
        currentPlayer: this.#gameData.active_player,
        card,
      })
    );
  }

  #setupHandler() {
    this.#websocket.addEventListener("message", (ev) => {
      const data = JSON.parse(ev.data);
      switch (data.type) {
        case "join":
          alert(data.msg);
          document
            .querySelector("[data-game-players]")
            .insertAdjacentHTML("beforeend", data.alive_html);
          break;

        case "start":
          this.#gameData = data.game;
          alert(data.msg);
          if (this.#gameData.active_player !== this.#player) this.startSync();
          if (this.#gameData.active_player !== this.#player) {
            document.getElementById("end-turn").hidden = true;
          }
          break;

        case "click":
          popcornExplosion({ clientX: 0, clientY: 0 });
          break;

        case "sync":
          this.#gameData = data.game;
          break;

        case "end_turn":
          this.#gameData = data.game;
          alert(data.msg);
          if (this.#gameData.active_player !== this.#player) {
            this.startSync();
          } else {
            this.stopSync();
          }
          break;

        case "kill":
          const active_player = this.#gameData.active_player;
          this.#gameData = data.game;
          alert(data.msg);
          if (this.#player === active_player) this.#websocket.close();
          history.back();
          break;

        case "play_card":
          this.#gameData = data.game;
          alert(data.msg);
          document
            .querySelector("[data-game-hand-contents]")
            .append(data.hand_html);
          break;

        case "win":
          alert(data.msg);
          this.#websocket.close();
          history.back();
          break;

        default:
          break;
      }
    });
  }

  #joinOnOpen() {
    this.#websocket.addEventListener("open", () => {
      if (this.#player !== this.#data.creator) {
        this.join();
      }
    });
  }

  #hideStartBtnIfNotCreator() {
    if (this.#player !== this.#data.creator) {
      document.querySelector("[data-game-start-btn]").remove();
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const el = document.querySelector("[data-game-ws]");
  if (el === null) return;

  const data = JSON.parse(document.querySelector("#ws_data").textContent);
  const player = data.player;
  const gameState = new GameState(data, player);

  window.handleCard = (card) => {
    gameState.playCard(card);
  };

  window.startGame = () => gameState.start();
  window.endTurn = () => gameState.endTurn();
  window.cornClick = () => gameState.click();
});

function popcornExplosion(event) {
  // Call createPopcorn to create popcorn at click location
  createPopcorn(event.clientX, event.clientY);
}

function createPopcorn(x, y) {
  const popcorn = document.createElement("img");
  const popcornNumber = Math.floor(Math.random() * 10); // Random popcorn image (0-9)
  popcorn.src = `/static/popcorn_kernel_${popcornNumber}.png`;

  popcorn.classList.add("popcorn");

  const main = document.querySelector("main");
  main.appendChild(popcorn);

  // Get screen position of the click event
  const xPos = x; // x position is directly from the click
  const yPos = y; // y position is directly from the click

  popcorn.style.left = `${xPos}px`; // Set left position based on the click
  popcorn.style.top = `${yPos}px`; // Set top position based on the click

  // Randomly choose to move left or right (xOffset)
  const xOffset = (Math.random() - 0.5) * 100; // Random small left or right offset

  // Apply the random xOffset to the custom property
  popcorn.style.setProperty("--x", `${xOffset}px`);

  // Remove the popcorn after the animation completes
  setTimeout(() => popcorn.remove(), 1500);
}
// document.addEventListener("DOMContentLoaded", () => {
//   const el = document.querySelector("[data-game-ws]");
//   if (el === null) return;

//   const data = JSON.parse(document.querySelector("#ws_data").textContent);

//   const url = new URL(`ws://${document.location.host}${data.ws}/`);
//   const ws = new WebSocket(url);
//   const players = [];
//   let currentPlayer = null;
//   let game;
//   document.querySelectorAll("[data-game-player-id]").forEach((el) => {
//     players.push(el.dataset.gamePlayerId);
//     if (el.dataset.gamePlayer) currentPlayer = el.dataset.gamePlayerId;
//   });

//   const startBtn = document.querySelector("[data-game-start-btn]");
//   if (currentPlayer != data.creator) startBtn.disabled = true;
//   startBtn.onclick = () => {
//     ws.send(JSON.stringify({ name: "start_game" }));
//     setInterval(() => {
//       ws.send(JSON.stringify({ type: "status" }));
//     }, 1000);
//     startBtn.remove();
//   };

//   ws.onopen = (ev) => {
//     console.log(currentPlayer, data.creator);
//     if (currentPlayer !== data.creator)
//       ws.send(JSON.stringify({ type: "join", email: currentPlayer }));
//   };

//   ws.onmessage = (ev) => {
//     const data = JSON.parse(ev.data);
//     if (data.type == "start") {
//       game = data.game;
//       console.log(game);
//     } else if (data.type == "status") {
//       game = data.game;
//       console.log(game);
//     } else if
//   };
// });

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
