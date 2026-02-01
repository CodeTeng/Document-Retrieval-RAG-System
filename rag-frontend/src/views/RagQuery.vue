<template>
  <div class="h-[calc(100vh-10rem)] flex flex-col gap-6">
    <div class="flex items-center justify-between">
       <h2 class="text-3xl font-bold text-white tracking-tight">智能问答</h2>
       <div class="px-3 py-1 bg-violet-500/10 border border-violet-500/20 rounded-full text-xs text-violet-400 flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse"></span>
          AI 模型准备就绪
       </div>
    </div>

    <!-- Main Chat/Result Area -->
    <div class="flex-1 bg-slate-900/80 border border-white/10 rounded-2xl p-6 overflow-hidden backdrop-blur-md shadow-2xl flex flex-col relative">
      <!-- Decor -->
      <div class="absolute top-0 right-0 w-96 h-96 bg-violet-500/10 rounded-full blur-[100px] -z-10 pointer-events-none"></div>
      <div class="absolute bottom-0 left-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-[80px] -z-10 pointer-events-none"></div>

      <!-- Empty State / Result Container -->
      <div class="flex-1 overflow-y-auto custom-scrollbar space-y-6 pr-2">
         <!-- Empty State -->
         <div class="h-full flex flex-col items-center justify-center text-slate-500 opacity-60">
             <div class="w-24 h-24 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 ring-1 ring-white/5">
               <svg class="w-10 h-10 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
               </svg>
             </div>
             <p class="text-xl font-medium text-slate-400">请输入您的问题以开始检索</p>
             <p class="text-sm mt-2 text-slate-600">基于 RAG 技术，为您提供精准文档问答</p>
         </div>
      </div>

      <!-- Input Area -->
      <div class="mt-6 pt-6 border-t border-white/5 relative z-10">
        <div class="relative group">
           <div class="absolute -inset-0.5 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-xl opacity-30 group-hover:opacity-60 transition duration-300 blur-md"></div>
           <div class="relative flex gap-2 bg-slate-950 rounded-xl p-1.5 ring-1 ring-white/10">
             <textarea 
               rows="1"
               class="flex-1 bg-transparent border-0 focus:ring-0 text-slate-200 placeholder-slate-600 resize-none py-3 px-4 leading-relaxed focus:outline-none"
               placeholder="在此输入您的问题..."
             ></textarea>
             <button class="px-8 py-2 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold rounded-lg shadow-lg shadow-violet-900/20 transition-all duration-200 flex items-center gap-2 transform active:scale-95">
               <span>提问</span>
               <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
               </svg>
             </button>
           </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Logic for query and results will go here
</script>
