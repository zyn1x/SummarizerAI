import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, AlertTriangle, Layers, Cpu, FileSearch, ArrowRight } from 'lucide-react';
import { getJobStatus, JobStatus } from '../api';

interface ProcessingProgressProps {
  jobId: string;
  onComplete: (documentId: string) => void;
  onError: (msg: string) => void;
}

export const ProcessingProgress: React.FC<ProcessingProgressProps> = ({ jobId, onComplete, onError }) => {
  const [job, setJob] = useState<JobStatus | null>(null);

  useEffect(() => {
    let interval: any;

    const check = async () => {
      try {
        const data = await getJobStatus(jobId);
        setJob(data);

        if (data.status === 'ready') {
          clearInterval(interval);
          setTimeout(() => onComplete(data.document_id), 800);
        } else if (data.status === 'failed') {
          clearInterval(interval);
          onError(data.error_message || 'Processing failed');
        }
      } catch (err: any) {
        clearInterval(interval);
        onError(err.message || 'Error tracking processing job');
      }
    };

    check();
    interval = setInterval(check, 1200);

    return () => clearInterval(interval);
  }, [jobId, onComplete, onError]);

  const steps = [
    { key: 'uploading', label: 'Uploading & Validating', icon: Layers },
    { key: 'extracting', label: 'Extracting Content', icon: FileSearch },
    { key: 'normalizing', label: 'Structure Normalization', icon: Cpu },
    { key: 'chunking', label: 'Structure-Aware Chunking', icon: Layers },
    { key: 'analyzing', label: 'Hierarchical Analysis', icon: CheckCircle2 },
  ];

  const getStepStatus = (stepKey: string) => {
    if (!job) return 'pending';
    const order = ['uploading', 'extracting', 'normalizing', 'chunking', 'analyzing', 'ready'];
    const currentIdx = order.indexOf(job.status);
    const stepIdx = order.indexOf(stepKey);

    if (job.status === 'failed') return 'failed';
    if (stepIdx < currentIdx || job.status === 'ready') return 'completed';
    if (stepIdx === currentIdx) return 'active';
    return 'pending';
  };

  return (
    <div className="w-full max-w-2xl mx-auto glass-panel p-8 rounded-2xl border border-slate-800 shadow-2xl space-y-6">
      <div className="text-center space-y-2">
        <div className="inline-flex p-3 rounded-2xl bg-indigo-950/80 border border-indigo-800/60 text-indigo-400 mb-1">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>
        <h3 className="text-xl font-bold text-white">Synthesizing Content Intelligence</h3>
        <p className="text-sm text-slate-400">
          {job?.current_step || 'Processing document streams and extracting structure...'}
        </p>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs font-semibold text-slate-400">
          <span>Progress</span>
          <span className="text-indigo-400">{job?.progress_percent || 15}%</span>
        </div>
        <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
          <div
            className="h-full bg-gradient-to-r from-indigo-500 via-indigo-400 to-emerald-400 transition-all duration-500 ease-out rounded-full shadow-lg shadow-indigo-500/50"
            style={{ width: `${job?.progress_percent || 15}%` }}
          />
        </div>
      </div>

      {/* Steps List */}
      <div className="space-y-3 pt-2">
        {steps.map((s, idx) => {
          const status = getStepStatus(s.key);
          const Icon = s.icon;
          return (
            <div
              key={idx}
              className={`flex items-center justify-between p-3 rounded-xl border transition ${
                status === 'completed'
                  ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-300'
                  : status === 'active'
                  ? 'bg-indigo-950/40 border-indigo-700/60 text-indigo-200'
                  : 'bg-slate-900/30 border-slate-800 text-slate-500'
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                    status === 'completed'
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : status === 'active'
                      ? 'bg-indigo-500/20 text-indigo-400'
                      : 'bg-slate-800 text-slate-500'
                  }`}
                >
                  {status === 'active' ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : status === 'completed' ? (
                    <CheckCircle2 className="w-4 h-4" />
                  ) : (
                    <Icon className="w-4 h-4" />
                  )}
                </div>
                <span className="text-xs font-semibold">{s.label}</span>
              </div>
              <span className="text-[11px] font-medium uppercase tracking-wider">
                {status === 'completed' ? 'Done' : status === 'active' ? 'Working...' : 'Queued'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
