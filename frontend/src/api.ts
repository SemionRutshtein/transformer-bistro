const BASE = "/api/v1";

export interface ApiError {
  error: {
    type: string;
    message: string;
    detail: unknown[];
    request_id: string;
  };
}

export interface EncodeResponse {
  input_text: string;
  token_ids: number[];
  tokens: string[];
  num_tokens: number;
  model: string;
}

export interface DecodeResponse {
  token_ids: number[];
  text: string;
  model: string;
}

export interface GenerateParams {
  max_new_tokens: number;
  temperature: number;
  top_k: number;
  top_p: number;
  do_sample: boolean;
  seed: number | null;
}

export interface GenerateResponse {
  prompt: string;
  generated_text: string;
  full_text: string;
  num_prompt_tokens: number;
  num_generated_tokens: number;
  params: GenerateParams;
  model: string;
  latency_ms: number;
}

export interface HistoryRecord {
  id: string;
  endpoint: string;
  request_body: Record<string, unknown>;
  response_summary: Record<string, unknown>;
  latency_ms: number;
  model: string;
  created_at: string;
}

async function post<T>(path: string, body: unknown): Promise<T | ApiError> {
  const resp = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return (await resp.json()) as T | ApiError;
}

async function get<T>(path: string): Promise<T | ApiError> {
  const resp = await fetch(`${BASE}${path}`);
  if (!resp.ok) return (await resp.json()) as ApiError;
  return (await resp.json()) as T;
}

export function isApiError(v: unknown): v is ApiError {
  return typeof v === "object" && v !== null && "error" in v;
}

export const api = {
  encode: (text: string, addSpecialTokens = false) =>
    post<EncodeResponse>("/encode", { text, add_special_tokens: addSpecialTokens }),

  decode: (tokenIds: number[], skipSpecialTokens = true) =>
    post<DecodeResponse>("/decode", { token_ids: tokenIds, skip_special_tokens: skipSpecialTokens }),

  generate: (params: {
    prompt: string;
    max_new_tokens?: number;
    temperature?: number;
    top_k?: number;
    top_p?: number;
    do_sample?: boolean;
    seed?: number | null;
  }) => post<GenerateResponse>("/generate", params),

  history: (limit = 20) => get<HistoryRecord[]>(`/history?limit=${limit}`),
};
