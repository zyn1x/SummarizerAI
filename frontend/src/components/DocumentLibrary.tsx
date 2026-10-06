import React from 'react';
import {
  FileText,
  Video,
  Globe,
  BookOpen,
  Trash2,
  Calendar,
  Layers,
  ArrowRight,
  Database,
} from 'lucide-react';
import { DocumentItem } from '../api';

interface DocumentLibraryProps {
  documents: DocumentItem[];
  selectedDocId?: string;
  onSelectDoc: (docId: string) => void;
  onDeleteDoc: (docId: string) => void;
  onClose: () => void;
}

export const DocumentLibrary: React.FC<DocumentLibraryProps> = ({
  documents,
  selectedDocId,
  onSelectDoc,
  onDeleteDoc,
  onClose,
}) => {
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

  return (
    <div className="w-full max-w-4xl mx-auto glass-panel p-6 rounded-2xl border border-slate-800 shadow-2xl space-y-5">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">Ingested Document Library</h3>
          <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-semibold">
            {documents.length} sources
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-xs text-slate-400 hover:text-white px-2.5 py-1 rounded bg-slate-900 border border-slate-800"
        >
          Back to Workspace
        </button>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-12 text-slate-500 text-sm">
          No documents ingested yet. Upload a PDF or submit a URL to begin.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[550px] overflow-y-auto pr-1">
          {documents.map((doc) => {
            const isSelected = selectedDocId === doc.id;
            return (
              <div
                key={doc.id}
                onClick={() => {
                  onSelectDoc(doc.id);
                  onClose();
                }}
                className={`p-4 rounded-xl border cursor-pointer transition flex flex-col justify-between group ${
                  isSelected
                    ? 'bg-indigo-950/60 border-indigo-500 shadow-lg shadow-indigo-500/10'
                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-700 hover:bg-slate-850'
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <span className="p-1 rounded bg-slate-800 border border-slate-700">
                        {getSourceIcon(doc.source_type)}
                      </span>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                        {doc.source_type.replace('_', ' ')}
                      </span>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm(`Delete "${doc.title}"?`)) {
                          onDeleteDoc(doc.id);
                        }
                      }}
                      className="text-slate-500 hover:text-red-400 p-1 rounded transition opacity-0 group-hover:opacity-100"
                      title="Delete document"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <h4 className="text-sm font-bold text-white group-hover:text-indigo-300 transition line-clamp-2">
                    {doc.title}
                  </h4>
                  {doc.summary_short && (
                    <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                      {doc.summary_short}
                    </p>
                  )}
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                  <span className="flex items-center gap-1">
                    <Layers className="w-3 h-3" /> {doc.chunk_count || 0} chunks
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" /> {new Date(doc.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
