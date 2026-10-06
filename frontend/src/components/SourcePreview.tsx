import React, { useState } from 'react';
import {
  FileText,
  Video,
  Globe,
  BookOpen,
  Layers,
  Search,
  ExternalLink,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { DocumentDetail, ChunkItem, CitationItem } from '../api';

interface SourcePreviewProps {
  document: DocumentDetail;
  chunks: ChunkItem[];
  highlightedChunkId?: string;
  onSelectChunk?: (chunk: ChunkItem) => void;
}

export const SourcePreview: React.FC<SourcePreviewProps> = ({
  document,
  chunks,
  highlightedChunkId,
  onSelectChunk,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState<'chunks' | 'raw'>('chunks');
  const [expandedChunkId, setExpandedChunkId] = useState<string | null>(highlightedChunkId || null);

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'youtube':
        return <Video className="w-4 h-4 text-red-400" />;
      case 'pdf':
        return <FileText className="w-4 h-4 text-indigo-400" />;
      case 'research_paper':
        return <BookOpen className="w-4 h-4 text-amber-400" />;
      default:
        return <Globe className="w-4 h-4 text-emerald-400" />;
    }
  };

  const filteredChunks = chunks.filter(
    (c) =>
      c.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (c.section_heading && c.section_heading.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="w-full glass-panel rounded-2xl border border-slate-800 p-6 space-y-5">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
              {getSourceIcon(document.source_type)}
            </span>
            <span className="text-xs uppercase tracking-wider font-bold text-slate-400">
              {document.source_type.replace('_', ' ')}
            </span>
            {document.source_url && (
              <a
                href={document.source_url}
                target="_blank"
                rel="noreferrer"
                className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium transition"
              >
                <span>Visit Link</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
          <h3 className="text-lg font-bold text-white tracking-tight">{document.title}</h3>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex rounded-lg bg-slate-900 p-1 border border-slate-800 text-xs font-semibold">
            <button
              onClick={() => setActiveTab('chunks')}
              className={`px-3 py-1 rounded-md transition ${
                activeTab === 'chunks' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Chunks ({chunks.length})
            </button>
            <button
              onClick={() => setActiveTab('raw')}
              className={`px-3 py-1 rounded-md transition ${
                activeTab === 'raw' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Raw Preview
            </button>
          </div>
        </div>
      </div>

      {/* YouTube Embed if source is YouTube */}
      {document.source_type === 'youtube' && document.metadata_json?.video_id && (
        <div className="rounded-xl overflow-hidden border border-slate-800 aspect-video max-h-[360px] mx-auto w-full">
          <iframe
            src={`https://www.youtube.com/embed/${document.metadata_json.video_id}`}
            title={document.title}
            className="w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      )}

      {/* Tab 1: Structure-Aware Chunks */}
      {activeTab === 'chunks' ? (
        <div className="space-y-3">
          {/* Search bar */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter chunks by keyword or section title..."
              className="w-full glass-input pl-10 pr-4 py-2.5 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none"
            />
          </div>

          <div className="max-h-[480px] overflow-y-auto space-y-2.5 pr-1">
            {filteredChunks.map((c) => {
              const isHighlighted = highlightedChunkId === c.id;
              const isExpanded = expandedChunkId === c.id || isHighlighted;

              return (
                <div
                  key={c.id}
                  id={`chunk-${c.id}`}
                  className={`p-3.5 rounded-xl border transition ${
                    isHighlighted
                      ? 'bg-indigo-950/70 border-indigo-500 ring-2 ring-indigo-500/40'
                      : 'bg-slate-900/40 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div
                    className="flex items-center justify-between cursor-pointer select-none"
                    onClick={() => setExpandedChunkId(isExpanded ? null : c.id)}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                        {c.page_number
                          ? `Page ${c.page_number}`
                          : c.timestamp_formatted
                          ? c.timestamp_formatted
                          : c.section_heading || `Chunk ${c.chunk_index + 1}`}
                      </span>
                      {c.section_heading && !c.page_number && (
                        <span className="text-xs font-semibold text-slate-300 truncate max-w-[280px]">
                          {c.section_heading}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-slate-500">~{c.token_count || 150} tokens</span>
                      {isExpanded ? (
                        <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                      )}
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="mt-3 pt-3 border-t border-slate-800 text-xs text-slate-300 leading-relaxed font-sans">
                      {c.content}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        /* Tab 2: Raw Document Preview */
        <div className="max-h-[500px] overflow-y-auto p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-mono text-slate-300 leading-relaxed whitespace-pre-wrap">
          {document.raw_text_preview || 'No raw preview available.'}
        </div>
      )}
    </div>
  );
};
