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
