import { defineStore } from 'pinia'
import { ref } from 'vue'
import { streamChat, type ChatStep } from '@/api/chat'

export interface ProcessStep {
  message: string
  status: 'loading' | 'done' | 'error'
  type?: string
  data?: any
}

export interface Message {
  role: 'user' | 'assistant'
  content: string
  loading?: boolean
  process?: ProcessStep[]
  showProcess?: boolean
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const loading = ref(false)

  const sendMessage = async (question: string) => {
    if (!question || loading.value) return

    // Add User Message
    messages.value.push({
      role: 'user',
      content: question
    })
    
    // Add Assistant Placeholder
    const assistantMsg = ref<Message>({
      role: 'assistant',
      content: '',
      loading: true,
      process: [],
      showProcess: true
    })
    messages.value.push(assistantMsg.value)
    loading.value = true

    try {
      await streamChat({ question }, (step: ChatStep) => {
        const currentProcess = assistantMsg.value.process || []
        
        // Update previous step status to done
        if (currentProcess.length > 0 && step.step !== 'answer' && step.step !== 'completed') {
           const lastStep = currentProcess[currentProcess.length - 1]
           if (lastStep.status === 'loading') {
              lastStep.status = 'done'
           }
        }

        switch (step.step) {
          case 'init':
          case 'retrieving':
          case 'generating':
            currentProcess.push({
              message: step.message || 'Processing...',
              status: 'loading',
              type: step.step
            })
            break
            
          case 'retrieved':
            // Update retrieving step to done and add data
            const retrievingStep = currentProcess.find(p => p.type === 'retrieving')
            if (retrievingStep) {
              retrievingStep.status = 'done'
              retrievingStep.message = step.message || '检索完成'
              retrievingStep.data = step.data
            }
            break
            
          case 'answer':
            // Generating step is done once we start getting answers
            const generatingStep = currentProcess.find(p => p.type === 'generating')
            if (generatingStep) {
               generatingStep.status = 'done'
            }
            // Append answer content
            if (step.data) {
               assistantMsg.value.content = step.data 
            }
            // Collapse process when answer starts streaming
            assistantMsg.value.showProcess = false
            break
            
          case 'completed':
            loading.value = false
            assistantMsg.value.loading = false
            break
            
          case 'error':
            currentProcess.push({
              message: step.message || 'Error occurred',
              status: 'error',
              type: 'error'
            })
            loading.value = false
            assistantMsg.value.loading = false
            break
        }
      })
    } catch (e) {
      console.error(e)
      if (loading.value) {
         const currentProcess = assistantMsg.value.process || []
         currentProcess.push({
            message: '网络连接异常，请检查后端服务',
            status: 'error',
            type: 'error'
         })
         loading.value = false
         assistantMsg.value.loading = false
      }
    }
  }

  const clearMessages = () => {
    messages.value = []
    loading.value = false
  }

  return {
    messages,
    loading,
    sendMessage,
    clearMessages
  }
})
