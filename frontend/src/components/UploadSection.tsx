import React, { useState, useRef } from 'react';
import { Upload, Link as LinkIcon, FileText, Video, BookOpen, Globe, ArrowRight, Loader2, Sparkles } from 'lucide-react';
import { uploadFile, submitUrl } from '../api';

interface UploadSectionProps {
  onIngestStarted: (jobId: string) => void;
  onError: (msg: string) => void;
}

export const UploadSection: React.FC<UploadSectionProps> = ({ onIngestStarted, onError }) => {
  const [activeTab, setActiveTab] = useState<'file' | 'url'>('file');
  const [urlInput, setUrlInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    try {
      setIsSubmitting(true);
      const res = await uploadFile(file);
      onIngestStarted(res.job_id);
    } catch (err: any) {
      onError(err.message || 'File upload failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUrlSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!urlInput.trim()) return;

    try {
      setIsSubmitting(true);
      const res = await submitUrl(urlInput.trim());
      onIngestStarted(res.job_id);
    } catch (err: any) {
      onError(err.message || 'URL ingestion failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const samplePresets = [
    {
      title: 'Attention Is All You Need (arXiv)',
      url: 'https://arxiv.org/abs/1706.03762',
      icon: BookOpen,
      badge: 'arXiv',
      badgeColor: 'text-amber-400 bg-amber-950/60 border-amber-800/60',
    },
    {
      title: 'Verifiable AI (Wikipedia)',
      url: 'https://en.wikipedia.org/wiki/Artificial_intelligence',
      icon: Globe,
      badge: 'Website',
      badgeColor: 'text-emerald-400 bg-emerald-950/60 border-emerald-800/60',
    },
    {
      title: 'Transformer Architecture Video',
      url: 'https://www.youtube.com/watch?v=wjZofJX0v4U',
      icon: Video,
      badge: 'YouTube',
      badgeColor: 'text-red-400 bg-red-950/60 border-red-800/60',
    }
  ];

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Header banner */}
      <div className="text-center space-y-3 pt-6 pb-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/60 border border-indigo-800/50 text-indigo-300 text-xs font-medium">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Universal Source Ingestion & Grounded AI Intelligence</span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Ingest Any Content. Discover Instant Truth.
        </h2>
        <p className="text-sm text-slate-400 max-w-xl mx-auto">
          Extract PDFs, text files, articles, research papers, and YouTube transcripts into a canonical intelligence representation with verifiable citations.
        </p>
      </div>

      {/* Main Ingestion Box */}
      <div className="glass-panel rounded-2xl overflow-hidden shadow-2xl border border-slate-800">
        {/* Tabs */}
        <div className="flex border-b border-slate-800 bg-slate-900/60 p-1.5">
          <button
            onClick={() => setActiveTab('file')}
            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold transition ${
              activeTab === 'file'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Upload className="w-4 h-4" />
            <span>Upload File (PDF / TXT / MD)</span>
          </button>
          <button
            onClick={() => setActiveTab('url')}
            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold transition ${
              activeTab === 'url'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <LinkIcon className="w-4 h-4" />
            <span>Enter URL (Web / YouTube / arXiv)</span>
          </button>
        </div>

        {/* Tab Content */}
        <div className="p-8">
          {activeTab === 'file' ? (
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center cursor-pointer transition text-center ${
                dragOver
                  ? 'border-indigo-500 bg-indigo-950/20'
                  : 'border-slate-700/80 hover:border-slate-600 bg-slate-900/40 hover:bg-slate-900/60'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.md"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileUpload(e.target.files[0]);
                  }
                }}
              />
              <div className="w-16 h-16 rounded-2xl bg-indigo-950/80 border border-indigo-800/60 flex items-center justify-center mb-4 text-indigo-400">
                {isSubmitting ? (
                  <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
                ) : (
                  <FileText className="w-8 h-8" />
                )}
              </div>
              <h3 className="text-base font-semibold text-slate-100">
                {isSubmitting ? 'Uploading document...' : 'Click or drag & drop document here'}
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Supports PDF (with OCR fallback for scanned docs), TXT, and Markdown files up to 50MB.
              </p>
            </div>
          ) : (
            <form onSubmit={handleUrlSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Target Source URL
                </label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <input
                      type="url"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      placeholder="e.g. https://arxiv.org/abs/... or https://youtube.com/watch?v=... or website URL"
                      className="w-full glass-input px-4 py-3 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={isSubmitting || !urlInput.trim()}
                    className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 disabled:opacity-50 text-white text-sm font-semibold flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition active:scale-95"
                  >
                    {isSubmitting ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <span>Ingest</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 pt-2">
                <span className="flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-emerald-400" /> Web (Trafilatura)
                </span>
                <span className="flex items-center gap-1.5">
                  <Video className="w-3.5 h-3.5 text-red-400" /> YouTube (Timestamp Transcripts)
                </span>
                <span className="flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-amber-400" /> Research Papers (arXiv/PDFs)
                </span>
              </div>
            </form>
          )}
        </div>

        {/* Quick Example Presets */}
        <div className="border-t border-slate-800 bg-slate-900/40 px-8 py-4">
          <p className="text-xs font-semibold text-slate-400 mb-2">Or try one of these sample sources:</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            {samplePresets.map((preset, idx) => {
              const Icon = preset.icon;
              return (
                <button
                  key={idx}
                  onClick={() => {
                    setActiveTab('url');
                    setUrlInput(preset.url);
                  }}
                  className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 text-left transition group"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <Icon className="w-4 h-4 text-slate-400 group-hover:text-indigo-400 shrink-0" />
                    <span className="text-xs text-slate-200 truncate group-hover:text-white font-medium">
                      {preset.title}
                    </span>
                  </div>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded border shrink-0 font-medium ${preset.badgeColor}`}>
                    {preset.badge}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
