import React from 'react';
import { ShieldCheck, Cpu, Sparkles } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-auto border-t border-slate-800/80 bg-slate-950/80 backdrop-blur-md py-6 px-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-400">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 font-medium text-slate-300">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            SummarizerAI Intelligence Platform
          </span>
          <span className="text-slate-600">|</span>
          <span className="flex items-center gap-1">
            <Cpu className="w-3 h-3 text-emerald-400" /> Local-First Architecture
          </span>
          <span className="text-slate-600">|</span>
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-cyan-400" /> SSRF & Privacy Protected
          </span>
        </div>

        <div className="flex items-center gap-2">
          <p className="font-semibold text-slate-200">
            Built by <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-emerald-400 font-bold">Dikshant Sharma</span>
          </p>
        </div>
      </div>
    </footer>
  );
};
