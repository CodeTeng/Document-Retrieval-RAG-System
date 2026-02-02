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
    <div class="flex-1 bg-zinc-900/80 border border-white/10 rounded-2xl p-6 overflow-hidden backdrop-blur-md shadow-2xl flex flex-col relative">
      <!-- Decor -->
      <div class="absolute top-0 right-0 w-96 h-96 bg-violet-500/10 rounded-full blur-[100px] -z-10 pointer-events-none"></div>
      <div class="absolute bottom-0 left-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-[80px] -z-10 pointer-events-none"></div>

      <!-- Chat Container -->
      <div ref="chatContainer" class="flex-1 overflow-y-auto custom-scrollbar space-y-6 pr-2 scroll-smooth">
         <!-- Empty State -->
         <div v-if="history.length === 0" class="h-full flex flex-col items-center justify-center text-zinc-500 opacity-60">
             <div class="w-24 h-24 bg-zinc-800/50 rounded-full flex items-center justify-center mb-6 ring-1 ring-white/5">
               <svg class="w-10 h-10 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
               </svg>
             </div>
             <p class="text-xl font-medium text-zinc-400">请输入您的问题以开始检索</p>
             <p class="text-sm mt-2 text-zinc-600">基于 RAG 技术，为您提供精准文档问答</p>
         </div>

         <!-- Message List -->
         <div v-else class="space-y-8 pb-4">
            <div v-for="(msg, index) in history" :key="index" :class="['flex w-full', msg.role === 'user' ? 'justify-end' : 'justify-start']">
                
                <!-- User Message -->
                <div v-if="msg.role === 'user'" class="max-w-[80%]">
                    <div class="bg-violet-600/20 border border-violet-500/20 text-white rounded-2xl rounded-tr-sm px-6 py-4 shadow-lg backdrop-blur-sm">
                        {{ msg.content }}
                    </div>
                </div>

                <!-- AI Message -->
                <div v-else class="max-w-[90%] w-full">
                    <div class="bg-zinc-800/40 border border-white/5 rounded-2xl rounded-tl-sm p-6 shadow-xl backdrop-blur-sm">
                        <!-- Header -->
                        <div class="flex items-center gap-3 mb-4 pb-3 border-b border-white/5">
                            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg">
                                <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <span class="font-bold text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-indigo-400">AI 智能回答</span>
                            <span v-if="msg.time" class="ml-auto text-xs text-zinc-500 font-mono flex items-center gap-1">
                                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                {{ msg.time.toFixed(2) }}s
                            </span>
                        </div>

                        <!-- Content (Markdown) -->
                        <div class="prose prose-invert prose-zinc max-w-none text-zinc-300 leading-relaxed" v-html="renderMarkdown(msg.content)"></div>

                        <!-- Details (Process & Chunks) -->
                        <div v-if="msg.process || msg.chunks" class="mt-6 space-y-2">
                             <!-- Retrieval Process -->
                            <div v-if="msg.process && msg.process.length > 0" class="rounded-lg bg-black/20 overflow-hidden border border-white/5">
                                <button @click="msg.showProcess = !msg.showProcess" 
                                        class="w-full px-4 py-2 flex items-center justify-between text-xs font-medium text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors">
                                    <span class="flex items-center gap-2">
                                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                        </svg>
                                        检索思考过程 ({{ msg.process.length }} 步)
                                    </span>
                                    <svg class="w-4 h-4 transform transition-transform duration-200" :class="{'rotate-180': msg.showProcess}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                                    </svg>
                                </button>
                                <div v-show="msg.showProcess" class="px-4 py-3 border-t border-white/5 bg-black/10">
                                    <ul class="space-y-2">
                                        <li v-for="(step, i) in msg.process" :key="i" class="text-xs text-zinc-400 flex gap-2">
                                            <span class="text-violet-500 font-mono opacity-70">{{ i + 1 }}.</span>
                                            <span>{{ step }}</span>
                                        </li>
                                    </ul>
                                </div>
                            </div>

                            <!-- References -->
                            <div v-if="msg.chunks && msg.chunks.length > 0" class="rounded-lg bg-black/20 overflow-hidden border border-white/5">
                                <button @click="msg.showChunks = !msg.showChunks" 
                                        class="w-full px-4 py-2 flex items-center justify-between text-xs font-medium text-zinc-500 hover:text-zinc-300 hover:bg-white/5 transition-colors">
                                    <span class="flex items-center gap-2">
                                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                        </svg>
                                        参考文档片段 ({{ msg.chunks.length }} 处)
                                    </span>
                                    <svg class="w-4 h-4 transform transition-transform duration-200" :class="{'rotate-180': msg.showChunks}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                                    </svg>
                                </button>
                                <div v-show="msg.showChunks" class="px-4 py-3 border-t border-white/5 bg-black/10 space-y-3">
                                    <div v-for="(chunk, i) in msg.chunks" :key="i" class="text-xs text-zinc-400 bg-white/5 p-2 rounded border border-white/5">
                                        <span class="text-indigo-400 font-bold block mb-1">片段 {{ i + 1 }}</span>
                                        {{ chunk }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading Indicator -->
            <div v-if="loading" class="flex w-full justify-start">
                <div class="bg-zinc-800/40 border border-white/5 rounded-2xl rounded-tl-sm p-4 shadow-xl backdrop-blur-sm flex items-center gap-3">
                     <div class="w-6 h-6 rounded-md bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
                        <svg class="w-3 h-3 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    </div>
                    <span class="text-zinc-400 text-sm animate-pulse">正在思考并检索相关文档...</span>
                </div>
            </div>
         </div>
      </div>

      <!-- Input Area -->
      <div class="mt-6 pt-6 border-t border-white/5 relative z-10">
        <div class="relative group">
           <div class="absolute -inset-0.5 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-xl opacity-30 group-hover:opacity-60 transition duration-300 blur-md" :class="{'opacity-60': loading}"></div>
           <div class="relative flex gap-2 bg-zinc-950 rounded-xl p-1.5 ring-1 ring-white/10">
             <textarea 
               v-model="inputQuestion"
               @keydown.enter.prevent="handleKeydown"
               rows="1"
               :disabled="loading"
               class="flex-1 bg-transparent border-0 focus:ring-0 text-zinc-200 placeholder-zinc-600 resize-none py-3 px-4 leading-relaxed focus:outline-none disabled:opacity-50"
               placeholder="在此输入您的问题..."
             ></textarea>
             <button 
               @click="handleQuery"
               :disabled="loading || !inputQuestion.trim()"
               class="px-8 py-2 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold rounded-lg shadow-lg shadow-violet-900/20 transition-all duration-200 flex items-center gap-2 transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none">
               <span v-if="!loading">提问</span>
               <span v-else>生成中</span>
               <svg v-if="!loading" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
               </svg>
               <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                   <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                   <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
               </svg>
             </button>
           </div>
        </div>
        <p class="text-center text-zinc-600 text-xs mt-3">Enter 发送，Shift + Enter 换行</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { queryQuestion } from '@/api/query'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true,
    breaks: true
})

interface ChatMessage {
    role: 'user' | 'ai'
    content: string
    time?: number
    process?: string[]
    chunks?: string[]
    showProcess?: boolean
    showChunks?: boolean
}

const inputQuestion = ref('')
const loading = ref(false)
const history = ref<ChatMessage[]>([])
const chatContainer = ref<HTMLElement | null>(null)

const scrollToBottom = async () => {
    await nextTick()
    if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
}

const renderMarkdown = (text: string) => {
    return md.render(text)
}

const handleKeydown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        handleQuery()
    }
}

const handleQuery = async () => {
    const question = inputQuestion.value.trim()
    if (!question || loading.value) return

    // Add User Message
    history.value.push({
        role: 'user',
        content: question
    })
    inputQuestion.value = ''
    scrollToBottom()

    loading.value = true

    try {
        const res = await queryQuestion({ question })
        
        // Add AI Message
        history.value.push({
            role: 'ai',
            content: res.answer,
            time: res.time,
            process: res.process,
            chunks: res.chunks,
            showProcess: false,
            showChunks: false
        })

    } catch (error: any) {
        console.error('Query failed:', error)
        // ElMessage.error(error.message || '检索失败，请稍后重试')
        
        // Mock Response for Demo if Backend fails (Optional, can remove in prod)
        history.value.push({
            role: 'ai',
            content: '抱歉，服务器暂时无法连接。这是一个模拟的回答，表明前端 UI 已经准备就绪。\n\n**可能的排查步骤：**\n1. 检查后端服务是否启动\n2. 检查网络连接\n3. 查看控制台错误日志',
            time: 0.5,
            process: ['检查服务状态', '尝试重新连接', '生成错误提示'],
            chunks: ['System Error: Connection Refused', 'Frontend: Network Error'],
            showProcess: true,
            showChunks: false
        })
    } finally {
        loading.value = false
        scrollToBottom()
    }
}

// Watch history changes to scroll
watch(() => history.value.length, () => {
    scrollToBottom()
})
</script>

<style scoped>
/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

/* Typography Overrides for Dark Mode */
:deep(.prose) {
    color: #d4d4d8; /* zinc-300 */
    font-size: 0.95rem;
}
:deep(.prose h1), :deep(.prose h2), :deep(.prose h3), :deep(.prose h4) {
    color: #fff;
    font-weight: 600;
    margin-top: 1.5em;
    margin-bottom: 0.75em;
}
:deep(.prose p) {
    margin-bottom: 1em;
}
:deep(.prose ul), :deep(.prose ol) {
    margin-bottom: 1em;
    padding-left: 1.5em;
}
:deep(.prose li) {
    margin-bottom: 0.25em;
}
:deep(.prose strong) {
    color: #a78bfa; /* violet-400 */
    font-weight: 600;
}
:deep(.prose code) {
    color: #e2e8f0;
    background-color: rgba(255,255,255,0.1);
    padding: 0.2em 0.4em;
    border-radius: 0.25em;
    font-size: 0.85em;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}
:deep(.prose pre) {
    background-color: #18181b; /* zinc-950 */
    padding: 1em;
    border-radius: 0.5em;
    overflow-x: auto;
    border: 1px solid rgba(255,255,255,0.1);
}
:deep(.prose pre code) {
    background-color: transparent;
    padding: 0;
    color: inherit;
    font-size: 0.9em;
}
:deep(.prose blockquote) {
    border-left-color: #7c3aed; /* violet-600 */
    color: #a1a1aa; /* zinc-400 */
    font-style: italic;
    padding-left: 1em;
}
:deep(.prose a) {
    color: #818cf8; /* indigo-400 */
    text-decoration: none;
    border-bottom: 1px dashed #818cf8;
}
:deep(.prose a:hover) {
    color: #a5b4fc; /* indigo-300 */
    border-bottom-style: solid;
}
</style>
