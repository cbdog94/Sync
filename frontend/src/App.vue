<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
const activeIndex = computed(() => router.currentRoute.value.path)

const menuItems = [
  { path: '/sync', label: '同步文字' },
  { path: '/extract', label: '提取文本' },
  { path: '/upload', label: '上传文件' },
  { path: '/download', label: '提取文件' },
]

const handleSelect = (key: string) => {
  router.push(key)
}
</script>

<template>
  <div class="app-container">
    <el-menu
      :default-active="activeIndex"
      mode="horizontal"
      @select="handleSelect"
      :ellipsis="false"
      class="app-menu"
    >
      <el-menu-item
        v-for="item in menuItems"
        :key="item.path"
        :index="item.path"
        class="menu-item"
      >
        {{ item.label }}
      </el-menu-item>
    </el-menu>
    
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', Arial, sans-serif;
}

#app {
  min-height: 100vh;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-menu {
  display: flex;
  justify-content: center;
}

.app-menu .menu-item {
  flex: 1;
  text-align: center;
  justify-content: center;
}

.main-content {
  flex: 1;
  padding: 24px;
  text-align: center;
}

h2 {
  color: #303133;
  margin-bottom: 24px;
  font-weight: 500;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
