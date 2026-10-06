import React, { useState, useEffect } from 'react';
import {
  Navbar,
} from './components/Navbar';
import { UploadSection } from './components/UploadSection';
import { ProcessingProgress } from './components/ProcessingProgress';
import { ActionSelector, ActionMode, SummaryFormat, UserGoal } from './components/ActionSelector';
import { ResultsView } from './components/ResultsView';
import { SourcePreview } from './components/SourcePreview';
import { QAChat } from './components/QAChat';
import { DocumentLibrary } from './components/DocumentLibrary';
import { Footer } from './components/Footer';
import {
  checkHealth,
  getDocuments,
  getDocument,
  getDocumentChunks,
  deleteDocument,
  generateSummary,
  generateKeyPoints,
  generateInsights,
  DocumentItem,
  DocumentDetail,
  ChunkItem,
  AnalysisItem,
  CitationItem,
} from './api';
import { AlertCircle, ArrowLeft, Eye, MessageSquare, Sparkles } from 'lucide-react';

export function App() {
  const [llmInfo, setLlmInfo] = useState<any>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [activeDocId, setActiveDocId] = useState<string | null>(null);
  const [activeDoc, setActiveDoc] = useState<DocumentDetail | null>(null);
  const [chunks, setChunks] = useState<ChunkItem[]>([]);
  
  // Ingestion state
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  
  // Workspace UI states
  const [actionMode, setActionMode] = useState<ActionMode>('summary');
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisItem | null>(null);
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);
  const [highlightedChunkId, setHighlightedChunkId] = useState<string | undefined>(undefined);
  const [showLibrary, setShowLibrary] = useState(false);
  const [showSourceModal, setShowSourceModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Initial load
  useEffect(() => {
    const init = async () => {
      try {
        const health = await checkHealth();
        setLlmInfo(health.llm);
      } catch (e) {
        console.error('Health check failed', e);
      }
      loadDocumentList();
    };
    init();
  }, []);

  const loadDocumentList = async () => {
    try {
      const list = await getDocuments();
      setDocuments(list);
    } catch (e) {
      console.error('Failed to load documents', e);
    }
  };

  const loadDocumentDetails = async (docId: string) => {
    try {
      setIsLoadingAnalysis(true);
      const [doc, docChunks] = await Promise.all([
        getDocument(docId),
        getDocumentChunks(docId),
      ]);
      setActiveDoc(doc);
      setChunks(docChunks);
      setActiveDocId(docId);

      // Auto-load executive summary initially
      const summary = await generateSummary(docId, 'executive', false);
      setCurrentAnalysis(summary);
      setActionMode('summary');
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load document');
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  const handleIngestStarted = (jobId: string) => {
    setActiveJobId(jobId);
    setErrorMessage(null);
  };

  const handleIngestCompleted = async (documentId: string) => {
    setActiveJobId(null);
    await loadDocumentList();
    await loadDocumentDetails(documentId);
  };

  const handleTriggerSummary = async (fmt: SummaryFormat) => {
    if (!activeDocId) return;
    try {
      setIsLoadingAnalysis(true);
      const res = await generateSummary(activeDocId, fmt, false);
      setCurrentAnalysis(res);
      setActionMode('summary');
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to generate summary');
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  const handleTriggerKeyPoints = async () => {
    if (!activeDocId) return;
    try {
      setIsLoadingAnalysis(true);
      const res = await generateKeyPoints(activeDocId, false);
      setCurrentAnalysis(res);
      setActionMode('key_points');
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to extract key points');
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  const handleTriggerInsights = async (goal: UserGoal, customFocus?: string) => {
    if (!activeDocId) return;
    try {
      setIsLoadingAnalysis(true);
      const res = await generateInsights(activeDocId, goal, customFocus, false);
      setCurrentAnalysis(res);
      setActionMode('actionable_insights');
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to generate actionable insights');
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  const handleCitationClick = (citation: CitationItem) => {
    setHighlightedChunkId(citation.chunk_id);
    setShowSourceModal(true);
    // Smooth scroll if element is present in DOM
    setTimeout(() => {
      const el = document.getElementById(`chunk-${citation.chunk_id}`);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 200);
  };

  const handleDelete = async (docId: string) => {
    try {
      await deleteDocument(docId);
      if (activeDocId === docId) {
        setActiveDocId(null);
        setActiveDoc(null);
        setCurrentAnalysis(null);
      }
      loadDocumentList();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to delete');
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-indigo-500 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        llmInfo={llmInfo}
        docCount={documents.length}
        onOpenLibrary={() => setShowLibrary(true)}
        onNewDoc={() => {
          setActiveDocId(null);
          setActiveDoc(null);
          setShowLibrary(false);
          setActiveJobId(null);
        }}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8 space-y-8">
        {/* Error notification banner */}
        {errorMessage && (
          <div className="glass-panel p-4 rounded-xl border border-red-500/40 bg-red-950/40 text-red-200 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-slate-400 hover:text-white px-2 py-0.5 rounded bg-slate-900 border border-slate-800"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* View 1: Document Library Modal / View */}
        {showLibrary ? (
          <DocumentLibrary
            documents={documents}
            selectedDocId={activeDocId || undefined}
            onSelectDoc={(id) => loadDocumentDetails(id)}
            onDeleteDoc={handleDelete}
            onClose={() => setShowLibrary(false)}
          />
        ) : activeJobId ? (
          /* View 2: Active Background Processing Stepper */
          <ProcessingProgress
            jobId={activeJobId}
            onComplete={handleIngestCompleted}
            onError={(msg) => {
              setActiveJobId(null);
              setErrorMessage(msg);
            }}
          />
        ) : !activeDocId || !activeDoc ? (
          /* View 3: Ingestion Home Page */
          <UploadSection
            onIngestStarted={handleIngestStarted}
            onError={(msg) => setErrorMessage(msg)}
          />
        ) : (
          /* View 4: Active Document Workspace */
          <div className="space-y-6">
            {/* Top Workspace Header Bar */}
            <div className="flex flex-wrap items-center justify-between gap-4 glass-panel p-4 rounded-2xl border border-slate-800">
              <div className="flex items-center gap-3">
                <button
                  onClick={() => {
                    setActiveDocId(null);
                    setActiveDoc(null);
                  }}
                  className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-white transition"
                  title="Back to Ingest"
                >
                  <ArrowLeft className="w-4 h-4" />
                </button>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-950 border border-indigo-800 text-indigo-300">
                      {activeDoc.source_type.replace('_', ' ')}
                    </span>
                    <h2 className="text-base font-bold text-white truncate max-w-md">
                      {activeDoc.title}
                    </h2>
                  </div>
                  <p className="text-xs text-slate-400">
                    {chunks.length} structure-aware chunks &bull; Preserved page numbers & timestamps
                  </p>
                </div>
              </div>

              {/* Source Viewer Toggle */}
              <button
                onClick={() => setShowSourceModal(!showSourceModal)}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl border text-xs font-semibold transition ${
                  showSourceModal
                    ? 'bg-indigo-600 text-white border-indigo-500'
                    : 'bg-slate-900 hover:bg-slate-850 border-slate-800 text-slate-300'
                }`}
              >
                <Eye className="w-3.5 h-3.5" />
                <span>{showSourceModal ? 'Hide Source Chunks' : 'Inspect Source Chunks'}</span>
              </button>
            </div>

            {/* Source Preview Inspector (Toggleable) */}
            {showSourceModal && (
              <SourcePreview
                document={activeDoc}
                chunks={chunks}
                highlightedChunkId={highlightedChunkId}
              />
            )}

            {/* Interactive Action Flow: "What would you like to do with this content?" */}
            <ActionSelector
              currentMode={actionMode}
              onSelectMode={(mode) => setActionMode(mode)}
              onTriggerSummary={handleTriggerSummary}
              onTriggerKeyPoints={handleTriggerKeyPoints}
              onTriggerInsights={handleTriggerInsights}
              isLoading={isLoadingAnalysis}
            />

            {/* Action Results or Q&A Interface */}
            {actionMode === 'qa' ? (
              <QAChat
                documentId={activeDoc.id}
                onCitationClick={handleCitationClick}
              />
            ) : currentAnalysis ? (
              <ResultsView
                analysis={currentAnalysis}
                onRefresh={() => {
                  if (currentAnalysis.action_type === 'summary') {
                    handleTriggerSummary((currentAnalysis.summary_format as SummaryFormat) || 'executive');
                  } else if (currentAnalysis.action_type === 'key_points') {
                    handleTriggerKeyPoints();
                  } else if (currentAnalysis.action_type === 'actionable_insights') {
                    handleTriggerInsights((currentAnalysis.user_goal as UserGoal) || 'understand_topic');
                  }
                }}
                onCitationClick={handleCitationClick}
                isLoading={isLoadingAnalysis}
              />
            ) : (
              <div className="glass-panel p-12 rounded-2xl border border-slate-800 text-center text-slate-400 text-sm">
                Select an action above to analyze this source.
              </div>
            )}
          </div>
        )}
      </main>

      {/* Mandatory User Rule: Footer "Built by Dikshant Sharma" */}
      <Footer />
    </div>
  );
}
export default App;
