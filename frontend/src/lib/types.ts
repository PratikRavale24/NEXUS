export type EntitySearchResult = {
  entity_id: string;
  entity_type: string;
  name: string;
  secondary_identifier?: string | null;
};

export type EntityProfile = {
  entity_id: string;
  entity_type: string;
  name: string;
  properties: Record<string, unknown>;
  connection_count: number;
  finding_count: number;
};

export type NetworkNode = {
  id: string;
  entity_type: string;
  label: string;
  properties: Record<string, unknown>;
};

export type NetworkEdge = {
  id: string;
  source: string;
  target: string;
  relationship: string;
  properties: Record<string, unknown>;
};

export type NetworkResponse = {
  root_entity_id: string;
  depth: number;
  nodes: NetworkNode[];
  edges: NetworkEdge[];
};

export type ApiError = Error & {
  status?: number;
  requestId?: string;
};

export type UserRole = "INVESTIGATOR" | "ANALYST" | "SUPERVISOR" | "ADMIN";

export type AuthUser = {
  user_id: number | null;
  role: UserRole;
  display_name: string;
};

export type AuthResponse = { user: AuthUser };

export type TimelineItem = {
  timestamp: string | null;
  event_type: string;
  description: string;

  entity_id?: string | null;
  entity_name?: string | null;

  related_entity_id?: string | null;
  related_entity_name?: string | null;

  case_id?: string | null;
  evidence_id?: string | null;
  source_type?: string | null;
};

export type TimelineResponse = {
  entity_id: string;
  items: TimelineItem[];
};

export type FindingSummary = {
  finding_id: string;
  finding_type: string;
  status: string;
  description: string;
  model?: string | null;
  model_score?: number | null;

  subjects: {
    entity_id: string;
    name?: string | null;
  }[];

  location_name?: string | null;
  participant_count?: number | null;

  window_start?: string | null;
  window_end?: string | null;
};

export type FindingDetail = FindingSummary & {
  reasons: string[];
  evidence: {
    evidence_id: string;
    source_type?: string | null;
    timestamp?: string | null;
    case_id?: string | null;
  }[];

  method?: string | null;
  case_ids: string[];
  review_notes?: string | null;
};

export type HealthStatus = {
  status: "ok";
  service?: string;
  database?: string;
  version?: string;
};

export type CaseStatus = "OPEN" | "UNDER_REVIEW" | "CLOSED";
export type ProcessingStatus = "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";

export type CaseSummary = {
  id: number;
  case_number: string;
  title: string;
  status: CaseStatus;
  created_at: string;
};

export type CaseDocument = {
  id: number;
  filename: string;
  document_type: string;
  sha256_hash: string;
  ingested_at: string;
  processing_status: ProcessingStatus;
  provenance: string;
};

export type CaseTimelineEntry = {
  action: string;
  resource_type: string;
  resource_id?: string | null;
  timestamp: string;
  result?: string | null;
};

export type CaseDetail = CaseSummary & {
  description?: string | null;
  documents: CaseDocument[];
  timeline: CaseTimelineEntry[];
};
