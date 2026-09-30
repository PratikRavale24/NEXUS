import type {
  EntityProfile,
  EntitySearchResult,
  FindingDetail,
  FindingSummary,
  HealthStatus,
  NetworkResponse,
  TimelineResponse,
  ApiError,
  CaseDetail,
  CaseDocument,
  CaseStatus,
  CaseSummary,
  CaseTimelineEntry,
  AuthResponse,
  UserRole,
} from "./types";


const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";


async function apiRequest<T>(
  path: string,
  options?: RequestInit & { timeoutMs?: number },
): Promise<T> {
  let response: Response;
  const controller = new AbortController();
  const timeout = options?.timeoutMs === 0 ? undefined : setTimeout(() => controller.abort(), options?.timeoutMs ?? 15000);

  try {
    response = await fetch(
      `${API_BASE_URL}${path}`,
      {
        ...options,
        signal: options?.signal ?? controller.signal,
        headers: {
          "Content-Type": "application/json",
          ...(options?.headers ?? {}),
        },
        credentials: "include",
        cache: "no-store",
      },
    );
  } catch (cause) {
    if (timeout) clearTimeout(timeout);
    if (cause instanceof DOMException && cause.name === "AbortError") {
      throw new Error("The request took too long. Retry the investigation.");
    }
    console.error("NEXUS API request failed", { path, cause });
    throw new Error(
      "The NEXUS API is unavailable. Check that the backend is running and retry.",
    );
  }

  if (timeout) clearTimeout(timeout);

  if (!response.ok) {
    let message = `API request failed: ${response.status}`;

    try {
      const errorData = await response.json();
      message = errorData?.message ?? errorData?.detail ?? message;
    } catch {
      // Keep the default message.
    }

    const error = new Error(message) as ApiError;
    error.status = response.status;
    error.requestId = response.headers.get("X-Request-ID") ?? undefined;
    throw error;
  }

  return response.json();
}

export function getCurrentUser(): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/auth/me");
}

export function loginMock(role: UserRole): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/auth/mock/login", { method: "POST", body: JSON.stringify({ role }) });
}

export function logoutMock(): Promise<{ status: string }> {
  return apiRequest<{ status: string }>("/auth/mock/logout", { method: "POST" });
}

export function getHealth(path = "/health"): Promise<HealthStatus> {
  return apiRequest<HealthStatus>(path);
}


export async function searchEntities(
  query: string,
  limit = 20,
): Promise<EntitySearchResult[]> {

  const params =
    new URLSearchParams({
      q: query,
      limit: String(limit),
    });

  return apiRequest<EntitySearchResult[]>(
    `/entities/search?${params.toString()}`,
  );
}


export async function getEntity(
  entityId: string,
): Promise<EntityProfile> {

  return apiRequest<EntityProfile>(
    `/entities/${encodeURIComponent(entityId)}`,
  );
}


export async function getEntityNetwork(
  entityId: string,
  depth = 1,
): Promise<NetworkResponse> {

  const params =
    new URLSearchParams({
      depth: String(depth),
    });

  return apiRequest<NetworkResponse>(
    `/entities/${encodeURIComponent(entityId)}/network?${params.toString()}`,
  );
}


export async function getEntityTimeline(
  entityId: string,
): Promise<TimelineResponse> {

  return apiRequest<TimelineResponse>(
    `/entities/${encodeURIComponent(entityId)}/timeline`,
  );
}


export async function getFindings(): Promise<
  FindingSummary[]
> {

  return apiRequest<FindingSummary[]>(
    "/findings",
  );
}


export async function getFinding(
  findingId: string,
): Promise<FindingDetail> {

  return apiRequest<FindingDetail>(
    `/findings/${encodeURIComponent(findingId)}`,
  );
}


export async function reviewFinding(
  findingId: string,
  status: string,
  reviewNotes?: string,
) {

  return apiRequest(
    `/findings/${encodeURIComponent(findingId)}/review`,
    {
      method: "POST",
      body: JSON.stringify({
        status,
        review_notes: reviewNotes ?? null,
      }),
    },
  );
}

export function getCases(status?: CaseStatus): Promise<CaseSummary[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return apiRequest<CaseSummary[]>(`/cases${query}`);
}

export function getCase(caseId: number): Promise<CaseDetail> {
  return apiRequest<CaseDetail>(`/cases/${caseId}`);
}

export function getCaseDocuments(caseId: number): Promise<CaseDocument[]> {
  return apiRequest<CaseDocument[]>(`/cases/${caseId}/documents`);
}

export function getCaseTimeline(caseId: number): Promise<CaseTimelineEntry[]> {
  return apiRequest<CaseTimelineEntry[]>(`/cases/${caseId}/timeline`);
}

export function startCaseProcessing(caseId: number, documentId: number) {
  return apiRequest(`/cases/${caseId}/processing?document_id=${documentId}`, { method: "POST" });
}

export function updateCaseStatus(caseId: number, status: CaseStatus): Promise<CaseSummary> {
  return apiRequest<CaseSummary>(`/cases/${caseId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}
