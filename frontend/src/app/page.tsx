"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { ArrowRight2, Cpu3, Diagram2, Bolt } from "reicon-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import MagneticButton from "@/components/ui/MagneticButton";

const fadeUp: any = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] } }
};

const stagger: any = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.15 } }
};

export default function LandingPage() {
  const { scrollYProgress } = useScroll();
  const y1 = useTransform(scrollYProgress, [0, 1], [0, -100]);
  const y2 = useTransform(scrollYProgress, [0, 1], [0, -50]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  return (
    <div className="min-h-[150vh] bg-[#050505] text-[#FAFAFA] font-body selection:bg-amd-red/30">
      {/* Navigation */}
      <nav className="fixed top-0 w-full border-b border-white/5 bg-[#050505]/60 backdrop-blur-xl z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <MagneticButton>
            <div className="flex items-center gap-2 cursor-pointer">
              <div className="w-8 h-8 bg-amd-red rounded-sm flex items-center justify-center font-bold text-white tracking-tighter">
                AMD
              </div>
              <span className="font-medium tracking-tight text-lg">Zero-Token Router</span>
            </div>
          </MagneticButton>
          <div className="flex items-center gap-6">
            <MagneticButton>
              <Link href="https://github.com/HamzaKhanBUIC/amd-developer-hackathon-track1" target="_blank" className="text-sm font-medium text-white/70 hover:text-white transition-colors">
                GitHub
              </Link>
            </MagneticButton>
            <MagneticButton>
              <Link 
                href="/chat" 
                className="text-sm font-medium bg-white text-black px-5 py-2.5 rounded-full hover:bg-white/90 transition-colors"
              >
                Launch App
              </Link>
            </MagneticButton>
          </div>
        </div>
      </nav>

      <main className="pt-32 pb-16 px-6 max-w-7xl mx-auto overflow-hidden relative">
        
        {/* Glow effect */}
        <div className="absolute top-[-10%] left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-amd-red/10 blur-[120px] rounded-full pointer-events-none" />

        {/* Hero Section */}
        <motion.section 
          initial="hidden" 
          animate="visible" 
          style={{ y: y1, opacity }}
          variants={stagger}
          className="py-32 md:py-48 flex flex-col items-center text-center max-w-4xl mx-auto relative z-10"
        >
          <motion.div variants={fadeUp} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs font-medium mb-12 tracking-wide uppercase text-white/80">
            <span className="w-1.5 h-1.5 rounded-full bg-amd-red animate-pulse" />
            Powered by AMD Instinct
          </motion.div>
          
          <motion.h1 variants={fadeUp} className="text-6xl md:text-8xl font-semibold tracking-tighter leading-[1.05] mb-8">
            Intelligent Routing for <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-amd-red to-orange-500">
              Zero-Token Efficiency
            </span>
          </motion.h1>
          
          <motion.p variants={fadeUp} className="text-xl md:text-2xl text-white/60 mb-12 max-w-2xl leading-relaxed font-light">
            A semantic router that intercepts large language model queries, classifying and answering them via high-efficiency local models before hitting cloud APIs.
          </motion.p>
          
          <motion.div variants={fadeUp} className="flex flex-col sm:flex-row items-center gap-6">
            <MagneticButton>
              <Link 
                href="/chat" 
                className="flex items-center gap-3 bg-white text-black px-8 py-4 rounded-full font-medium text-lg hover:bg-white/90 transition-colors"
              >
                Start Routing
                <ArrowRight2 className="w-5 h-5" />
              </Link>
            </MagneticButton>
            <MagneticButton>
              <Link 
                href="#architecture" 
                className="flex items-center gap-2 bg-transparent border border-white/20 text-white px-8 py-4 rounded-full font-medium text-lg hover:bg-white/5 transition-colors"
              >
                View Architecture
              </Link>
            </MagneticButton>
          </motion.div>
        </motion.section>

        {/* Features Grid */}
        <motion.section 
          id="architecture"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={stagger}
          style={{ y: y2 }}
          className="py-32 relative z-10"
        >
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Cpu3 className="w-8 h-8 text-amd-red" />}
              title="AMD Instinct Accelerated"
              description="Built to run optimally on AMD ROCm hardware, maximizing inference throughput for local semantic classification."
            />
            <FeatureCard 
              icon={<Diagram2 className="w-8 h-8 text-white" />}
              title="Semantic Thresholding"
              description="Dual-tier funnel using local embeddings and classifiers to perfectly route complex versus simple queries."
            />
            <FeatureCard 
              icon={<Bolt className="w-8 h-8 text-white" />}
              title="Zero-Token Cost"
              description="Intercept repetitive and simple queries locally, dropping cloud model costs by up to 85 percent."
            />
          </div>
        </motion.section>

      </main>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <motion.div 
      variants={fadeUp}
      className="p-10 rounded-[32px] bg-[#0A0A0A] border border-white/5 hover:border-white/10 transition-all duration-500 hover:-translate-y-2 group relative overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      <div className="relative z-10">
        <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mb-8 group-hover:scale-110 group-hover:bg-white/10 transition-all duration-500">
          {icon}
        </div>
        <h3 className="text-2xl font-medium tracking-tight mb-4">{title}</h3>
        <p className="text-white/50 leading-relaxed text-lg">
          {description}
        </p>
      </div>
    </motion.div>
  );
}
