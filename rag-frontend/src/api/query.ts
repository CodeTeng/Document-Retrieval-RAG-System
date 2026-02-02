import request from '@/utils/request'

export interface QueryRequest {
  question: string
  doc_id?: string
}

export interface QueryResponse {
  process: string[]      // 检索过程步骤
  chunks: string[]       // 相关文本块
  answer: string         // 最终回答
  time: number           // 耗时(秒)
}

export function queryQuestion(data: QueryRequest) {
  return request<any, QueryResponse>({
    url: '/query',
    method: 'post',
    data
  })
}
