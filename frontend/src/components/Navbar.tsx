import React from 'react';
import { Cpu, FileText, Database, Sparkles } from 'lucide-react';

interface NavbarProps {
  llmInfo?: {
    ollama_online: boolean;
    active_model: string;
    default_provider: string;
  };
  docCount: number;
  onOpenLibrary: () => void;
  onNewDoc: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ llmInfo, docCount, onOpenLibrary, onNewDoc }) => {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3 cursor-pointer" onClick={onNewDoc}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 p-0.5 shadow-lg shadow-indigo-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-indigo-400" />
            </div>
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              Summarizer<span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-emerald-400">AI</span>
              <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-indigo-950/80 text-indigo-300 border border-indigo-800/50">
                v0.1
              </span>
            </h1>
            <p className="text-[11px] text-slate-400 hidden sm:block">Local-First Content Intelligence</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* LLM Status Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <div className="flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full ${
                  llmInfo?.ollama_online ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
                }`}
              />
              <span className="text-slate-300 font-medium">
                {llmInfo?.ollama_online ? `Ollama (${llmInfo.active_model})` : 'Offline Engine Active'}
              </span>
            </div>
          </div>

          {/* Library Button */}
          <button
            onClick={onOpenLibrary}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 text-xs font-medium transition"
          >
            <Database className="w-3.5 h-3.5 text-slate-400" />
            <span>Library</span>
            <span className="ml-1 px-1.5 py-0.2 rounded-full bg-indigo-600/30 text-indigo-300 text-[11px] font-semibold border border-indigo-500/30">
              {docCount}
            </span>
          </button>

          {/* New Document Button */}
          <button
            onClick={onNewDoc}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition active:scale-95"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Ingest Source</span>
          </button>
        </div>
      </div>
    </header>
  );
};
