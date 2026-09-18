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
  return request("/chat", {
    method: "POST",
    body: JSON.stringify({ repository_id: repositoryId, question, messages }),
  });
}
