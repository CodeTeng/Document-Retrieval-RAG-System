<template>
  <div class="bg-white shadow sm:rounded-lg p-6">
    <h2 class="text-lg font-medium leading-6 text-gray-900 mb-4">Q&A Retrieval</h2>
    
    <div class="mb-6">
      <label for="question" class="block text-sm font-medium text-gray-700">Your Question</label>
      <div class="mt-1">
        <textarea id="question" rows="3" class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md" placeholder="Enter your question here..."></textarea>
      </div>
      <div class="mt-2">
        <button type="button" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          Ask
        </button>
      </div>
    </div>

    <div class="border-t border-gray-200 pt-6">
      <h3 class="text-md font-medium text-gray-900 mb-2">Answer</h3>
      <div class="bg-gray-50 rounded-md p-4 text-sm text-gray-500">
        Answer will appear here...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Logic for query and results will go here
</script>
