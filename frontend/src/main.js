import { createApp } from 'vue'
import ElementPlus, { ElMessage, ElMessageBox } from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './styles/global.css'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.config.globalProperties.$message = ElMessage
app.config.globalProperties.$confirm = ElMessageBox.confirm
app.mount('#app')
