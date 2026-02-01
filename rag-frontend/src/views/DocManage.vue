<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-3xl font-bold text-white tracking-tight">文档库管理</h2>
        <p class="mt-2 text-slate-400 text-lg">上传并管理您的知识库文档，支持 PDF, Word, Markdown, TXT 格式</p>
      </div>
    </div>

    <!-- Upload Card -->
    <div class="relative group">
      <div class="absolute -inset-0.5 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-2xl opacity-20 group-hover:opacity-40 transition duration-500 blur"></div>
      <div class="relative bg-slate-900/80 border border-white/10 rounded-xl p-8 text-center transition-all duration-300 backdrop-blur-md">
        <div class="border-2 border-dashed border-slate-700 rounded-xl p-12 hover:border-violet-500/50 hover:bg-violet-500/5 transition-all duration-300 cursor-pointer group/upload">
          <div class="flex flex-col items-center gap-6">
             <div class="p-5 bg-slate-800 rounded-full group-hover/upload:scale-110 transition-transform duration-300 shadow-xl shadow-black/20 ring-1 ring-white/10">
               <svg class="w-10 h-10 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
               </svg>
             </div>
             <div>
                <p class="text-xl font-medium text-white mb-2">点击或拖拽文件到此处上传</p>
                <p class="text-sm text-slate-500">支持 PDF, Word, Markdown, TXT (最大 10MB)</p>
             </div>
          </div>
        </div>
      </div>
    </div>

    <!-- List -->
    <div class="bg-slate-900/50 border border-white/5 rounded-xl overflow-hidden backdrop-blur-sm shadow-xl">
      <div class="px-6 py-4 border-b border-white/5 bg-white/5 flex items-center justify-between">
        <h3 class="text-lg font-medium text-white flex items-center gap-2">
          <span class="w-1.5 h-4 bg-violet-500 rounded-full"></span>
          已上传文档
        </h3>
        <span class="text-xs px-2 py-1 bg-slate-800 rounded border border-white/5 text-slate-400">Total: 0</span>
      </div>
      <div class="p-12 text-center text-slate-500 flex flex-col items-center justify-center min-h-[200px]">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-slate-800/50 mb-6 ring-1 ring-white/5">
           <svg class="w-10 h-10 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
           </svg>
        </div>
        <p class="text-lg font-medium text-slate-400">暂无上传文档</p>
        <p class="text-sm mt-1">请上传文档以开始构建知识库</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Logic for file upload and listing will go here
</script>
