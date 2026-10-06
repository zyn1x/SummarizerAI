export interface DocumentItem {
  id: string;
  title: string;
  source_type: 'pdf' | 'txt' | 'website' | 'youtube' | 'research_paper';
  source_url?: string;
  original_filename?: string;
  file_size_bytes?: number;
  summary_short?: string;
  metadata_json?: Record<string, any>;
  created_at: string;
  updated_at: string;
  chunk_count?: number;
}

export interface DocumentDetail extends DocumentItem {
  raw_text_preview?: string;
  has_analyses: boolean;
  analyses_count: number;
}

export interface ChunkItem {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  page_number?: number;
  section_heading?: string;
  timestamp_start?: number;
  timestamp_end?: number;
  timestamp_formatted?: string;
  token_count?: number;
  metadata_json?: Record<string, any>;
}

export interface CitationItem {
  id?: string;
  chunk_id: string;
  citation_label: string;
  citation_type: 'page' | 'section' | 'timestamp' | 'chunk';
  page_number?: number;
  section_heading?: string;
  timestamp_formatted?: string;
  timestamp_seconds?: number;
  quote_text: string;
}

export interface AnalysisItem {
  id: string;
  document_id: string;
  action_type: 'summary' | 'key_points' | 'actionable_insights';
  summary_format?: string;
  user_goal?: string;
  result_markdown: string;
  key_takeaways?: string[];
  citations?: CitationItem[];
  created_at: string;
  is_cached?: boolean;
}

export interface JobStatus {
  id: string;
  document_id: string;
  status: 'uploading' | 'extracting' | 'normalizing' | 'chunking' | 'analyzing' | 'ready' | 'failed';
  progress_percent: number;
  current_step?: string;
  error_message?: string;
}

export interface QAResult {
  id: string;
  document_id: string;
  question: string;
  answer: string;
  is_grounded: boolean;
  citations: CitationItem[];
  created_at: string;
}

const API_BASE = '/api';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function uploadFile(file: File): Promise<{ document_id: string; job_id: string }> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/ingest/file`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to upload file' }));
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}

export async function submitUrl(url: string): Promise<{ document_id: string; job_id: string }> {
  const res = await fetch(`${API_BASE}/ingest/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to submit URL' }));
    throw new Error(err.detail || 'URL ingestion failed');
  }
  return res.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) throw new Error('Job not found');
  return res.json();
}

export async function getDocuments(): Promise<DocumentItem[]> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}

export async function getDocument(docId: string): Promise<DocumentDetail> {
  const res = await fetch(`${API_BASE}/documents/${docId}`);
  if (!res.ok) throw new Error('Failed to fetch document details');
  return res.json();
}

export async function getDocumentChunks(docId: string): Promise<ChunkItem[]> {
  const res = await fetch(`${API_BASE}/documents/${docId}/chunks`);
  if (!res.ok) throw new Error('Failed to fetch document chunks');
  return res.json();
}

export async function deleteDocument(docId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${docId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete document');
}

export async function generateSummary(
  docId: string,
  summaryFormat: 'executive' | 'detailed' | 'bulleted' = 'executive',
  forceRefresh: boolean = false
): Promise<AnalysisItem> {
  const res = await fetch(`${API_BASE}/documents/${docId}/actions/summary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action_type: 'summary',
      summary_format: summaryFormat,
      force_refresh: forceRefresh,
    }),
  });
  if (!res.ok) throw new Error('Failed to generate summary');
  return res.json();
}

export async function generateKeyPoints(docId: string, forceRefresh: boolean = false): Promise<AnalysisItem> {
  const res = await fetch(`${API_BASE}/documents/${docId}/actions/key_points?force_refresh=${forceRefresh}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to generate key points');
  return res.json();
}

export async function generateInsights(
  docId: string,
  userGoal: string,
  customContext?: string,
  forceRefresh: boolean = false
): Promise<AnalysisItem> {
  const res = await fetch(`${API_BASE}/documents/${docId}/actions/insights`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_goal: userGoal,
      custom_context: customContext,
      force_refresh: forceRefresh,
    }),
  });
  if (!res.ok) throw new Error('Failed to generate actionable insights');
  return res.json();
}

export async function getDocumentAnalyses(docId: string): Promise<AnalysisItem[]> {
  const res = await fetch(`${API_BASE}/documents/${docId}/actions/history`);
  if (!res.ok) return [];
  return res.json();
}

export async function askQuestion(docId: string, question: string, topK: number = 5): Promise<QAResult> {
  const res = await fetch(`${API_BASE}/documents/${docId}/qa`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK }),
  });
  if (!res.ok) throw new Error('Failed to ask question');
  return res.json();
}

export async function getQAHistory(docId: string): Promise<QAResult[]> {
  const res = await fetch(`${API_BASE}/documents/${docId}/qa/history`);
  if (!res.ok) return [];
  return res.json();
}
