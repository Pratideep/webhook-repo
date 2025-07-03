async function fetchUpdates() {
    const response = await fetch("/get-updates");
    const data = await response.json();
  
    const list = document.getElementById("events-list");
    list.innerHTML = "";
  
    data.forEach(event => {
      let text = "";
      if (event.action === "push") {
        text = `${event.author} pushed to ${event.to_branch} on ${event.timestamp}`;
      } else if (event.action === "pull_request") {
        text = `${event.author} submitted a pull request from ${event.from_branch} to ${event.to_branch} on ${event.timestamp}`;
      } else if (event.action === "merge") {
        text = `${event.author} merged branch ${event.from_branch} to ${event.to_branch} on ${event.timestamp}`;
      }
      const li = document.createElement("li");
      li.innerText = text;
      list.appendChild(li);
    });
  }
  
  // Initial fetch
  fetchUpdates();
  // Poll every 15s
  setInterval(fetchUpdates, 15000);
  