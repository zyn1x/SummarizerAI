import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Loader2,
  Sparkles,
  Bot,
  User,
  Quote,
  ShieldCheck,
  AlertTriangle,
  ExternalLink,
} from 'lucide-react';
import { QAResult, CitationItem, askQuestion, getQAHistory } from '../api';

interface QAChatProps {
  documentId: string;
  onCitationClick: (citation: CitationItem) => void;
}

export const QAChat: React.FC<QAChatProps> = ({ documentId, onCitationClick }) => {
  const [messages, setMessages] = useState<QAResult[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isAsking, setIsAsking] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const hist = await getQAHistory(documentId);
        setMessages(hist);
      } catch {
        // history fetch error ignored
      }
    };
    fetchHistory();
  }, [documentId]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isAsking]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputQuery.trim() || isAsking) return;

    const q = inputQuery.trim();
    setInputQuery('');
    setIsAsking(true);

    try {
      const res = await askQuestion(documentId, q);
      setMessages((prev) => [...prev, res]);
    } catch (err: any) {
      // Add error mock message
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          document_id: documentId,
          question: q,
          answer: `Error answering inquiry: ${err.message || 'Server error'}`,
          is_grounded: false,
          citations: [],
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsAsking(false);
    }
  };

  const sampleQuestions = [
    'What is the core problem addressed in this content?',
    'What methodologies or algorithms are proposed?',
    'What are the key conclusions and quantitative results?',
  ];

  return (
    <div className="w-full glass-panel rounded-2xl border border-slate-800 flex flex-col h-[650px] shadow-2xl overflow-hidden">
      {/* Chat Header */}
      <div className="p-4 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Document Q&A / Grounded RAG</h4>
            <p className="text-[11px] text-slate-400">
              Retrieval-augmented generation grounded with deterministic source citations
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500">
              <Bot className="w-6 h-6 text-cyan-400" />
            </div>
            <div className="space-y-1 max-w-sm">
              <h5 className="text-sm font-bold text-slate-200">Ask Anything About This Document</h5>
              <p className="text-xs text-slate-400">
                The AI searches semantic vector chunks and provides answers with exact page, section, or timestamp evidence.
              </p>
            </div>

            <div className="space-y-2 pt-2 w-full max-w-md">
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Suggested Questions:</p>
              {sampleQuestions.map((sq, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setInputQuery(sq);
                  }}
                  className="w-full text-left p-2.5 rounded-lg bg-slate-900/80 hover:bg-slate-850 border border-slate-800 text-xs text-slate-300 transition"
                >
                  "{sq}"
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m) => (
            <div key={m.id} className="space-y-3">
              {/* User Question */}
              <div className="flex items-start gap-2.5 justify-end">
                <div className="max-w-[80%] rounded-2xl rounded-tr-none px-4 py-2.5 bg-indigo-600 text-white text-xs leading-relaxed shadow-md">
                  {m.question}
                </div>
                <div className="w-7 h-7 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-300 shrink-0">
                  <User className="w-4 h-4" />
                </div>
              </div>

              {/* Assistant Answer */}
              <div className="flex items-start gap-2.5">
                <div className="w-7 h-7 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-300 shrink-0 mt-0.5">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="max-w-[85%] space-y-2.5">
                  <div className="rounded-2xl rounded-tl-none px-4 py-3 bg-slate-900 border border-slate-800 text-slate-200 text-xs leading-relaxed space-y-2 shadow-sm">
                    <p className="whitespace-pre-line">{m.answer}</p>

                    {/* Grounding badge */}
                    <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
                      {m.is_grounded ? (
                        <span className="flex items-center gap-1 text-emerald-400 font-medium">
                          <ShieldCheck className="w-3.5 h-3.5" /> Grounded in verified evidence
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-amber-400 font-medium">
                          <AlertTriangle className="w-3.5 h-3.5" /> Out-of-bounds or insufficient source detail
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Evidence Citations */}
                  {m.citations && m.citations.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pl-1">
                      {m.citations.map((c, idx) => (
                        <button
                          key={idx}
                          onClick={() => onCitationClick(c)}
                          className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-md bg-slate-900 hover:bg-slate-800 border border-slate-700 hover:border-cyan-500 text-cyan-300 transition group"
                        >
                          <Quote className="w-2.5 h-2.5 text-cyan-400" />
                          <span>{c.citation_label}</span>
                          <ExternalLink className="w-2.5 h-2.5 text-slate-500 group-hover:text-cyan-300" />
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}

        {isAsking && (
          <div className="flex items-start gap-2.5">
            <div className="w-7 h-7 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-300 shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-3 rounded-2xl rounded-tl-none bg-slate-900 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
              <span>Retrieving vector embeddings and synthesizing answer...</span>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input Box */}
      <form onSubmit={handleSend} className="p-3 bg-slate-900/60 border-t border-slate-800 flex items-center gap-2">
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Ask a question about this source (e.g. 'What are the main findings?')..."
          className="flex-1 glass-input px-4 py-2.5 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={!inputQuery.trim() || isAsking}
          className="p-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white transition active:scale-95 shadow-md shadow-cyan-600/30"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
