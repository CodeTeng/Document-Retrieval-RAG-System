<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-3xl font-bold text-white tracking-tight">文档库管理</h2>
        <p class="mt-2 text-zinc-400 text-lg">上传并管理您的知识库文档，支持 PDF, Word, Markdown, TXT 格式</p>
      </div>
    </div>

    <!-- Upload Card -->
    <div class="relative group">
      <div class="absolute -inset-0.5 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-2xl opacity-20 group-hover:opacity-40 transition duration-500 blur"></div>
      <div class="relative bg-zinc-900/80 border border-white/10 rounded-xl p-8 transition-all duration-300 backdrop-blur-md">
        <DocUpload />
      </div>
    </div>

    <!-- List -->
    <div class="bg-zinc-900/50 border border-white/5 rounded-xl overflow-hidden backdrop-blur-sm shadow-xl">
      <div class="px-6 py-4 border-b border-white/5 bg-white/5 flex items-center justify-between">
        <h3 class="text-lg font-medium text-white flex items-center gap-2">
          <span class="w-1.5 h-4 bg-violet-500 rounded-full"></span>
          已上传文档
        </h3>
        <span class="text-xs px-2 py-1 bg-zinc-800 rounded border border-white/5 text-zinc-400">Total: {{ docList.length }}</span>
      </div>
      
      <!-- Empty State -->
      <div v-if="docList.length === 0" class="p-12 text-center text-zinc-500 flex flex-col items-center justify-center min-h-[200px]">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-zinc-800/50 mb-6 ring-1 ring-white/5">
           <svg class="w-10 h-10 text-zinc-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
           </svg>
        </div>
        <p class="text-lg font-medium text-zinc-400">暂无上传文档</p>
        <p class="text-sm mt-1">请上传文档以开始构建知识库</p>
      </div>

      <!-- Data List -->
      <div v-else class="divide-y divide-white/5">
        <div v-for="doc in docList" :key="doc.id" class="p-4 flex items-center justify-between hover:bg-white/5 transition-colors duration-200">
          <div class="flex items-center gap-4">
            <!-- Icon based on file type -->
            <div class="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-xs shadow-inner"
                 :class="getFileIconClass(doc.name)">
               {{ getFileExtension(doc.name) }}
            </div>
            <div>
              <h4 class="text-white font-medium truncate max-w-[300px]" :title="doc.name">{{ doc.name }}</h4>
              <div class="flex items-center gap-3 text-xs text-zinc-500 mt-1">
                <span>{{ doc.upload_time }}</span>
                <span v-if="doc.size">{{ formatFileSize(doc.size) }}</span>
                <span class="px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-white/5">{{ doc.status }}</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2">
             <button class="p-2 text-zinc-400 hover:text-white hover:bg-white/10 rounded-lg transition-all" title="查看详情">
               <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
               </svg>
             </button>
             <button class="p-2 text-zinc-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all" title="删除">
               <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
               </svg>
             </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DocUpload from '@/components/DocUpload.vue'
import { getDocList, type DocItem } from '@/api/doc'
import { ElMessage } from 'element-plus'

const docList = ref<DocItem[]>([])

const fetchDocList = async () => {
  try {
    const res = await getDocList()
    // 兼容后端可能返回的结构，如果直接返回数组则使用，否则检查 data 字段
    if (Array.isArray(res)) {
      docList.value = res
    } else if (res && Array.isArray((res as any).data)) {
      docList.value = (res as any).data
    } else {
       // Mock data for preview if backend is not ready
       // Remove this when backend is ready
       docList.value = [
         { id: '1', name: 'RAG技术架构方案.pdf', upload_time: '2025-02-24 10:30', status: '已索引', size: 1024 * 1024 * 2.5 },
         { id: '2', name: '产品需求文档_v1.0.docx', upload_time: '2025-02-23 15:45', status: '解析中', size: 1024 * 512 },
         { id: '3', name: '运维手册.md', upload_time: '2025-02-22 09:20', status: '已索引', size: 1024 * 15 }
       ]
    }
  } catch (error) {
    console.error('Failed to fetch doc list:', error)
    // ElMessage.error('获取文档列表失败')
    
    // Fallback to mock data for demo purposes since backend might not be ready
    docList.value = [
       { id: '1', name: 'RAG技术架构方案.pdf', upload_time: '2025-02-24 10:30', status: '已索引', size: 1024 * 1024 * 2.5 },
       { id: '2', name: '产品需求文档_v1.0.docx', upload_time: '2025-02-23 15:45', status: '解析中', size: 1024 * 512 },
       { id: '3', name: '运维手册.md', upload_time: '2025-02-22 09:20', status: '已索引', size: 1024 * 15 }
    ]
  }
}

const getFileExtension = (filename: string) => {
  return filename.split('.').pop()?.toUpperCase() || 'FILE'
}

const getFileIconClass = (filename: string) => {
  const ext = filename.split('.').pop()?.toLowerCase()
  switch (ext) {
    case 'pdf': return 'bg-red-500/20 text-red-500 border border-red-500/20'
    case 'doc':
    case 'docx': return 'bg-blue-500/20 text-blue-500 border border-blue-500/20'
    case 'md':
    case 'markdown': return 'bg-white/10 text-white border border-white/20'
    case 'txt': return 'bg-zinc-700/50 text-zinc-400 border border-zinc-600/30'
    default: return 'bg-violet-500/20 text-violet-500 border border-violet-500/20'
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

onMounted(() => {
  fetchDocList()
})
</script>
