import { defineStore } from 'pinia'
import type { Document } from '../types/doc'

export const useDocStore = defineStore('doc', {
  state: () => ({
    documents: [] as Document[]
  }),
  actions: {
    addDocument(doc: Document) {
      this.documents.push(doc)
    }
  }
})
