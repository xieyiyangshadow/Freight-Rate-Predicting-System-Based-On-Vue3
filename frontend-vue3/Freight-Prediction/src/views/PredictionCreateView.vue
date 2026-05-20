<template>
  <div class="prediction-create">
    <h1>新建预测任务</h1>

    <div class="card">
      <form @submit.prevent="handleCreate">
        <div v-if="predictionStore.error" class="error-box">{{ predictionStore.error }}</div>
        <div class="form-row">
            <div class="form-group">
            <label>任务名称 <span class="required">*</span></label>
            <input v-model="form.task_name" type="text" placeholder="" required />
          </div>
          <div class="form-group">
            <label>任务描述</label>
            <input v-model="form.task_description" type="text" placeholder="可选" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>关联数据集 <span class="required">*</span></label>
            <select v-model="form.dataset_id" required>
              <option value="" disabled>请选择数据集</option>
              <option v-for="ds in datasetStore.datasets" :key="ds.dataset_id" :value="ds.dataset_id">
                {{ ds.user_provided_name }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>选择模型（可多选）<span class="required">*</span></label>
          <div class="model-checkboxes">
            <label v-for="model in modelStore.completedModels" :key="model.model_id" class="checkbox-item">
              <input 
                type="checkbox" 
                :value="model.model_id" 
                v-model="selectedModelIds"
              />
              <span>{{ model.user_provided_name }}</span>
            </label>
            <p v-if="!modelStore.completedModels?.length" class="hint">暂无可用模型，请先上传并训练完成</p>
          </div>
        </div>

        <div class="form-group">
          <label>输入数据</label>
          <div v-if="selectedDataset">
            <p class="hint">根据所选数据集的特征填写（系统会在提交时自动对齐与训练时的特征）。</p>
            <div v-for="col in featureColumns" :key="col" class="form-row">
              <div class="form-group" style="width:100%">
                <label>{{ col }}</label>
                <input
                  v-model="inputData[col]"
                  :type="isNumericColumn(col) ? 'number' : 'text'"
                />
              </div>
            </div>
          </div>
          <div v-else>
            <p class="hint">请选择数据集后将自动生成输入字段。</p>
          </div>
        </div>

        <div class="actions">
          <button type="submit" :disabled="creating || !canCreate">
            {{ creating ? '创建中...' : '创建预测任务' }}
          </button>
          <button type="button" class="btn-secondary" @click="router.push('/predictions')">
            取消
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { usePredictionStore } from '@/stores/prediction'
import { useDatasetStore } from '@/stores/dataset'
import { useModelStore } from '@/stores/model'

const router = useRouter()
const predictionStore = usePredictionStore()
const datasetStore = useDatasetStore()
const modelStore = useModelStore()

const creating = ref(false)
const selectedModelIds = ref([] as string[])
const inputData = ref<Record<string, any>>({})

const form = ref({
  task_name: '',
  task_description: '',
  dataset_id: '',
})

const selectedDataset = computed(() => datasetStore.datasets.find(d => d.dataset_id === form.value.dataset_id) || null)

const featureColumns = computed(() => {
  if (!selectedDataset.value) return [] as string[]
  return (selectedDataset.value.columns || []).filter(c => c !== selectedDataset.value?.target_column)
})

const isNumericColumn = (col: string) => {
  if (!selectedDataset.value) return false
  // data_types map: true -> numeric? fallback to false
  return !!selectedDataset.value.data_types?.[col]
}

// 当选择数据集变化时，重置 inputData 的字段
watch(() => form.value.dataset_id, (newId: string | undefined) => {
  inputData.value = {}
  const ds = datasetStore.datasets.find(d => d.dataset_id === newId)
  const cols = (ds?.columns || []).filter(c => c !== ds?.target_column)
  cols.forEach(c => { inputData.value[c] = '' })
})


const canCreate = computed(() => {
  const hasAll = form.value.task_name && form.value.dataset_id && selectedModelIds.value.length > 0
  const hasInputs = featureColumns.value.length ? featureColumns.value.every(c => inputData.value[c] !== undefined && inputData.value[c] !== '') : false
  return hasAll && hasInputs
})

const handleCreate = async () => {
  if (!canCreate.value) return

  const payloadInput = { ...inputData.value }

  creating.value = true
  try {
    await predictionStore.createPredictionTask({
      task_name: form.value.task_name,
      task_description: form.value.task_description,
      dataset_id: form.value.dataset_id,
      model_ids: selectedModelIds.value,
      input_data: payloadInput,
    })
    alert('预测任务创建成功，正在执行中...')
    router.push('/predictions')
  } catch (err) {
    // 错误信息会由 store 写入 predictionStore.error 并在界面展示
  } finally {
    creating.value = false
  }
}

datasetStore.fetchDatasets()
modelStore.fetchModels()
</script>

<style scoped>
.prediction-create { max-width: 800px; margin: 0 auto; }
h1 { margin-bottom: 20px; font-size: 24px; }
.card { background: #fff; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { margin-bottom: 16px; }
label { display: block; margin-bottom: 6px; font-size: 14px; color: #555; }
.required { color: #f56c6c; }
input, select, textarea { width: 100%; padding: 8px 12px; border: 1px solid #dcdfe6; border-radius: 4px; font-size: 14px; font-family: inherit; }
input:focus, select:focus, textarea:focus { outline: none; border-color: #409eff; }
.model-checkboxes { display: flex; flex-direction: column; gap: 8px; }
.checkbox-item { display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 14px; }
.checkbox-item input { width: auto; }
.hint { color: #909399; font-size: 12px; margin-top: 4px; }
.actions { display: flex; gap: 12px; margin-top: 24px; }
button { padding: 10px 20px; background: #409eff; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: #909399; }
 .error-box { background: #fff0f0; color: #c80000; border: 1px solid #f5c6cb; padding: 12px; border-radius: 6px; margin-bottom: 12px; }
</style>