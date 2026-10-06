import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Copy,
  Check,
  Download,
  RotateCw,
  BookmarkCheck,
  ExternalLink,
  Sparkles,
  Quote,
  Clock,
  FileText,
  Layers,
} from 'lucide-react';
import { AnalysisItem, CitationItem } from '../api';

interface ResultsViewProps {
  analysis: AnalysisItem;
  onRefresh: () => void;
  onCitationClick: (citation: CitationItem) => void;
  isLoading: boolean;
}

export const ResultsView: React.FC<ResultsViewProps> = ({
  analysis,
  onRefresh,
  onCitationClick,
  isLoading,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(analysis.result_markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([analysis.result_markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `summarizerai_${analysis.action_type}_${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatActionTitle = () => {
    if (analysis.action_type === 'summary') {
      return `${analysis.summary_format || 'Executive'} Summary`;
    } else if (analysis.action_type === 'key_points') {
      return 'Key Takeaways & Core Arguments';
    } else if (analysis.action_type === 'actionable_insights') {
      const gMap: Record<string, string> = {
        study_exam: 'Exam Preparation Blueprint',
        understand_topic: 'First-Principles Mental Model',
        implement_method: 'Engineering Execution Guide',
        apply_project: 'Project Integration Strategy',
        find_research_gaps: 'Research Gaps & Hypotheses',
        prepare_presentation: 'Executive Presentation Outline',
      };
      return gMap[analysis.user_goal || ''] || 'Actionable Insights';
    }
    return 'Analysis Deliverable';
  };

  return (
    <div className="w-full space-y-6">
      {/* Top Header Card */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white capitalize">{formatActionTitle()}</h3>
              {analysis.is_cached && (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950/70 border border-emerald-800/60 text-emerald-400 font-semibold flex items-center gap-1">
                  <BookmarkCheck className="w-3 h-3" /> Cached
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400">Generated with source grounding & verified evidence</p>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold transition"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied!' : 'Copy'}</span>
          </button>

          <button
            onClick={handleDownload}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download</span>
          </button>

          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 text-xs font-semibold transition"
            title="Re-run analysis fresh"
          >
            <RotateCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Regenerate</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Markdown Output + Evidence Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Markdown Content (8 Cols) */}
        <div className="lg:col-span-8 glass-panel p-8 rounded-2xl border border-slate-800 text-slate-200">
          <article className="prose prose-invert prose-indigo max-w-none prose-headings:text-white prose-p:text-slate-300 prose-p:leading-relaxed prose-li:text-slate-300 prose-strong:text-white prose-code:text-indigo-300 prose-code:bg-slate-900 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {analysis.result_markdown}
            </ReactMarkdown>
          </article>
        </div>

        {/* Evidence & Grounding Panel (4 Cols) */}
        <div className="lg:col-span-4 space-y-4">
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Quote className="w-4 h-4 text-emerald-400" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  Verified Source Evidence ({analysis.citations?.length || 0})
                </h4>
              </div>
            </div>

            <p className="text-xs text-slate-400 leading-normal">
              Backend-controlled deterministic citations mapped directly to source locations. Click any citation to inspect the verified text chunk.
            </p>

            <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
              {analysis.citations && analysis.citations.length > 0 ? (
                analysis.citations.map((c, i) => (
                  <div
                    key={i}
                    onClick={() => onCitationClick(c)}
                    className="p-3 rounded-xl bg-slate-900/60 hover:bg-slate-850/80 border border-slate-800 hover:border-indigo-500/50 cursor-pointer transition group"
                  >
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded bg-indigo-950/80 border border-indigo-800/60 text-indigo-300 group-hover:border-indigo-500">
                        {c.citation_type === 'page' && <FileText className="w-3 h-3 text-indigo-400" />}
                        {c.citation_type === 'timestamp' && <Clock className="w-3 h-3 text-red-400" />}
                        {c.citation_type === 'section' && <Layers className="w-3 h-3 text-emerald-400" />}
                        {c.citation_label}
                      </span>
                      <ExternalLink className="w-3 h-3 text-slate-500 group-hover:text-indigo-400 transition" />
                    </div>
                    <p className="text-[11px] text-slate-400 italic line-clamp-3 leading-snug">
                      "{c.quote_text}"
                    </p>
                  </div>
                ))
              ) : (
                <div className="text-center py-6 text-xs text-slate-500">
                  No citations attached for this document segment.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
