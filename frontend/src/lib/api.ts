import type { Application, ChatResponse, ResumeProfile } from "./types";

const baseUrl = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 20_000);
  try {
    const response = await fetch(`${baseUrl}${path}`, {
      ...options,
      signal: controller.signal,
      headers:
        options?.body instanceof FormData
          ? options.headers
          : {
              "Content-Type": "application/json",
              ...options?.headers,
            },
    });
    const payload: unknown = await response.json().catch(() => null);
    if (!response.ok) {
      const detail =
        typeof payload === "object" && payload !== null && "detail" in payload
          ? String(payload.detail)
          : `Request failed (${response.status})`;
      throw new ApiError(detail, response.status);
    }
    return payload as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(
        "The request timed out. Check that the backend is running.",
        408,
      );
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export function sendChat(
  message: string,
  conversationId: string | null,
  resumeProfile: ResumeProfile | null,
  visibleJobIds: string[],
  visibleJobOffset = 0,
) {
  return request<ChatResponse>("/api/v1/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      resume_profile: resumeProfile,
      visible_job_ids: visibleJobIds,
      visible_job_offset: visibleJobOffset,
    }),
  });
}

export async function parseResume(file: File): Promise<ResumeProfile> {
  const form = new FormData();
  form.append("file", file);
  const response = await request<{ profile: ResumeProfile }>(
    "/api/v1/resume/parse",
    {
      method: "POST",
      body: form,
    },
  );
  return response.profile;
}

export function createApplication(jobId: string) {
  return request<Application>("/api/v1/applications", {
    method: "POST",
    body: JSON.stringify({ job_id: jobId }),
  });
}

export function listApplications() {
  return request<Application[]>("/api/v1/applications");
}
