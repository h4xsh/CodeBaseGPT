const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail || "The request failed.");
  }
  return body;
}

export function createRepository(githubUrl) {
  return request("/repositories", {
    method: "POST",
    body: JSON.stringify({ github_url: githubUrl }),
  });
}

export function getRepository(repositoryId) {
  return request(`/repositories/${repositoryId}`);
}

export function deleteRepository(repositoryId) {
  return request(`/repositories/${repositoryId}`, { method: "DELETE" });
}

export function askQuestion(repositoryId, question, messages) {
  return streamQuestion(repositoryId, question, messages);
}

export async function streamQuestion(repositoryId, question, messages, onToken) {
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ repository_id: repositoryId, question, messages }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "The request failed.");
  }
  if (!response.body) throw new Error("The browser does not support response streaming.");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let result = { answer: "", sources: [], model: "" };

  function processEvent(event) {
    if (!event.trim()) return;
    const data = JSON.parse(event.replace(/^data:\s*/, ""));
    if (data.type === "token") {
      result.answer += data.content;
      result.model = data.model || result.model;
      onToken(data.content);
    } else if (data.type === "done") {
      result.sources = data.sources || [];
      result.model = data.model || result.model;
    } else if (data.type === "error") {
      throw new Error(data.detail || "The model could not answer.");
    }
  }

  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";
    events.forEach(processEvent);
    if (done) break;
  }
  if (buffer.trim()) processEvent(buffer);
  return result;
}
