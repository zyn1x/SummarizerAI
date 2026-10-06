import React, { useState } from 'react';
import {
  FileText,
  ListFilter,
  Lightbulb,
  MessageSquare,
  GraduationCap,
  Brain,
  Wrench,
  Rocket,
  Compass,
  Presentation,
  Check,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

export type ActionMode = 'summary' | 'key_points' | 'actionable_insights' | 'qa';
export type SummaryFormat = 'executive' | 'detailed' | 'bulleted';
export type UserGoal =
  | 'study_exam'
  | 'understand_topic'
  | 'implement_method'
  | 'apply_project'
  | 'find_research_gaps'
  | 'prepare_presentation';

interface ActionSelectorProps {
  currentMode: ActionMode;
  onSelectMode: (mode: ActionMode) => void;
  onTriggerSummary: (format: SummaryFormat) => void;
  onTriggerKeyPoints: () => void;
  onTriggerInsights: (goal: UserGoal, customFocus?: string) => void;
  isLoading: boolean;
}

export const ActionSelector: React.FC<ActionSelectorProps> = ({
  currentMode,
  onSelectMode,
  onTriggerSummary,
  onTriggerKeyPoints,
  onTriggerInsights,
  isLoading,
}) => {
  const [selectedFormat, setSelectedFormat] = useState<SummaryFormat>('executive');
  const [selectedGoal, setSelectedGoal] = useState<UserGoal>('understand_topic');
  const [customFocus, setCustomFocus] = useState('');
  const [showGoalModal, setShowGoalModal] = useState(false);

  const goalOptions = [
    {
      id: 'study_exam',
      label: 'Study for an Exam',
      desc: 'High-yield definitions, key formulas, flashcard concepts & sample exam questions.',
      icon: GraduationCap,
      color: 'from-amber-500/20 to-orange-500/20 border-amber-500/40 text-amber-300',
    },
    {
      id: 'understand_topic',
      label: 'Understand the Topic',
      desc: 'ELI5 mental models, foundational principles, analogies & progressive breakdown.',
      icon: Brain,
      color: 'from-blue-500/20 to-indigo-500/20 border-blue-500/40 text-blue-300',
    },
    {
      id: 'implement_method',
      label: 'Implement the Method',
      desc: 'Technical execution steps, algorithms, code schemas, dependencies & edge cases.',
      icon: Wrench,
      color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/40 text-emerald-300',
    },
    {
      id: 'apply_project',
      label: 'Apply to a Project',
      desc: 'Architecture blueprint, integration roadmap, ROI analysis & risk matrix.',
      icon: Rocket,
      color: 'from-purple-500/20 to-pink-500/20 border-purple-500/40 text-purple-300',
    },
    {
      id: 'find_research_gaps',
      label: 'Find Research Gaps',
      desc: 'Underlying assumptions, methodological limits, open contradictions & future hypotheses.',
      icon: Compass,
      color: 'from-cyan-500/20 to-blue-500/20 border-cyan-500/40 text-cyan-300',
    },
    {
      id: 'prepare_presentation',
      label: 'Prepare a Presentation',
      desc: '5-slide deck outline, slide titles, key bullets, speaker notes & audience Q&A.',
      icon: Presentation,
      color: 'from-rose-500/20 to-red-500/20 border-rose-500/40 text-rose-300',
    },
  ];

  return (
    <div className="w-full glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl space-y-6">
      {/* Prominent Header Prompt */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Interactive Intelligence Flow</span>
          </div>
          <h3 className="text-xl font-extrabold text-white tracking-tight">
            What would you like to do with this content?
          </h3>
        </div>
      </div>

      {/* 4 Main Action Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* Action 1: Summary */}
        <div
          onClick={() => {
            onSelectMode('summary');
            onTriggerSummary(selectedFormat);
          }}
          className={`cursor-pointer rounded-xl p-4 border transition flex flex-col justify-between group ${
            currentMode === 'summary'
              ? 'bg-indigo-950/40 border-indigo-500/80 shadow-md shadow-indigo-500/20 ring-1 ring-indigo-500/30'
              : 'bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-850/60'
          }`}
        >
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-105 transition">
              <FileText className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white">Summary</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Hierarchical map-reduce synthesis for documents of any length.
            </p>
          </div>

          {/* Format selection chips */}
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
            {(['executive', 'detailed', 'bulleted'] as SummaryFormat[]).map((fmt) => (
              <button
                key={fmt}
                onClick={() => {
                  setSelectedFormat(fmt);
                  onSelectMode('summary');
                  onTriggerSummary(fmt);
                }}
                className={`text-[10px] capitalize px-2 py-0.5 rounded-md font-semibold border transition ${
                  selectedFormat === fmt && currentMode === 'summary'
                    ? 'bg-indigo-600 text-white border-indigo-500'
                    : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                {fmt}
              </button>
            ))}
          </div>
        </div>

        {/* Action 2: Key Points */}
        <div
          onClick={() => {
            onSelectMode('key_points');
            onTriggerKeyPoints();
          }}
          className={`cursor-pointer rounded-xl p-4 border transition flex flex-col justify-between group ${
            currentMode === 'key_points'
              ? 'bg-indigo-950/40 border-indigo-500/80 shadow-md shadow-indigo-500/20 ring-1 ring-indigo-500/30'
              : 'bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-850/60'
          }`}
        >
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 group-hover:scale-105 transition">
              <ListFilter className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white">Key Points</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Extract core arguments, quantitative data, and strategic implications.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span className="text-[11px] font-medium text-emerald-400">Deterministic Evidence</span>
            <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:translate-x-1 transition" />
          </div>
        </div>

        {/* Action 3: Actionable Insights */}
        <div
          onClick={() => {
            onSelectMode('actionable_insights');
            setShowGoalModal(true);
          }}
          className={`cursor-pointer rounded-xl p-4 border transition flex flex-col justify-between group ${
            currentMode === 'actionable_insights'
              ? 'bg-indigo-950/40 border-indigo-500/80 shadow-md shadow-indigo-500/20 ring-1 ring-indigo-500/30'
              : 'bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-850/60'
          }`}
        >
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 group-hover:scale-105 transition">
              <Lightbulb className="w-5 h-5" />
            </div>
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-bold text-white">Actionable Insights</h4>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-950/80 border border-amber-800/60 text-amber-400 font-semibold uppercase">
                Goal-Specific
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Tailored for exams, understanding, implementation, projects, or presentations.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
            <span className="text-[11px] text-amber-300 font-medium">Select Your Goal</span>
            <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:translate-x-1 transition" />
          </div>
        </div>

        {/* Action 4: Ask Questions (RAG) */}
        <div
          onClick={() => onSelectMode('qa')}
          className={`cursor-pointer rounded-xl p-4 border transition flex flex-col justify-between group ${
            currentMode === 'qa'
              ? 'bg-indigo-950/40 border-indigo-500/80 shadow-md shadow-indigo-500/20 ring-1 ring-indigo-500/30'
              : 'bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-850/60'
          }`}
        >
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition">
              <MessageSquare className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white">Ask Questions</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Document Q&A with vector search, semantic retrieval, and source citations.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span className="text-[11px] font-medium text-cyan-400">Grounded RAG</span>
            <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:translate-x-1 transition" />
          </div>
        </div>
      </div>

      {/* Goal Selection Modal / Drawer for Actionable Insights */}
      {showGoalModal && (
        <div className="p-6 rounded-xl bg-slate-900/90 border border-indigo-900/50 shadow-2xl space-y-4 animate-in fade-in slide-in-from-top-4 duration-200">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-amber-400" />
              <h4 className="text-base font-bold text-white">What is your primary goal with this content?</h4>
            </div>
            <button
              onClick={() => setShowGoalModal(false)}
              className="text-xs text-slate-400 hover:text-white px-2 py-1 rounded bg-slate-800/50"
            >
              Close
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {goalOptions.map((g) => {
              const Icon = g.icon;
              const isSelected = selectedGoal === g.id;
              return (
                <div
                  key={g.id}
                  onClick={() => setSelectedGoal(g.id as UserGoal)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition flex flex-col justify-between ${
                    isSelected
                      ? `bg-gradient-to-br ${g.color} ring-1 ring-indigo-500/50`
                      : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <div className="w-8 h-8 rounded-lg bg-slate-900/80 flex items-center justify-center">
                        <Icon className="w-4 h-4" />
                      </div>
                      {isSelected && <Check className="w-4 h-4 text-emerald-400" />}
                    </div>
                    <h5 className="text-xs font-bold text-white">{g.label}</h5>
                    <p className="text-[11px] text-slate-400 leading-snug">{g.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Optional custom focus input */}
          <div className="space-y-1.5 pt-2">
            <label className="text-xs text-slate-400 font-medium">
              Optional: Specify areas of focus or constraints (e.g. "Focus on section 3", "Target undergraduate level"):
            </label>
            <input
              type="text"
              value={customFocus}
              onChange={(e) => setCustomFocus(e.target.value)}
              placeholder="e.g. Focus on practical implementation details and edge cases..."
              className="w-full glass-input px-3.5 py-2.5 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none"
            />
          </div>

          {/* Action Trigger Button */}
          <div className="flex justify-end gap-2 pt-2">
            <button
              onClick={() => setShowGoalModal(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                setShowGoalModal(false);
                onTriggerInsights(selectedGoal, customFocus);
              }}
              disabled={isLoading}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 via-amber-500 to-indigo-600 hover:from-amber-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-amber-500/20 flex items-center gap-2"
            >
              <Lightbulb className="w-3.5 h-3.5" />
              <span>Generate Goal-Specific Intelligence</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
