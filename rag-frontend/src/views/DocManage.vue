<template>
  <div class="bg-white shadow sm:rounded-lg p-6">
    <h2 class="text-lg font-medium leading-6 text-gray-900 mb-4">Document Management</h2>
    <div class="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
      <span class="mt-2 block text-sm font-medium text-gray-900">
        Drag and drop files here or click to upload
      </span>
      <p class="mt-1 text-xs text-gray-500">PDF, Word, Markdown, TXT up to 10MB</p>
    </div>
    
    <div class="mt-8">
      <h3 class="text-md font-medium text-gray-900 mb-2">Uploaded Documents</h3>
      <p class="text-sm text-gray-500">No documents uploaded yet.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// Logic for file upload and listing will go here
</script>
