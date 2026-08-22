"use client";

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { LayoutDashboard, Activity, Route, History, Settings, Bell, GitBranch, SlidersHorizontal, Plus, Send, Sparkles, Database, Copy, ThumbsUp, RefreshCcw } from 'lucide-react';
import { Cpu3 } from 'reicon-react';
import MagneticButton from '@/components/ui/MagneticButton';

export default function ChatDashboard() {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [input, setInput] = useState('');

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
  };

  return (
    <div className="h-screen flex bg-[#050505] text-[#FAFAFA] overflow-hidden selection:bg-amd-red/30">
      
      {/* Sidebar Navigation */}
      <nav className="w-20 flex flex-col items-center py-8 bg-[#0A0A0A]/50 backdrop-blur-2xl border-r border-white/5 z-50">
        <div className="mb-12">
          <div className="w-10 h-10 bg-amd-red rounded-lg flex items-center justify-center font-bold text-white text-xs tracking-tighter shadow-[0_0_20px_rgba(239,68,68,0.3)]">
            AMD
          </div>
        </div>
        
        <div className="flex flex-col gap-8 items-center flex-1">
          <NavItem icon={<LayoutDashboard className="w-5 h-5" />} label="Dashboard" active />
          <NavItem icon={<Activity className="w-5 h-5" />} label="Analytics" />
          <NavItem icon={<Route className="w-5 h-5" />} label="Routing" />
          <NavItem icon={<History className="w-5 h-5" />} label="History" />
        </div>
        
        <div className="mt-auto">
          <NavItem icon={<Settings className="w-5 h-5" />} label="Settings" />
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 flex overflow-hidden relative">
        {/* Glow Effects */}
        <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] bg-amd-red/5 blur-[120px] rounded-full pointer-events-none" />
        <div className="absolute bottom-[-20%] left-[-10%] w-[600px] h-[600px] bg-amd-blue/5 blur-[120px] rounded-full pointer-events-none" />

        {/* Analytics Panel */}
        <aside className="w-80 bg-[#0A0A0A]/30 backdrop-blur-xl border-r border-white/5 flex flex-col p-6 overflow-y-auto hidden lg:flex z-10">
          <h2 className="text-sm font-medium text-white/80 mb-8 uppercase tracking-widest flex items-center gap-2">
            <Activity className="w-4 h-4 text-amd-red" />
            Telemetry
          </h2>

          <MetricCard 
            label="Tokens Saved" 
            value="1.2M" 
            subValue="+14% vs prev. hour" 
            progress={78} 
            color="bg-amd-red" 
          />

          <div className="p-5 rounded-2xl bg-[#111] border border-white/5 mb-8 group hover:border-white/10 transition-colors">
            <p className="text-[10px] text-white/40 uppercase tracking-widest mb-3">Active Instance</p>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center border border-white/10">
                <Cpu3 className="w-5 h-5 text-amd-blue" />
              </div>
              <div>
                <p className="text-sm font-medium text-white">Llama 3 70B</p>
                <p className="text-xs text-white/50">ROCm Optimized</p>
              </div>
            </div>
          </div>

          <div className="mt-4">
            <p className="text-[10px] text-white/40 uppercase tracking-widest mb-6">Routing Topology</p>
            <div className="space-y-6 relative before:absolute before:left-4 before:top-4 before:bottom-4 before:w-px before:bg-gradient-to-b before:from-amd-red before:via-white/10 before:to-transparent">
              <TopologyNode label="L1" title="Semantic Filter" sub="Latency: 12ms" color="bg-amd-red" active />
              <TopologyNode label="L2" title="Zero-Token Router" sub="Cache Hit" color="bg-amd-blue" active />
              <TopologyNode label="L3" title="Cloud Fallback" sub="Bypassed" color="bg-white/10" />
            </div>
          </div>
        </aside>

        {/* Chat Interface */}
        <section className="flex-1 flex flex-col relative z-10">
          {/* Header */}
          <header className="flex justify-between items-center px-8 h-20 bg-transparent border-b border-white/5 backdrop-blur-sm">
            <div className="flex items-center gap-3">
              <span className="font-medium text-lg text-white">Console</span>
              <span className="px-2 py-0.5 rounded-full bg-amd-red/10 text-amd-red text-[10px] font-bold tracking-widest border border-amd-red/20">PREMIUM</span>
            </div>
            <div className="flex items-center gap-2">
              <MagneticButton><button className="p-2.5 text-white/50 hover:text-white transition-colors rounded-full hover:bg-white/5"><Bell className="w-4 h-4" /></button></MagneticButton>
              <MagneticButton><button className="p-2.5 text-white/50 hover:text-white transition-colors rounded-full hover:bg-white/5"><GitBranch className="w-4 h-4" /></button></MagneticButton>
              <MagneticButton><button className="p-2.5 text-white/50 hover:text-white transition-colors rounded-full hover:bg-white/5"><SlidersHorizontal className="w-4 h-4" /></button></MagneticButton>
              <div className="w-9 h-9 rounded-full ml-4 bg-gradient-to-tr from-amd-red to-orange-500 p-[1px]">
                <div className="w-full h-full rounded-full bg-[#0A0A0A] border border-black overflow-hidden">
                  <img className="w-full h-full object-cover opacity-80 mix-blend-luminosity" src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=100&q=80" alt="User" />
                </div>
              </div>
            </div>
          </header>

          {/* Messages */}
          <div className="flex-1 p-8 overflow-y-auto custom-scrollbar flex flex-col gap-8">
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex justify-end">
              <div className="max-w-[70%]">
                <div className="bg-[#1A1A1A] text-white p-5 rounded-2xl rounded-tr-sm border border-white/5 text-sm leading-relaxed">
                  Analyze the efficiency of our recent semantic routing layer. Are we seeing significant token reductions in the North American cluster?
                </div>
                <div className="text-[10px] text-white/30 uppercase tracking-widest mt-2 text-right">10:24 AM</div>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="flex gap-4 max-w-[85%]">
              <div className="w-10 h-10 shrink-0 rounded-xl bg-[#111] border border-amd-red/20 flex items-center justify-center">
                <div className="w-2 h-2 rounded-full bg-amd-red animate-pulse" />
              </div>
              <div>
                <div className="bg-transparent border border-white/5 p-6 rounded-2xl rounded-tl-sm relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent" />
                  <div className="relative z-10 text-sm leading-relaxed text-white/80">
                    <p className="mb-6">
                      Optimization analysis complete. The semantic cache layer is performing at <span className="text-white font-medium">92.4% efficiency</span> for the North American cluster.
                    </p>
                    
                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div className="p-4 bg-[#0A0A0A] rounded-xl border border-white/5">
                        <p className="text-[10px] text-white/40 uppercase tracking-widest mb-2">Token Reduction</p>
                        <p className="text-2xl font-light text-white">440K <span className="text-sm text-green-500 font-medium">↓</span></p>
                      </div>
                      <div className="p-4 bg-[#0A0A0A] rounded-xl border border-white/5">
                        <p className="text-[10px] text-white/40 uppercase tracking-widest mb-2">Avg Latency</p>
                        <p className="text-2xl font-light text-white">18ms <span className="text-sm text-amd-blue font-medium">~</span></p>
                      </div>
                    </div>
                    
                    <p>
                      Recommendation: shift the L3 spillover to the <span className="text-white border-b border-white/20 pb-0.5">Virginia-B8 cluster</span> to reduce egress costs by an additional 4%.
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4 mt-3 pl-2">
                  <span className="text-[10px] text-white/30 uppercase tracking-widest">Router OS</span>
                  <div className="flex gap-2">
                    <button className="text-white/30 hover:text-white transition-colors"><Copy className="w-3.5 h-3.5" /></button>
                    <button className="text-white/30 hover:text-white transition-colors"><ThumbsUp className="w-3.5 h-3.5" /></button>
                    <button className="text-white/30 hover:text-white transition-colors"><RefreshCcw className="w-3.5 h-3.5" /></button>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Input Area */}
          <div className="p-8 pt-0">
            <div className="max-w-4xl mx-auto">
              <div className="relative bg-[#0A0A0A] rounded-2xl border border-white/10 overflow-hidden focus-within:border-white/30 transition-colors shadow-2xl">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-amd-red via-transparent to-amd-blue opacity-50" />
                <div className="flex items-end p-3 gap-3">
                  <button className="p-3 text-white/40 hover:text-white transition-colors rounded-xl hover:bg-white/5">
                    <Plus className="w-5 h-5" />
                  </button>
                  <textarea 
                    ref={textareaRef}
                    value={input}
                    onChange={handleInput}
                    placeholder="Enter query to route..." 
                    className="flex-1 bg-transparent border-none outline-none text-white placeholder-white/30 py-3.5 resize-none text-sm font-light leading-relaxed max-h-[200px]"
                    rows={1}
                  />
                  <div className="p-1">
                    <MagneticButton>
                      <button className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all ${input.trim() ? 'bg-white text-black shadow-lg hover:scale-105' : 'bg-[#111] text-white/30'}`}>
                        <Send className="w-5 h-5" />
                      </button>
                    </MagneticButton>
                  </div>
                </div>
              </div>
              <div className="flex justify-between items-center px-4 mt-4">
                <div className="flex gap-6">
                  <span className="flex items-center gap-2 text-[10px] text-white/40 uppercase tracking-widest font-medium">
                    <Sparkles className="w-3 h-3 text-amd-red" />
                    Auto-Route
                  </span>
                  <span className="flex items-center gap-2 text-[10px] text-white/40 uppercase tracking-widest font-medium">
                    <Database className="w-3 h-3 text-amd-blue" />
                    Local Context
                  </span>
                </div>
                <span className="text-[10px] text-white/30 uppercase tracking-widest">Enter to send</span>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

function NavItem({ icon, label, active = false }: { icon: React.ReactNode, label: string, active?: boolean }) {
  return (
    <div className="relative group w-full flex justify-center">
      <MagneticButton>
        <button className={`p-3.5 rounded-2xl transition-all duration-300 ${active ? 'bg-white text-black shadow-lg' : 'text-white/40 hover:text-white hover:bg-white/5'}`}>
          {icon}
        </button>
      </MagneticButton>
      <div className="absolute left-full ml-4 top-1/2 -translate-y-1/2 px-3 py-1.5 bg-[#111] border border-white/10 rounded-lg text-xs font-medium text-white opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
        {label}
      </div>
    </div>
  );
}

function MetricCard({ label, value, subValue, progress, color }: { label: string, value: string, subValue: string, progress: number, color: string }) {
  return (
    <div className="p-5 rounded-2xl bg-[#111] border border-white/5 mb-6 group hover:border-white/10 transition-colors">
      <p className="text-[10px] text-white/40 uppercase tracking-widest mb-3">{label}</p>
      <div className="flex items-baseline gap-3 mb-4">
        <span className="text-3xl font-light text-white tracking-tight">{value}</span>
        <span className="text-xs text-white/50">{subValue}</span>
      </div>
      <div className="h-1 w-full bg-[#1A1A1A] rounded-full overflow-hidden">
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={`h-full ${color}`} 
        />
      </div>
    </div>
  );
}

function TopologyNode({ label, title, sub, color, active = false }: { label: string, title: string, sub: string, color: string, active?: boolean }) {
  return (
    <div className={`flex items-center gap-5 relative z-10 ${active ? 'opacity-100' : 'opacity-40'}`}>
      <div className={`w-8 h-8 rounded-full ${color} flex items-center justify-center text-[10px] font-bold ${active ? 'text-white' : 'text-white/50'} shadow-lg ring-4 ring-[#0A0A0A]`}>
        {label}
      </div>
      <div className="flex-1">
        <p className="text-xs font-medium text-white mb-0.5">{title}</p>
        <p className="text-[10px] text-white/40">{sub}</p>
      </div>
    </div>
  );
}
